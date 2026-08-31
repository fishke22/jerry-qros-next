import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LeanRemediationResearchTests(unittest.TestCase):
    def setUp(self):
        self.r = json.loads(
            (ROOT / "config" / "lean-remediation-research.json").read_text(
                encoding="utf-8"
            )
        )

    def test_no_remediation_action_is_authorized(self):
        self.assertTrue(self.r["research_only"])
        self.assertTrue(self.r["architecture_amendment_approved"])
        self.assertTrue(self.r["lean_source_patch_experiment_authorized"])
        self.assertFalse(self.r["lean_source_patch_authorized"])
        self.assertFalse(self.r["lean_fork_authorized"])
        self.assertFalse(self.r["lean_gitlink_change_authorized"])
        self.assertFalse(self.r["runtime_promotion_allowed"])

    def test_latest_official_master_is_not_claimed_fixed(self):
        self.assertFalse(self.r["upstream"]["official_revision_remediation_available"])
        self.assertEqual(
            self.r["upstream"]["latest_master_dotnetzip_version"], "1.16.0"
        )

    def test_audit_maps_two_root_cause_clusters(self):
        clusters = {x["cluster"]: x for x in self.r["root_cause_clusters"]}
        self.assertIn("COMPRESSION", clusters)
        self.assertIn("MESSAGING", clusters)
        self.assertFalse(clusters["COMPRESSION"]["no_source_change_escape_path"])
        self.assertFalse(clusters["MESSAGING"]["no_source_change_escape_path"])

    def test_research_is_accepted_but_security_hard_stop_remains(self):
        gate = self.r["next_gate"]
        self.assertTrue(gate["research_evidence_accepted"])
        self.assertFalse(gate["security_remediation_available"])
        self.assertTrue(gate["hard_stop_active"])
        self.assertFalse(gate["runtime_promotion_allowed"])

    def test_warning_suppression_and_drop_in_fork_are_rejected(self):
        c = {x["candidate"]: x for x in self.r["candidate_paths"]}
        self.assertEqual(c["DROP_IN_DOTNETZIP_FORK"]["status"], "REJECTED")
        self.assertEqual(
            c["SUPPRESS_NUGET_SECURITY_WARNINGS"]["status"], "REJECTED"
        )


if __name__ == "__main__":
    unittest.main()
