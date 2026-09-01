from __future__ import annotations
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHA40=re.compile(r"^[0-9a-f]{40}$");SHA256=re.compile(r"^[0-9a-f]{64}$");EXACT=re.compile(r"^[0-9]+(?:\.[0-9]+)+(?:[A-Za-z0-9._-]*)$")
def load(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def fail(m):raise AssertionError(m)
def git_tree(rev):
 return subprocess.check_output(["git","rev-parse",rev+"^{tree}"],cwd=ROOT,text=True).strip()
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
 lean=next(x for x in r["dependencies"] if x["dependency_id"]=="quantconnect-lean")
 if lean.get("security_status")!="ACCEPTED_PHASE3D_PATCHED_LOCAL_RESEARCH_RUNTIME" or lean.get("runtime_promotion_allowed") is not True:fail("Phase 3D LEAN registry acceptance drift")
 if lean.get("runtime_promotion_scope")!="LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH" or lean.get("unpatched_upstream_runtime_allowed") is not False:fail("Phase 3D LEAN runtime scope drift")
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
 lc=next(c for c in b["components"] if c.get("purl")=="pkg:github/QuantConnect/Lean@b692bf4788e8b54fc23bdcb5659666bf055ce89f");props={x["name"]:x["value"] for x in lc.get("properties",[])}
 if props.get("qros:runtime-overlay")!="PHASE3D_DETERMINISTIC_CHECKOUT_TIME_PATCH" or props.get("qros:runtime-overlay-scope")!="LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY" or props.get("qros:unpatched-upstream-runtime-allowed")!="false":fail("main SBOM Phase 3D overlay drift")
def validate_license_manifest():
 m=load("supply-chain/dependency-license-manifest.json");q=m.get("quant_engine_dependencies",[])
 if len(q)!=1 or q[0].get("license_spdx")!="Apache-2.0":fail("LEAN license drift")
 if q[0].get("runtime_overlay_license_status")!="PASS_55_PACKAGES" or q[0].get("package_authorized") is not False or q[0].get("release_authorized") is not False:fail("Phase 3D LEAN license overlay drift")
 o=m.get("phase3d_quant_engine_overlay",{})
 if o.get("status")!="ACCEPTED_LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY" or o.get("resolved_package_count")!=55 or o.get("distribution_status")!="DENY_UNTIL_SEPARATE_PACKAGE_RELEASE_AUTHORIZATION":fail("Phase 3D license manifest closure drift")
 t={x["dependency_id"]:x for x in m.get("toolchain_dependencies",[])}
 if t.get("cpython",{}).get("version")!="3.14.7" or t.get("dotnet-sdk",{}).get("version")!="10.0.400":fail("toolchain evidence drift")
def validate_source_and_provenance():
 s=load("supply-chain/source-revisions.json")
 if s.get("dotnet_sdk",{}).get("version")!="10.0.400":fail(".NET source evidence drift")
 o=s.get("quant_engine_runtime_overlay",{})
 if o.get("base_revision")!="b692bf4788e8b54fc23bdcb5659666bf055ce89f" or o.get("gitlink_changed") is not False or o.get("fork_created") is not False:fail("Phase 3D source overlay drift")
 if o.get("runtime_scope")!="LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY" or o.get("package_authorized") is not False or o.get("release_authorized") is not False:fail("Phase 3D source overlay scope drift")
 p=load("supply-chain/provenance-manifest.json").get("quant_engine_runtime_overlay",{})
 if p.get("status")!="ACCEPTED_PHASE3D_LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY" or p.get("unpatched_upstream_runtime_allowed") is not False:fail("Phase 3D provenance overlay drift")
 e=load("supply-chain/build-environment.json")
 if e.get("paid_compute_allowed") is not False or e.get("product_build_exists") is not False:fail("hard gate drift")
 if e.get("quant_engine",{}).get("revision")!="b692bf4788e8b54fc23bdcb5659666bf055ce89f":fail("LEAN build evidence drift")
 q=e.get("quant_engine",{})
 if q.get("status")!="ACCEPTED_PHASE3D_PATCHED_LOCAL_RESEARCH_RUNTIME" or q.get("runtime_promotion_allowed") is not True:fail("Phase 3D build-environment acceptance drift")
 if q.get("runtime_promotion_scope")!="LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH" or q.get("baseline_unpatched_upstream_runtime_allowed") is not False:fail("Phase 3D build-environment scope drift")
 if q.get("synthetic_backtest",{}).get("status")!="ACCEPTED_LOCAL_RESEARCH_BACKTEST_PHASE3D_PATCH_ONLY":fail("Phase 3D synthetic backtest build evidence drift")
 c=e.get("phase3_merge_closure",{})
 if c.get("pr")!=13 or c.get("integration_commit")!="744b53c18ab433346ab01fb26d35c55e5633ba43" or c.get("accepted_head")!="7b5f89a1972fd39abb78e0ad998eacf874e42739" or c.get("tree_equivalent") is not True:fail("Phase 3 merge closure evidence drift")
 evidence_ref="refs/remotes/origin/evidence/phase-3d-accepted-head"
 if c.get("accepted_head_evidence_ref")!="refs/heads/evidence/phase-3d-accepted-head":fail("Phase 3 accepted-head evidence ref drift")
 evidence_head=subprocess.check_output(["git","rev-parse",evidence_ref],cwd=ROOT,text=True).strip()
 if evidence_head!=c["accepted_head"]:fail("Phase 3 accepted-head evidence ref target drift")
 accepted_tree=git_tree(evidence_ref);integration_tree=git_tree(c["integration_commit"])
 if accepted_tree!=c.get("accepted_tree") or integration_tree!=c.get("integration_tree") or accepted_tree!=integration_tree:fail("Phase 3 merge tree proof drift")
 h=e.get("phase3e_hardening_closure",{})
 if h.get("status")!="ACCEPTED_MERGED_LOCAL_RESEARCH_BACKTEST_HARDENING_ONLY" or h.get("pr")!=15:fail("Phase 3E closure status drift")
 if h.get("accepted_head")!="968255313ff0bff9051d50d17da335bd9da10207" or h.get("integration_commit")!="791d99363228126e199d6cdac89857612743a2c9" or h.get("tree_equivalent") is not True:fail("Phase 3E merge closure evidence drift")
 evidence_ref3e="refs/remotes/origin/evidence/phase-3e-accepted-head"
 if h.get("accepted_head_evidence_ref")!="refs/heads/evidence/phase-3e-accepted-head":fail("Phase 3E accepted-head evidence ref drift")
 evidence_head3e=subprocess.check_output(["git","rev-parse",evidence_ref3e],cwd=ROOT,text=True).strip()
 if evidence_head3e!=h["accepted_head"]:fail("Phase 3E accepted-head evidence ref target drift")
 accepted_tree3e=git_tree(evidence_ref3e);integration_tree3e=git_tree(h["integration_commit"])
 if accepted_tree3e!=h.get("accepted_tree") or integration_tree3e!=h.get("integration_tree") or accepted_tree3e!=integration_tree3e:fail("Phase 3E merge tree proof drift")
 if h.get("runtime_result_contract")!="lean-backtest-result/v2" or h.get("runtime_assembly_count")!=191:fail("Phase 3E runtime identity evidence drift")
 for key in ("package_authorized","release_authorized","yuanta_integration_authorized","live_trading_authorized"):
  if h.get(key) is not False:fail("Phase 3E hard gate drift: "+key)
 if h.get("incremental_monetary_cost")!=0:fail("Phase 3E zero-cost closure drift")
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
