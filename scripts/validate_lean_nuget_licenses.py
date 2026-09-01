from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def package_identities(assets: dict) -> list[str]:
    targets = assets.get("targets")
    require(isinstance(targets, dict) and targets, "NuGet assets targets missing")
    identities: set[str] = set()
    for target_nodes in targets.values():
        require(isinstance(target_nodes, dict), "invalid NuGet target node")
        for identity, node in target_nodes.items():
            if isinstance(node, dict) and node.get("type") == "package":
                identities.add(identity)
    require(identities, "NuGet assets contain no package nodes")
    return sorted(identities, key=str.lower)


def child(parent: ET.Element, local_name: str) -> ET.Element | None:
    return parent.find("{*}" + local_name)


def child_text(parent: ET.Element, local_name: str) -> str | None:
    node = child(parent, local_name)
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_package(packages_root: Path, identity: str) -> dict:
    package_id, version = identity.rsplit("/", 1)
    package_dir = packages_root / package_id.lower() / version.lower()
    require(package_dir.is_dir(), f"NuGet package directory missing: {identity}")
    nuspecs = sorted(package_dir.glob("*.nuspec"))
    require(len(nuspecs) == 1, f"expected one nuspec for {identity}, got {len(nuspecs)}")

    root = ET.parse(nuspecs[0]).getroot()
    metadata = child(root, "metadata")
    require(metadata is not None, f"nuspec metadata missing: {identity}")

    declared_id = child_text(metadata, "id")
    declared_version = child_text(metadata, "version")
    require(
        declared_id is not None and declared_id.lower() == package_id.lower(),
        f"nuspec id mismatch: {identity}",
    )
    require(declared_version == version, f"nuspec version mismatch: {identity}")

    license_node = child(metadata, "license")
    license_url = child_text(metadata, "licenseUrl")
    evidence: dict[str, object] = {
        "identity": identity,
        "nuspec_sha256": file_sha256(nuspecs[0]),
        "project_url": child_text(metadata, "projectUrl"),
        "repository_url": None,
        "license_kind": "MISSING",
        "license_value": None,
        "license_file_sha256": None,
        "requires_manual_review": True,
    }

    repository_node = child(metadata, "repository")
    if repository_node is not None:
        evidence["repository_url"] = repository_node.attrib.get("url")

    if license_node is not None and license_node.text:
        value = license_node.text.strip()
        kind = (license_node.attrib.get("type") or "").strip().lower()
        if kind == "expression":
            evidence["license_kind"] = "EXPRESSION"
            evidence["license_value"] = value
            evidence["requires_manual_review"] = False
        elif kind == "file":
            evidence["license_kind"] = "FILE"
            evidence["license_value"] = value
            license_file = package_dir / value
            require(license_file.is_file(), f"license file missing: {identity}: {value}")
            evidence["license_file_sha256"] = file_sha256(license_file)
        else:
            evidence["license_kind"] = "UNSUPPORTED"
            evidence["license_value"] = value
    elif license_url:
        evidence["license_kind"] = "URL"
        evidence["license_value"] = license_url

    return evidence


def validate_manual_dispositions(observed: dict, disposition_doc: dict) -> None:
    require(disposition_doc.get("unknown_is_deny") is True, "manual license dispositions must be fail-closed")
    require(disposition_doc.get("package_release_authorized") is False, "package/release gate must remain closed")
    rows = disposition_doc.get("dispositions")
    require(isinstance(rows, list), "manual license dispositions missing")
    by_id = {row.get("identity"): row for row in rows if isinstance(row, dict)}
    require(len(by_id) == len(rows), "duplicate or invalid manual license disposition")

    manual = {
        item["identity"]: item
        for item in observed["packages"]
        if item["requires_manual_review"]
    }
    require(
        set(by_id) == set(manual),
        "manual license disposition coverage mismatch: "
        f"expected={sorted(manual)} actual={sorted(by_id)}",
    )

    for identity, row in by_id.items():
        require(row.get("review_status") == "ACCEPTED", f"license review not accepted: {identity}")
        expression = row.get("spdx_expression")
        require(
            isinstance(expression, str)
            and expression
            and "UNKNOWN" not in expression.upper()
            and "NOASSERTION" not in expression.upper(),
            f"unresolved SPDX license disposition: {identity}",
        )
        evidence = row.get("evidence")
        require(isinstance(evidence, list) and evidence, f"license evidence missing: {identity}")
        obligations = row.get("distribution_obligations")
        require(
            isinstance(obligations, list) and obligations,
            f"distribution obligations missing: {identity}",
        )
        exact_hash = row.get("exact_package_license_file_sha256")
        package_hash = manual[identity].get("license_file_sha256")
        if exact_hash is not None:
            require(exact_hash == package_hash, f"embedded package license hash mismatch: {identity}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument(
        "--packages-root",
        type=Path,
        default=Path.home() / ".nuget" / "packages",
    )
    parser.add_argument("--expected-metadata", required=True, type=Path)
    parser.add_argument("--manual-dispositions", required=True, type=Path)
    parser.add_argument("--print-canonical", action="store_true")
    args = parser.parse_args()

    assets = json.loads(args.assets.read_text(encoding="utf-8"))
    packages = [
        inspect_package(args.packages_root, identity)
        for identity in package_identities(assets)
    ]
    observed = {
        "schema_version": 1,
        "package_count": len(packages),
        "packages": packages,
    }

    if args.print_canonical:
        print(
            "QROS_LEAN_NUGET_LICENSES="
            + json.dumps(observed, sort_keys=True, separators=(",", ":"))
        )

    expected = json.loads(args.expected_metadata.read_text(encoding="utf-8"))
    require(
        observed == expected,
        "patched Launcher NuGet license metadata differs from canonical evidence",
    )
    print("QROS patched Launcher NuGet license metadata snapshot: PASS")

    for item in observed["packages"]:
        if not item["requires_manual_review"]:
            require(item["license_kind"] == "EXPRESSION", f"unexpected auto license kind: {item['identity']}")
            value = item["license_value"]
            require(
                isinstance(value, str)
                and value
                and "UNKNOWN" not in value.upper()
                and "NOASSERTION" not in value.upper(),
                f"unresolved NuGet SPDX expression: {item['identity']}",
            )

    dispositions = json.loads(args.manual_dispositions.read_text(encoding="utf-8"))
    validate_manual_dispositions(observed, dispositions)
    manual_count = sum(1 for x in observed["packages"] if x["requires_manual_review"])
    expression_count = len(observed["packages"]) - manual_count
    print(
        "QROS patched Launcher NuGet license gate: PASS "
        f"packages={len(observed['packages'])} "
        f"spdx_metadata={expression_count} manual_reviewed={manual_count}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print("QROS patched Launcher NuGet license gate: DENY:", exc)
        raise SystemExit(2)
