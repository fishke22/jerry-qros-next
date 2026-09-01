from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_ENGINE="b692bf4788e8b54fc23bdcb5659666bf055ce89f"
EXPECTED_SCOPE="LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH"
EXPECTED_BLOCKERS={
("DotNetZip","1.16.0","GHSA-xhg6-9j5j-w4vf","HIGH"),
("System.Drawing.Common","4.7.0","GHSA-rxg9-xrhp-64gj","CRITICAL"),
("System.Net.Http.WinHttpHandler","4.4.0","GHSA-6xh7-4v2w-36q6","HIGH"),
("System.Private.ServiceModel","4.4.0","GHSA-jc8g-xhw5-6x46","HIGH"),
("System.ServiceModel.Primitives","4.4.0","GHSA-jc8g-xhw5-6x46","HIGH")}
def load_review():return json.loads((ROOT/"config"/"lean-security-review.json").read_text(encoding="utf-8"))
def validate_review():
 r=load_review()
 if r.get("engine_revision")!=EXPECTED_ENGINE:raise AssertionError("LEAN security review revision drift")
 if r.get("unknown_is_deny") is not True:raise AssertionError("LEAN security review must remain fail-closed")
 if r.get("baseline_unpatched_upstream_runtime_allowed") is not False:raise AssertionError("unpatched upstream LEAN runtime unexpectedly allowed")
 if r.get("runtime_promotion_allowed") is not True:raise AssertionError("Phase 3D patched local runtime unexpectedly denied")
 if r.get("runtime_promotion_scope")!=EXPECTED_SCOPE:raise AssertionError("Phase 3D runtime promotion scope drift")
 if r.get("phase3b_merge_allowed") is not False:raise AssertionError("historical Phase 3B unpatched merge gate unexpectedly opened")
 if r.get("lean_transitive_sbom_status")!="PATCHED_LAUNCHER_COMPLETE_55_NUGET_PACKAGES":raise AssertionError("patched Launcher SBOM completeness drift")
 o={(x["package"],x["version"],x["advisory"],x["severity"]) for x in r.get("blockers",[])}
 if not EXPECTED_BLOCKERS.issubset(o):raise AssertionError("known baseline LEAN security blocker missing from review")
 if any(x.get("phase3d_patched_runtime_status")!="ABSENT_FROM_RESOLVED_GRAPH" for x in r.get("blockers",[])):raise AssertionError("Phase 3D blocker disposition drift")
 if r.get("remediation_gate",{}).get("currently_satisfied") is not True:raise AssertionError("Phase 3D remediation gate unexpectedly unsatisfied")
 ov=r.get("runtime_overlay",{})
 for k in ("package_authorized","release_authorized","yuanta_integration_authorized","live_trading_authorized"):
  if ov.get(k) is not False:raise AssertionError("hard gate unexpectedly opened: "+k)
 return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--enforce-runtime-promotion",action="store_true");a=p.parse_args();r=validate_review();print("QROS LEAN security review representation: PASS")
 if a.enforce_runtime_promotion:
  if not r["runtime_promotion_allowed"] or r["runtime_promotion_scope"]!=EXPECTED_SCOPE:
   print("QROS LEAN runtime promotion gate: DENY",file=sys.stderr);return 2
  print("QROS LEAN runtime promotion gate: ALLOW_LOCAL_RESEARCH_BACKTEST_PHASE3D_PATCH_ONLY")
 return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except AssertionError as e:print("QROS LEAN security review: FAIL:",e,file=sys.stderr);raise SystemExit(1)
