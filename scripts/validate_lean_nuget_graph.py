from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonicalize_assets(doc: dict) -> dict:
    require(isinstance(doc, dict), "NuGet assets root must be an object")
    targets = doc.get("targets")
    libraries = doc.get("libraries")
    require(isinstance(targets, dict) and targets, "NuGet assets targets missing")
    require(isinstance(libraries, dict), "NuGet assets libraries missing")

    canonical_targets = []
    package_count = 0
    project_count = 0

    for target_name, target_nodes in sorted(targets.items()):
        require(isinstance(target_nodes, dict), f"invalid target node: {target_name}")
        nodes = []
        for identity, node in sorted(target_nodes.items()):
            require(isinstance(node, dict), f"invalid assets node: {identity}")
            node_type = node.get("type")
            require(isinstance(node_type, str), f"node type missing: {identity}")

            dependencies = node.get("dependencies", {})
            require(
                isinstance(dependencies, dict),
                f"dependencies must be an object: {identity}",
            )
            item = {
                "identity": identity,
                "type": node_type,
                "dependencies": {
                    name: dependencies[name] for name in sorted(dependencies)
                },
            }

            if node_type == "package":
                package_count += 1
                library = libraries.get(identity)
                require(
                    isinstance(library, dict),
                    f"package library metadata missing: {identity}",
                )
                sha512 = library.get("sha512")
                require(
                    isinstance(sha512, str) and sha512,
                    f"package integrity hash missing: {identity}",
                )
                item["sha512"] = sha512
            elif node_type == "project":
                project_count += 1

            nodes.append(item)

        canonical_targets.append({"target": target_name, "nodes": nodes})

    require(package_count > 0, "NuGet assets contain no package nodes")
    return {
        "schema_version": 1,
        "assets_version": doc.get("version"),
        "package_count": package_count,
        "project_count": project_count,
        "targets": canonical_targets,
    }


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--print-canonical", action="store_true")
    args = parser.parse_args()

    observed = canonicalize_assets(
        json.loads(args.assets.read_text(encoding="utf-8"))
    )
    digest = "sha256:" + hashlib.sha256(canonical_bytes(observed)).hexdigest()

    if args.print_canonical:
        print(
            "QROS_LEAN_NUGET_GRAPH="
            + json.dumps(observed, sort_keys=True, separators=(",", ":"))
        )
    print(f"QROS patched Launcher NuGet graph hash: {digest}")
    print(
        "QROS patched Launcher NuGet graph nodes: "
        f"packages={observed['package_count']} projects={observed['project_count']}"
    )

    if args.expected is not None:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        if observed != expected:
            print("DENY: patched Launcher NuGet graph differs from canonical evidence")
            return 2
        print("QROS patched Launcher NuGet graph snapshot: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
