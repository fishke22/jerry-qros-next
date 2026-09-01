from __future__ import annotations
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHA40=re.compile(r"^[0-9a-f]{40}$");SHA256=re.compile(r"^[0-9a-f]{64}$");EXACT=re.compile(r"^[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9._-]*)$")
def load(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def fail(m):raise AssertionError(m)
def validate_dependency_registry():
 r=load("config/dependency-registry.json");ids=set()
 if r.get("unknown_is_deny") is not True:fail("registry not fail-closed")
 for d in r["dependencies"]:
  if d["dependency_id"] in ids:fail("duplicate dependency");ids.add(d["dependency_id"])
  if d["status"]=="ADOPTED":
   p=d.get("pin_type")
   if p in ("GIT_COMMIT_SHA40","GIT_SUBMODULE_SHA40"):
    if not SHA40.fullmatch(d.get("revision") or ""):fail("git pin invalid: "+d["dependency_id"])
   elif p=="PYPI_EXACT_VERSION":
    if not EXACT.fullmatch(d.get("version_label") or "") or not d.get("artifact_sha256"):fail("pypi pin invalid: "+d["dependency_id"])
   elif p=="EXACT_TOOLCHAIN_VERSION":
    if d.get("version_label")!=d.get("revision") or not EXACT.fullmatch(d.get("version_label") or ""):fail("toolchain pin invalid")
   else:fail("unsupported pin type: "+str(p))
   if str(d["license_spdx"]).startswith("UNKNOWN") or not d["license_verified_at"]:fail("license unverified")
   if not d["cost_class"].startswith(("FREE_","OSS_")):fail("cost unverified")
  if d["status"].startswith("PLANNED_") and d["introduction_authorized"] is not False:fail("planned dependency authorized")
def validate_lockfile():
 lock=(ROOT/"requirements"/"phase2.lock").read_text(encoding="utf-8")
 for d in [x for x in load("config/dependency-registry.json")["dependencies"] if x["runtime_scope"]=="RUNTIME" and x["status"]=="ADOPTED"]:
  n="pandera[pyarrow]==" if d["package_name"]=="pandera" else f"{d['package_name']}=="
  if n not in lock:fail("runtime missing from lock")
  for h in d["artifact_sha256"].values():
   if f"sha256:{h}" not in lock:fail("runtime hash missing")
 g=load("global.json")["sdk"]
 if g.get("version")!="10.0.400" or g.get("rollForward")!="disable":fail(".NET global.json drift")
def validate_lean_gitlink():
 p=subprocess.check_output(["git","ls-tree","HEAD","external/lean"],cwd=ROOT,text=True).strip().split()
 if len(p)<3 or p[0]!="160000" or p[1]!="commit" or p[2]!="b692bf4788e8b54fc23bdcb5659666bf055ce89f":fail("LEAN gitlink drift")
def validate_sbom():
 b=load("supply-chain/bom.cdx.json");r=load("config/dependency-registry.json")["dependencies"]
 introduced=[d for d in r if d["status"]=="ADOPTED" and d["runtime_scope"] in ("RUNTIME","QUANT_ENGINE")]
 if len(b["components"])!=len(introduced):fail("SBOM component count drift")
 purls={c.get("purl") for c in b["components"]}
 if "pkg:github/QuantConnect/Lean@b692bf4788e8b54fc23bdcb5659666bf055ce89f" not in purls:fail("LEAN missing from SBOM")
def validate_license_manifest():
 m=load("supply-chain/dependency-license-manifest.json");q=m.get("quant_engine_dependencies",[])
 if len(q)!=1 or q[0].get("license_spdx")!="Apache-2.0":fail("LEAN license drift")
 t={x["dependency_id"]:x for x in m.get("toolchain_dependencies",[])}
 if t.get("cpython",{}).get("version")!="3.14.7" or t.get("dotnet-sdk",{}).get("version")!="10.0.400":fail("toolchain evidence drift")
def validate_source_and_provenance():
 s=load("supply-chain/source-revisions.json")
 if s.get("dotnet_sdk",{}).get("version")!="10.0.400":fail(".NET source evidence drift")
 e=load("supply-chain/build-environment.json")
 if e.get("paid_compute_allowed") is not False or e.get("product_build_exists") is not False:fail("hard gate drift")
 if e.get("quant_engine",{}).get("revision")!="b692bf4788e8b54fc23bdcb5659666bf055ce89f":fail("LEAN build evidence drift")
def validate_phase3d_lean_evidence():
 g=load("supply-chain/lean/launcher-patched-nuget-graph.json");m=load("supply-chain/lean/launcher-patched-nuget-license-metadata.json");d=load("config/lean-nuget-license-dispositions.json");b=load("supply-chain/lean/launcher-patched-bom.cdx.json")
 if g.get("package_count")!=55 or g.get("project_count")!=19:fail("Phase 3D NuGet graph count drift")
 ids={n["identity"] for t in g["targets"] for n in t["nodes"] if n.get("type")=="package"}
 if "ProDotNetZip/1.20.0" not in ids or any(x.split("/",1)[0].lower() in ("dotnetzip","netmq") for x in ids):fail("Phase 3D patched package set drift")
 if m.get("package_count")!=55 or {x["identity"] for x in m["packages"]}!=ids:fail("Phase 3D license metadata coverage drift")
 if d.get("unknown_is_deny") is not True or d.get("package_release_authorized") is not False:fail("Phase 3D license policy drift")
 manual={x["identity"] for x in m["packages"] if x.get("requires_manual_review")}
 rows=d.get("dispositions",[])
 if len(rows)!=11 or {x.get("identity") for x in rows}!=manual or any(x.get("review_status")!="ACCEPTED" or not x.get("spdx_expression") for x in rows):fail("Phase 3D manual license disposition drift")
 if len(b.get("components",[]))!=55:fail("Phase 3D patched SBOM count drift")
 purls={x.get("purl") for x in b["components"]}
 expected={"pkg:nuget/"+x.rsplit("/",1)[0]+"@"+x.rsplit("/",1)[1] for x in ids}
 if purls!=expected:fail("Phase 3D patched SBOM package coverage drift")
def main():
 for f in (validate_dependency_registry,validate_lockfile,validate_lean_gitlink,validate_sbom,validate_license_manifest,validate_source_and_provenance,validate_phase3d_lean_evidence):f();print("PASS",f.__name__)
 print("QROS Phase 3A supply-chain gate: PASS");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AssertionError,subprocess.CalledProcessError) as e:print("QROS Phase 3A supply-chain gate: FAIL:",e,file=sys.stderr);raise SystemExit(1)
