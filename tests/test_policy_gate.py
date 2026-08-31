import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Phase0PolicyTests(unittest.TestCase):
 def test_hard_gates_are_closed(self):
  p=json.loads((ROOT/"config"/"cost-policy.json").read_text(encoding="utf-8"))
  self.assertTrue(p["zero_cost_required"])
  for k in ("paid_services_allowed","paid_runners_allowed","larger_runners_allowed","gpu_runners_allowed","paid_data_allowed","paid_llm_api_allowed","paid_storage_allowed","paid_code_signing_allowed","actions_paid_overage_allowed","package_authorized","release_authorized","yuanta_integration_authorized","live_trading_authorized"):
   self.assertFalse(p[k],k)
  self.assertEqual(p["repository_visibility"],"public")
 def test_jnu_validation_gate_remains_unsolved(self):
  r=json.loads((ROOT/"config"/"data-source-registry.json").read_text(encoding="utf-8"))
  self.assertEqual(r["constraints"]["JNU_VALIDATION_GRADE_INTRADAY"],"UNSOLVED_UNDER_ZERO_COST_POLICY")
 def test_unverified_terms_are_denied(self):
  r=json.loads((ROOT/"config"/"data-source-registry.json").read_text(encoding="utf-8"))
  for s in r["sources"]:
   if s["terms_verified_at"] is None:self.assertTrue(s["status"].startswith("DENY_"),s["source_id"])
 def test_external_lean_is_gitlink_not_qros_owned_blob_tree(self):
  line=subprocess.check_output(["git","ls-files","-s","external/lean"],cwd=ROOT,text=True).strip()
  self.assertTrue(line.startswith("160000 "))
  self.assertIn("b692bf4788e8b54fc23bdcb5659666bf055ce89f",line)
if __name__=="__main__":unittest.main()
