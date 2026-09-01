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


def _nonempty_problem_fields(doc: dict) -> list[str]:
    problems = []
    for node in walk(doc):
        for key in ("problem", "problems", "error", "errors"):
            if key in node and node[key] not in (None, "", [], {}, False):
                problems.append(key)
    return problems


def audit_coverage(
    doc: dict, label: str, *, require_frameworks: bool
) -> tuple[set[str], set[tuple[str, str]]]:
    if not isinstance(doc, dict):
        raise ValueError(f"{label} audit root must be an object")
    if doc.get("version") not in (1, "1"):
        raise ValueError(f"{label} audit output version is missing or unsupported")
    problems = _nonempty_problem_fields(doc)
    if problems:
        raise ValueError(
            f"{label} audit reports problem/error fields: {sorted(set(problems))}"
        )

    projects = doc.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError(f"{label} audit project coverage missing")

    project_paths: set[str] = set()
    coverage: set[tuple[str, str]] = set()
    for project in projects:
        if not isinstance(project, dict) or not isinstance(project.get("path"), str):
            raise ValueError(f"{label} audit project path missing")
        path = project["path"]
        if path in project_paths:
            raise ValueError(f"{label} audit duplicate project: {path}")
        project_paths.add(path)

        frameworks = project.get("frameworks", [])
        if not isinstance(frameworks, list):
            raise ValueError(f"{label} audit frameworks must be a list for {path}")
        if require_frameworks and not frameworks:
            raise ValueError(f"{label} audit framework coverage missing for {path}")
        for framework in frameworks:
            if not isinstance(framework, dict) or not isinstance(
                framework.get("framework"), str
            ):
                raise ValueError(f"{label} audit framework identity missing")
            for package_key in ("topLevelPackages", "transitivePackages"):
                if package_key not in framework or not isinstance(
                    framework[package_key], list
                ):
                    raise ValueError(
                        f"{label} audit package evidence missing or invalid: "
                        f"{path} / {framework['framework']} / {package_key}"
                    )
            key = (path, framework["framework"])
            if key in coverage:
                raise ValueError(
                    f"{label} audit duplicate project/framework coverage: {key}"
                )
            coverage.add(key)
    return project_paths, coverage


def validate_audit_documents(
    all_doc: dict, vuln_doc: dict
) -> tuple[set[tuple[str, str]], list[dict]]:
    all_projects, all_coverage = audit_coverage(
        all_doc, "all-packages", require_frameworks=True
    )
    vulnerable_projects, vulnerable_coverage = audit_coverage(
        vuln_doc, "vulnerable", require_frameworks=False
    )
    if all_projects != vulnerable_projects:
        raise ValueError(
            "NuGet audit project coverage mismatch between all-packages and vulnerable outputs"
        )
    if not vulnerable_coverage.issubset(all_coverage):
        raise ValueError(
            "NuGet vulnerable audit reports unknown project/framework coverage"
        )
    pairs = package_pairs(all_doc)
    if not pairs:
        raise ValueError("NuGet all-packages audit contains no resolved package evidence")
    return pairs, high_or_critical(vuln_doc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", required=True, type=Path)
    parser.add_argument("--vulnerable", required=True, type=Path)
    args = parser.parse_args()
    try:
        all_doc = json.loads(args.all.read_text(encoding="utf-8"))
        vuln_doc = json.loads(args.vulnerable.read_text(encoding="utf-8"))
        pairs, severe = validate_audit_documents(all_doc, vuln_doc)
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"DENY: incomplete or invalid NuGet vulnerability evidence: {exc}")
        return 2

    violations = []
    for package, version in sorted(BANNED.items()):
        for observed_name, observed_version in sorted(pairs):
            if observed_name.lower() == package.lower() and (
                version is None or observed_version == version
            ):
                violations.append(f"banned package present: {observed_name} {observed_version}")
    if severe:
        violations.append(f"NuGet audit reported {len(severe)} HIGH/CRITICAL vulnerability record(s)")
    if not any(
        name.lower() == "prodotnetzip" and version == "1.20.0"
        for name, version in pairs
    ):
        violations.append("expected ProDotNetZip 1.20.0 not present in resolved graph")

    if violations:
        for violation in violations:
            print(f"DENY: {violation}")
        return 2

    print("QROS patched LEAN dependency gate: PASS / AUDIT COVERAGE VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
