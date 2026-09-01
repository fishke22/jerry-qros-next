from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT_REF = "pkg:github/QuantConnect/Lean@b692bf4788e8b54fc23bdcb5659666bf055ce89f#Launcher"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def package_purl(identity: str) -> str:
    package_id, version = identity.rsplit("/", 1)
    return f"pkg:nuget/{package_id}@{version}"


def build_expected(graph: dict, metadata: dict, dispositions: dict) -> dict:
    meta_by_id = {x["identity"]: x for x in metadata["packages"]}
    manual_by_id = {x["identity"]: x for x in dispositions["dispositions"]}
    package_nodes = [
        node
        for target in graph["targets"]
        for node in target["nodes"]
        if node["type"] == "package"
    ]
    exact_by_name = {
        node["identity"].rsplit("/", 1)[0].lower(): node["identity"]
        for node in package_nodes
    }

    components = []
    dependencies = []
    for node in package_nodes:
        identity = node["identity"]
        package_id, version = identity.rsplit("/", 1)
        meta = meta_by_id[identity]
        manual = manual_by_id.get(identity)
        expression = manual["spdx_expression"] if manual else meta["license_value"]
        require(isinstance(expression, str) and expression, f"missing resolved license: {identity}")
        components.append(
            {
                "type": "library",
                "bom-ref": package_purl(identity),
                "name": package_id,
                "version": version,
                "purl": package_purl(identity),
                "licenses": [{"expression": expression}],
                "properties": [
                    {
                        "name": "qros:nuget-content-hash-sha512-base64",
                        "value": node["sha512"],
                    },
                    {
                        "name": "qros:nuspec-sha256",
                        "value": meta["nuspec_sha256"],
                    },
                    {
                        "name": "qros:license-review-mode",
                        "value": (
                            "MANUAL_REVIEWED"
                            if manual
                            else "NUGET_SPDX_EXPRESSION"
                        ),
                    },
                ],
            }
        )
        resolved = []
        for dependency_name in sorted(node.get("dependencies", {})):
            exact = exact_by_name.get(dependency_name.lower())
            require(exact is not None, f"unresolved NuGet edge: {identity} -> {dependency_name}")
            resolved.append(package_purl(exact))
        dependencies.append({"ref": package_purl(identity), "dependsOn": sorted(resolved)})

    components.sort(key=lambda x: x["bom-ref"])
    dependencies.sort(key=lambda x: x["ref"])
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": ROOT_REF,
                "name": "QuantConnect LEAN Launcher — QROS Phase 3D patched checkout-time runtime",
                "version": "b692bf4788e8b54fc23bdcb5659666bf055ce89f+qros-phase3d",
                "properties": [
                    {
                        "name": "qros:base-lean-gitlink",
                        "value": "b692bf4788e8b54fc23bdcb5659666bf055ce89f",
                    },
                    {
                        "name": "qros:runtime-scope",
                        "value": "LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY",
                    },
                    {
                        "name": "qros:patch-mode",
                        "value": "DETERMINISTIC_CHECKOUT_TIME_NO_FORK_NO_GITLINK_CHANGE",
                    },
                    {
                        "name": "qros:canonical-graph-sha256",
                        "value": "sha256:165ba17fec034b417f4ae91b86544cbe9b2002f1c561f4908b0d43a76875f235",
                    },
                    {"name": "qros:package-authorized", "value": "false"},
                    {"name": "qros:release-authorized", "value": "false"},
                ],
            }
        },
        "components": components,
        "dependencies": [
            {"ref": ROOT_REF, "dependsOn": sorted(x["bom-ref"] for x in components)},
            *dependencies,
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--manual-dispositions", required=True, type=Path)
    parser.add_argument("--expected", required=True, type=Path)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    dispositions = json.loads(args.manual_dispositions.read_text(encoding="utf-8"))
    observed = json.loads(args.expected.read_text(encoding="utf-8"))
    expected = build_expected(graph, metadata, dispositions)
    require(observed == expected, "patched Launcher CycloneDX SBOM differs from canonical graph/license evidence")
    require(len(observed["components"]) == graph["package_count"] == 55, "patched Launcher SBOM package count drift")
    require(
        any(x["purl"] == "pkg:nuget/ProDotNetZip@1.20.0" for x in observed["components"]),
        "ProDotNetZip 1.20.0 missing from patched Launcher SBOM",
    )
    require(
        not any(x["name"].lower() in {"dotnetzip", "netmq"} for x in observed["components"]),
        "banned package present in patched Launcher SBOM",
    )
    print("QROS patched Launcher CycloneDX SBOM gate: PASS packages=55")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print("QROS patched Launcher CycloneDX SBOM gate: DENY:", exc)
        raise SystemExit(2)
