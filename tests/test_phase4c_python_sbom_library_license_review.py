import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4CPythonLicenseReviewTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads(
            (
                ROOT
                / "config"
                / "phase4c-python-sbom-library-license-dispositions.json"
            ).read_text(encoding="utf-8")
        )
        self.inventory = json.loads(
            (
                ROOT
                / "docs"
                / "source-evidence"
                / "phase-4c-python-wheel-inventory.json"
            ).read_text(encoding="utf-8")
        )

    def test_dispositions_cover_exact_wheel_graph(self):
        expected = {
            (p["name"], p["version"])
            for p in self.inventory["packages"]
        }
        actual = {
            (p["name"], p["version"])
            for p in self.review["dispositions"]
        }
        self.assertEqual(len(expected), 26)
        self.assertEqual(actual, expected)

    def test_no_unknown_or_fee_blocker(self):
        gate = self.review["gate"]
        self.assertEqual(gate["unknown_normalized_license_count"], 0)
        self.assertEqual(gate["conditional_usage_fee_blocker_count"], 0)
        self.assertEqual(
            gate["license_gate"],
            "PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY",
        )
        self.assertEqual(
            gate["zero_cost_gate"],
            "PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY",
        )

    def test_mpl_is_explicit_and_distribution_remains_closed(self):
        fqdn = next(
            p for p in self.review["dispositions"]
            if p["name"] == "fqdn"
        )
        self.assertEqual(fqdn["normalized_license"], "MPL-2.0")
        self.assertIn(
            "MPL_SOURCE_AND_NOTICE",
            fqdn["distribution_disposition"],
        )
        self.assertFalse(
            self.review["policy"]["external_distribution_authorized"]
        )

    def test_rfc3987_uses_artifact_license_expression(self):
        p = next(
            p for p in self.review["dispositions"]
            if p["name"] == "rfc3987-syntax"
        )
        self.assertEqual(p["normalized_license"], "MIT")
        special = self.review["special_cases"]["rfc3987-syntax"]
        self.assertIn("stale metadata", special["resolution"])

    def test_python_dateutil_is_conservative_bsd(self):
        p = next(
            p for p in self.review["dispositions"]
            if p["name"] == "python-dateutil"
        )
        self.assertEqual(p["normalized_license"], "BSD-3-Clause")

    def test_hard_gates_remain_closed(self):
        policy = self.review["policy"]
        self.assertFalse(policy["package_authorized"])
        self.assertFalse(policy["release_authorized"])
        self.assertFalse(policy["permanent_tool_adoption_authorized"])
        self.assertFalse(
            policy["dependency_registry_promotion_authorized"]
        )
        self.assertFalse(
            policy["canonical_sbom_1_7_promotion_authorized"]
        )


if __name__ == "__main__":
    unittest.main()
