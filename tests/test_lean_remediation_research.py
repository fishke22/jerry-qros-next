import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LeanRemediationResearchTests(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/"config"/"lean-remediation-research.json").read_text(encoding="utf-8"))
 def test_record_is_historical_and_superseded(self):
  self.assertEqual(self.r["record_semantics"],"HISTORICAL_PHASE3C_SNAPSHOT");self.assertEqual(self.r["superseded_by"],"docs/adr/0010-phase-3d-lean-security-patch-candidate.md");self.assertEqual(self.r["current_runtime_authority"],"config/lean-security-review.json");self.assertFalse(self.r["current_runtime_state_encoded_here"])
 def test_original_phase3c_denials_remain_historical_evidence(self):
  self.assertTrue(self.r["research_only"]);self.assertFalse(self.r["architecture_amendment_approved"]);self.assertFalse(self.r["lean_source_patch_authorized"]);self.assertFalse(self.r["lean_fork_authorized"]);self.assertFalse(self.r["lean_gitlink_change_authorized"]);self.assertFalse(self.r["runtime_promotion_allowed"])
 def test_latest_official_master_is_not_rewritten_as_fixed(self):self.assertFalse(self.r["upstream"]["official_revision_remediation_available"]);self.assertEqual(self.r["upstream"]["latest_master_dotnetzip_version"],"1.16.0")
 def test_audit_maps_two_root_cause_clusters(self):
  c={x["cluster"]:x for x in self.r["root_cause_clusters"]};self.assertIn("COMPRESSION",c);self.assertIn("MESSAGING",c);self.assertFalse(c["COMPRESSION"]["no_source_change_escape_path"]);self.assertFalse(c["MESSAGING"]["no_source_change_escape_path"])
 def test_historical_gate_is_not_current_runtime_authority(self):
  g=self.r["next_gate"];self.assertTrue(g["historical_phase3c_gate"]);self.assertFalse(g["current_runtime_gate"]);self.assertTrue(g["research_evidence_accepted"]);self.assertFalse(g["security_remediation_available"]);self.assertTrue(g["hard_stop_active"])
 def test_warning_suppression_and_drop_in_fork_are_rejected(self):
  c={x["candidate"]:x for x in self.r["candidate_paths"]};self.assertEqual(c["DROP_IN_DOTNETZIP_FORK"]["status"],"REJECTED");self.assertEqual(c["SUPPRESS_NUGET_SECURITY_WARNINGS"]["status"],"REJECTED")
if __name__=="__main__":unittest.main()
