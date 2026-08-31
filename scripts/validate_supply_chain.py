from __future__ import annotations
import json,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA256=re.compile(r"^[0-9a-f]{64}$")

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def fail(msg):
    raise AssertionError(msg)

def validate_dependency_registry():
    r=load("config/dependency-registry.json")
    if r.get("registry_version")!=1 or r.get("unknown_is_deny") is not True:
        fail("dependency registry must remain v1 fail-closed")
    ids=set()
    for d in r.get("dependencies",[]):
        if d["dependency_id"] in ids: fail("duplicate dependency id: "+d["dependency_id"])
        ids.add(d["dependency_id"])
        if d["status"]=="ADOPTED":
            if d["version_label"]=="UNSPECIFIED" or not SHA40.fullmatch(d["revision"] or ""):
                fail("adopted dependency is not exactly pinned: "+d["dependency_id"])
            if d["license_spdx"].startswith("UNKNOWN") or not d["license_verified_at"]:
                fail("adopted dependency license is not verified: "+d["dependency_id"])
            if not d["cost_class"].startswith(("FREE_","OSS_")):
                fail("adopted dependency cost not proven zero: "+d["dependency_id"])
        if d["status"].startswith("PLANNED_") and d["introduction_authorized"] is not False:
            fail("planned dependency accidentally authorized: "+d["dependency_id"])

def validate_sbom():
    b=load("supply-chain/bom.cdx.json")
    if b.get("bomFormat")!="CycloneDX" or b.get("specVersion")!="1.7":
        fail("SBOM must use CycloneDX 1.7")
    runtime=[d for d in load("config/dependency-registry.json")["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
    if len(b.get("components",[]))!=len(runtime):
        fail("SBOM runtime component count does not match adopted runtime dependencies")
    props={p["name"]:p["value"] for p in b["metadata"]["component"].get("properties",[])}
    for k in ("qros:package-authorized","qros:release-authorized","qros:yuanta-integration-authorized","qros:live-trading-authorized"):
        if props.get(k)!="false": fail("hard gate not represented closed in SBOM: "+k)

def validate_license_manifest():
    m=load("supply-chain/dependency-license-manifest.json")
    if m.get("policy")!="UNKNOWN_LICENSE_DENIES_INTRODUCTION":
        fail("license manifest policy drift")
    if m.get("runtime_dependencies")!=[]:
        fail("Phase 1B must not introduce runtime dependencies")
    for d in m.get("adopted_dependencies",[]):
        if d["license_spdx"] in ("UNKNOWN","NOASSERTION") or not SHA40.fullmatch(d["revision"]):
            fail("adopted dependency license/revision invalid")

def validate_source_and_provenance():
    s=load("supply-chain/source-revisions.json")
    if s["qros_source_revision"]["strategy"]!="GIT_COMMIT_AT_BUILD":
        fail("QROS source revision must be captured at build")
    p=load("supply-chain/provenance-manifest.json")
    if p.get("unknown_is_deny") is not True or not SHA256.fullmatch(p["authority"]["sha256"]):
        fail("provenance authority hash invalid")
    e=load("supply-chain/build-environment.json")
    if e.get("paid_compute_allowed") is not False or e.get("product_build_exists") is not False:
        fail("Phase 1B build environment drift")

def main():
    for fn in (validate_dependency_registry,validate_sbom,validate_license_manifest,validate_source_and_provenance):
        fn();print("PASS",fn.__name__)
    print("QROS Phase 1B supply-chain gate: PASS")
    return 0

if __name__=="__main__":
    try:raise SystemExit(main())
    except AssertionError as exc:
        print("QROS Phase 1B supply-chain gate: FAIL:",exc,file=sys.stderr)
        raise SystemExit(1)
