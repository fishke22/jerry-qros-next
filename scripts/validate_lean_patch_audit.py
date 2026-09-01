from __future__ import annotations

import argparse
import json
from pathlib import Path

BANNED = {
    "DotNetZip": None,
    "NetMQ": None,
    "System.Drawing.Common": "4.7.0",
    "System.Net.Http.WinHttpHandler": "4.4.0",
    "System.Private.ServiceModel": "4.4.0",
    "System.ServiceModel.Primitives": "4.4.0",
}


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def package_pairs(doc: dict) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for node in walk(doc):
        name = node.get("id") or node.get("name") or node.get("packageId")
        version = node.get("resolvedVersion") or node.get("resolved") or node.get("version")
        if isinstance(name, str) and isinstance(version, str):
            pairs.add((name, version))
    return pairs


def high_or_critical(doc: dict) -> list[dict]:
    hits = []
    for node in walk(doc):
        severity = node.get("severity")
        if isinstance(severity, str) and severity.lower() in {"high", "critical"}:
            hits.append(node)
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", required=True, type=Path)
    parser.add_argument("--vulnerable", required=True, type=Path)
    args = parser.parse_args()

    all_doc = json.loads(args.all.read_text(encoding="utf-8"))
    vuln_doc = json.loads(args.vulnerable.read_text(encoding="utf-8"))
    pairs = package_pairs(all_doc)

    violations = []
    for package, version in sorted(BANNED.items()):
        for observed_name, observed_version in sorted(pairs):
            if observed_name.lower() == package.lower() and (version is None or observed_version == version):
                violations.append(f"banned package present: {observed_name} {observed_version}")

    severe = high_or_critical(vuln_doc)
    if severe:
        violations.append(f"NuGet audit reported {len(severe)} HIGH/CRITICAL vulnerability record(s)")

    if violations:
        for violation in violations:
            print(f"DENY: {violation}")
        return 2

    if not any(name.lower() == "prodotnetzip" and version == "1.20.0" for name, version in pairs):
        print("DENY: expected ProDotNetZip 1.20.0 not present in resolved graph")
        return 2

    print("QROS patched LEAN dependency gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
