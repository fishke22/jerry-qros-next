import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4CanonicalSbomResearchTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (ROOT / "config" / "phase4-canonical-sbom-research.json").read_text(
                encoding="utf-8"
            )
        )

    def test_canonical_policy_and_current_gap_are_explicit(self):
        self.assertEqual(self.policy["canonical_policy"]["format"], "CycloneDX")
        self.assertEqual(
            self.policy["canonical_policy"]["required_spec_version"], "1.7"
        )
        current = self.policy["current_cargo_candidate"]
        self.assertEqual(current["generator"], "cargo-cyclonedx")
        self.assertEqual(current["version"], "0.5.9")
        self.assertEqual(current["spec_version"], "1.5")
        self.assertFalse(current["permanent_tool_adoption_authorized"])

    def test_conversion_candidate_is_exact_but_not_adopted(self):
        candidate = self.policy["conversion_candidate"]
        self.assertEqual(candidate["tool"], "CycloneDX CLI")
        self.assertEqual(candidate["version"], "0.33.1")
        self.assertEqual(
            candidate["source_revision"],
            "b3cfa4b0edc356dad07e0b6e7ab6da0a94af0246",
        )
        self.assertEqual(candidate["license"], "Apache-2.0")
        self.assertEqual(candidate["target_framework"], "net10.0")
        self.assertEqual(candidate["dotnet_sdk_candidate"], "10.0.400")
        self.assertTrue(candidate["supports_output_version_1_7"])
        self.assertTrue(candidate["supports_validation_fail_on_errors"])
        self.assertFalse(candidate["upstream_packages_lock_present"])
        self.assertFalse(candidate["permanent_tool_adoption_authorized"])

    def test_fidelity_gate_is_not_schema_only(self):
        required = set(self.policy["fidelity_requirements"])
        self.assertIn("component count", required)
        self.assertIn("component bom-ref", required)
        self.assertIn("component purl", required)
        self.assertIn("component hashes", required)
        self.assertIn("component licenses", required)
        self.assertIn("dependency edge set", required)
        rejected = self.policy["rejected_or_deferred"]
        self.assertEqual(rejected["manual_spec_version_string_rewrite"], "REJECT")
        self.assertEqual(
            rejected["schema_validation_without_fidelity_test"], "REJECT"
        )

    def test_all_promotion_gates_remain_closed(self):
        scope = self.policy["acceptance_scope"]
        self.assertTrue(scope["research_complete_enough_for_candidate_design"])
        self.assertFalse(scope["implementation_authorized"])
        self.assertFalse(scope["cyclonedx_cli_permanent_adoption_authorized"])
        self.assertFalse(scope["canonical_sbom_1_7_promotion_authorized"])
        self.assertFalse(scope["dependency_registry_promotion_authorized"])
        self.assertFalse(scope["main_runtime_promotion_authorized"])
        self.assertFalse(scope["production_readiness_authorized"])
        gates = self.policy["hard_gates"]
        self.assertTrue(gates["zero_cost_required"])
        self.assertFalse(gates["package_authorized"])
        self.assertFalse(gates["release_authorized"])
        self.assertFalse(gates["yuanta_integration_authorized"])
        self.assertFalse(gates["live_trading_authorized"])

    def test_adr_is_proposed_not_accepted(self):
        adr = (
            ROOT / "docs" / "adr" / "0014-phase-4c-canonical-sbom-1-7.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Status: **PROPOSED / REVIEW REQUIRED**", adr)
        self.assertIn("PHASE4_CANONICAL_SBOM_1_7_PROMOTION = DENY", adr)
        self.assertNotIn("Status: **ACCEPTED**", adr)


if __name__ == "__main__":
    unittest.main()
