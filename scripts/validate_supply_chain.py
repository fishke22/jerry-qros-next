from __future__ import annotations
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA256=re.compile(r"^[0-9a-f]{64}$")
EXACT_VERSION=re.compile(r"^[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9._-]*)$")

def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def fail(msg): raise AssertionError(msg)

def validate_dependency_registry():
    r=load("config/dependency-registry.json")
    if r.get("registry_version")!=1 or r.get("unknown_is_deny") is not True: fail("dependency registry must remain v1 fail-closed")
    ids=set()
    for d in r.get("dependencies",[]):
        if d["dependency_id"] in ids: fail("duplicate dependency id: "+d["dependency_id"])
        ids.add(d["dependency_id"])
        if d["status"]=="ADOPTED":
            pin=d.get("pin_type")
            if pin=="GIT_COMMIT_SHA40":
                if not SHA40.fullmatch(d.get("revision") or ""): fail("adopted git dependency is not SHA40 pinned: "+d["dependency_id"])
            elif pin=="PYPI_EXACT_VERSION":
                if not EXACT_VERSION.fullmatch(d.get("version_label") or ""): fail("adopted PyPI dependency lacks exact version: "+d["dependency_id"])
                hashes=d.get("artifact_sha256") or {}
                if not hashes or any(not SHA256.fullmatch(v) for v in hashes.values()): fail("adopted PyPI dependency lacks artifact hashes: "+d["dependency_id"])
                if d.get("lock_required") is not True: fail("adopted PyPI dependency must be lock-required: "+d["dependency_id"])
            else: fail("unsupported adopted pin type: "+d["dependency_id"])
            if str(d["license_spdx"]).startswith("UNKNOWN") or not d["license_verified_at"]: fail("adopted dependency license is not verified: "+d["dependency_id"])
            if not d["cost_class"].startswith(("FREE_","OSS_")): fail("adopted dependency cost not proven zero: "+d["dependency_id"])
        if d["status"].startswith("PLANNED_") and d["introduction_authorized"] is not False: fail("planned dependency accidentally authorized: "+d["dependency_id"])

def validate_lockfile():
    lock=(ROOT/"requirements"/"phase2.lock").read_text(encoding="utf-8")
    runtime=[d for d in load("config/dependency-registry.json")["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
    for d in runtime:
        package=d["package_name"]
        if f"{package}==" not in lock and not (package=="pandera" and "pandera[pyarrow]==" in lock): fail("runtime dependency absent from phase2 lock: "+package)
        for digest in d["artifact_sha256"].values():
            if f"sha256:{digest}" not in lock: fail("runtime dependency hash absent from phase2 lock: "+package)

def validate_sbom():
    b=load("supply-chain/bom.cdx.json")
    if b.get("bomFormat")!="CycloneDX" or b.get("specVersion")!="1.7": fail("SBOM must use CycloneDX 1.7")
    runtime=[d for d in load("config/dependency-registry.json")["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
    if len(b.get("components",[]))!=len(runtime): fail("SBOM runtime component count does not match adopted runtime dependencies")
    purls={c.get("purl") for c in b.get("components",[])}
    for d in runtime:
        expected=f"pkg:pypi/{d['package_name']}@{d['version_label']}"
        if expected not in purls: fail("runtime dependency missing from SBOM: "+expected)
    props={p["name"]:p["value"] for p in b["metadata"]["component"].get("properties",[])}
    for k in ("qros:package-authorized","qros:release-authorized","qros:yuanta-integration-authorized","qros:live-trading-authorized"):
        if props.get(k)!="false": fail("hard gate not represented closed in SBOM: "+k)

def validate_license_manifest():
    m=load("supply-chain/dependency-license-manifest.json")
    if m.get("policy")!="UNKNOWN_LICENSE_DENIES_INTRODUCTION": fail("license manifest policy drift")
    runtime=m.get("runtime_dependencies",[])
    if not runtime: fail("Phase 2 runtime license manifest must not be empty")
    if any(d["license_spdx"] in ("UNKNOWN","NOASSERTION") for d in runtime): fail("runtime dependency has unknown license")
    toolchains=m.get("toolchain_dependencies",[])
    if not toolchains or toolchains[0].get("version")!="3.14.7": fail("Python 3.14.7 toolchain evidence missing")

def validate_source_and_provenance():
    s=load("supply-chain/source-revisions.json")
    if s["qros_source_revision"]["strategy"]!="GIT_COMMIT_AT_BUILD": fail("QROS source revision must be captured at build")
    if s.get("python_runtime",{}).get("version")!="3.14.7": fail("Python runtime pin missing")
    p=load("supply-chain/provenance-manifest.json")
    if p.get("unknown_is_deny") is not True or not SHA256.fullmatch(p["authority"]["sha256"]): fail("provenance authority hash invalid")
    e=load("supply-chain/build-environment.json")
    if e.get("paid_compute_allowed") is not False or e.get("product_build_exists") is not False: fail("product packaging/build gate drift")
    if e.get("data_runtime_exists") is not True: fail("Phase 2 data runtime evidence missing")

def main():
    for fn in (validate_dependency_registry,validate_lockfile,validate_sbom,validate_license_manifest,validate_source_and_provenance):
        fn();print("PASS",fn.__name__)
    print("QROS Phase 2 supply-chain gate: PASS");return 0

if __name__=="__main__":
    try: raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 2 supply-chain gate: FAIL:",exc,file=sys.stderr);raise SystemExit(1)
