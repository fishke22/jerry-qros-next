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
        self.assertFalse(self.r["architecture_amendment_approved"])
        self.assertFalse(self.r["lean_source_patch_authorized"])
        self.assertFalse(self.r["lean_fork_authorized"])
        self.assertFalse(self.r["lean_gitlink_change_authorized"])
        self.assertFalse(self.r["runtime_promotion_allowed"])

    def test_latest_official_master_is_not_claimed_fixed(self):
        self.assertFalse(self.r["upstream"]["official_revision_remediation_available"])
        self.assertEqual(
            self.r["upstream"]["latest_master_dotnetzip_version"], "1.16.0"
        )

    def test_warning_suppression_and_drop_in_fork_are_rejected(self):
        c = {x["candidate"]: x for x in self.r["candidate_paths"]}
        self.assertEqual(c["DROP_IN_DOTNETZIP_FORK"]["status"], "REJECTED")
        self.assertEqual(
            c["SUPPRESS_NUGET_SECURITY_WARNINGS"]["status"], "REJECTED"
        )


if __name__ == "__main__":
    unittest.main()
