import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LeanSecurityPolicyTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads(
            (ROOT / "config" / "lean-security-review.json").read_text(encoding="utf-8")
        )

    def test_runtime_promotion_and_phase3b_merge_are_denied(self):
        self.assertFalse(self.review["runtime_promotion_allowed"])
        self.assertFalse(self.review["phase3b_merge_allowed"])
        self.assertFalse(self.review["remediation_gate"]["currently_satisfied"])

    def test_high_and_critical_blockers_are_explicit(self):
        pairs = {
            (x["package"], x["advisory"], x["severity"])
            for x in self.review["blockers"]
        }
        self.assertIn(("DotNetZip", "GHSA-xhg6-9j5j-w4vf", "HIGH"), pairs)
        self.assertIn(
            ("System.Drawing.Common", "GHSA-rxg9-xrhp-64gj", "CRITICAL"), pairs
        )
        self.assertGreaterEqual(len(pairs), 5)

    def test_transitive_sbom_is_not_claimed_complete(self):
        self.assertEqual(
            self.review["lean_transitive_sbom_status"],
            "INCOMPLETE_REQUIRES_FULL_NUGET_GRAPH",
        )


if __name__ == "__main__":
    unittest.main()
