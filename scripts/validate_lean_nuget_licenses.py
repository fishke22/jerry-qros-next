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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument(
        "--packages-root",
        type=Path,
        default=Path.home() / ".nuget" / "packages",
    )
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--print-canonical", action="store_true")
    parser.add_argument("--allow-unreviewed", action="store_true")
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

    review_required = [
        item["identity"] for item in packages if item["requires_manual_review"]
    ]
    missing = [
        item["identity"]
        for item in packages
        if item["license_kind"] in {"MISSING", "UNSUPPORTED"}
    ]
    print(
        "QROS patched Launcher NuGet license metadata: "
        f"packages={len(packages)} manual_review={len(review_required)} missing={len(missing)}"
    )

    if args.expected is not None:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        if observed != expected:
            print("DENY: patched Launcher NuGet license metadata differs from canonical evidence")
            return 2
        print("QROS patched Launcher NuGet license metadata snapshot: PASS")

    if missing:
        for identity in missing:
            print(f"DENY: missing/unsupported NuGet license metadata: {identity}")
        return 2

    if review_required and not args.allow_unreviewed:
        for identity in review_required:
            print(f"DENY: NuGet license requires manual review: {identity}")
        return 2

    if review_required:
        print("QROS patched Launcher NuGet license gate: REVIEW_REQUIRED")
    else:
        print("QROS patched Launcher NuGet license gate: METADATA_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
