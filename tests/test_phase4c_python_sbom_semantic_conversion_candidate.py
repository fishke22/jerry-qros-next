import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class Phase4CPythonSemanticConversionCandidateTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(
            (
                ROOT
                / "config"
                / "phase4c-python-sbom-semantic-conversion-candidate.json"
            ).read_text(encoding="utf-8")
        )
        self.workflow=(
            ROOT
            / ".github"
            / "workflows"
            / "phase4c-python-semantic-conversion-candidate.yml"
        ).read_text(encoding="utf-8")

    def test_exact_qut_input_is_pinned(self):
        i=self.policy["input"]
        self.assertEqual(
            i["source_head"],
            "32e74ccfde93cf02fc0f149dd84a9c4ea6b1112e",
        )
        self.assertEqual(
            i["expected_sbom_sha256"],
            "50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623",
        )
        self.assertEqual(i["expected_component_count"],253)
        self.assertIn(i["source_head"],self.workflow)
        self.assertIn(i["expected_sbom_sha256"],self.workflow)

    def test_fidelity_rule_is_initially_strict(self):
        f=self.policy["fidelity"]
        self.assertTrue(f["input_strict_validation_required"])
        self.assertTrue(f["output_strict_validation_required"])
        self.assertTrue(f["byte_deterministic_output_required"])
        self.assertEqual(
            f["semantic_rule"],
            "CANONICAL_JSON_DEEP_EQUAL_AFTER_SERIALNUMBER_ABSENCE_PRESERVATION_AND_EXACT_SET_COLLECTION_ORDER_NORMALIZATION_EXCEPT_$schema_AND_specVersion",
        )
        self.assertIn('d.pop("$schema",None)',self.workflow)
        self.assertIn('d.pop("specVersion",None)',self.workflow)
        self.assertIn("if a != b:",self.workflow)
        serial=self.policy["fidelity"]["serial_number_policy"]
        self.assertFalse(serial["cyclonedx_1_7_required"])
        self.assertIn("IF_INPUT_ABSENT",serial["rule"])
        self.assertIn('doc.pop("serialNumber")',self.workflow)
        self.assertIn("UUID(serial.removeprefix",self.workflow)
        self.assertIn("QROS_PHASE4C_SERIALNUMBER_ABSENCE_PRESERVATION=PASS",self.workflow)
        order=f["order_insensitive_collections"]
        self.assertEqual(
            set(order),
            {"components","externalReferences"},
        )
        self.assertTrue(f["all_other_arrays_order_sensitive"])
        self.assertIn(
            'if key=="components"',
            self.workflow,
        )
        self.assertIn(
            'elif key=="externalReferences"',
            self.workflow,
        )
        self.assertIn(
            "QROS_PHASE4C_SET_COLLECTION_ORDER_NORMALIZATION=PASS",
            self.workflow,
        )

    def test_converter_execution_is_candidate_only(self):
        s=self.policy["scope"]
        self.assertTrue(s["bom_from_json_execution_authorized"])
        self.assertTrue(s["json_v1_7_generation_authorized"])
        self.assertTrue(s["schema_validation_execution_authorized"])
        self.assertTrue(s["semantic_fidelity_test_authorized"])
        for key in (
            "permanent_tool_adoption_authorized",
            "cargo_cyclonedx_permanent_adoption_authorized",
            "dependency_registry_promotion_authorized",
            "canonical_sbom_1_7_promotion_authorized",
            "main_runtime_promotion_authorized",
            "production_readiness_authorized",
        ):
            self.assertFalse(s[key])

    def test_conversion_uses_exact_offline_converter_install(self):
        self.assertIn("--require-hashes",self.workflow)
        self.assertIn("--no-index",self.workflow)
        self.assertIn("--no-deps",self.workflow)
        self.assertIn("Bom.from_json(",self.workflow)
        self.assertIn("JsonV1Dot7(",self.workflow)
        self.assertIn("JsonStrictValidator(SchemaVersion.V1_5)",self.workflow)
        self.assertIn("JsonStrictValidator(SchemaVersion.V1_7)",self.workflow)

    def test_hard_gates_remain_closed(self):
        g=self.policy["hard_gates"]
        self.assertTrue(g["zero_cost_required"])
        self.assertFalse(g["package_authorized"])
        self.assertFalse(g["release_authorized"])
        self.assertFalse(g["yuanta_integration_authorized"])
        self.assertFalse(g["live_trading_authorized"])


if __name__=="__main__":
    unittest.main()
