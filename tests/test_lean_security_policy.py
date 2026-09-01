import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LeanSecurityPolicyTests(unittest.TestCase):
 def setUp(self):self.review=json.loads((ROOT/"config"/"lean-security-review.json").read_text(encoding="utf-8"))
 def test_only_phase3d_patched_local_runtime_is_allowed(self):
  self.assertTrue(self.review["runtime_promotion_allowed"]);self.assertEqual(self.review["runtime_promotion_scope"],"LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH");self.assertFalse(self.review["baseline_unpatched_upstream_runtime_allowed"]);self.assertFalse(self.review["phase3b_merge_allowed"]);self.assertTrue(self.review["remediation_gate"]["currently_satisfied"])
 def test_high_and_critical_baseline_blockers_remain_explicit(self):
  p={(x["package"],x["advisory"],x["severity"]) for x in self.review["blockers"]};self.assertIn(("DotNetZip","GHSA-xhg6-9j5j-w4vf","HIGH"),p);self.assertIn(("System.Drawing.Common","GHSA-rxg9-xrhp-64gj","CRITICAL"),p);self.assertGreaterEqual(len(p),5);self.assertTrue(all(x["phase3d_patched_runtime_status"]=="ABSENT_FROM_RESOLVED_GRAPH" for x in self.review["blockers"]))
 def test_patched_transitive_sbom_is_complete(self):self.assertEqual(self.review["lean_transitive_sbom_status"],"PATCHED_LAUNCHER_COMPLETE_55_NUGET_PACKAGES");self.assertEqual(self.review["acceptance_evidence"]["package_count"],55)
 def test_packaging_broker_and_live_trading_stay_closed(self):
  o=self.review["runtime_overlay"]
  for k in ("package_authorized","release_authorized","yuanta_integration_authorized","live_trading_authorized"):self.assertFalse(o[k])
if __name__=="__main__":unittest.main()
