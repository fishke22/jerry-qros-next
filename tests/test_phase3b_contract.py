import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase3BContractTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_v1_backtest_contract_remains_fail_closed_and_generic(self):
        schema = self.load("packages/schemas/lean-backtest-result.v1.schema.json")
        props = schema["properties"]
        self.assertEqual(props["classification"]["const"], "PASS_REVIEW_ONLY")
        self.assertTrue(props["research_only"]["const"])
        self.assertFalse(props["gate_opened"]["const"])
        self.assertEqual(props["statistics"]["additionalProperties"]["type"], "string")

    def test_v2_backtest_contract_remains_immutable_and_compatible(self):
        schema = self.load("packages/schemas/lean-backtest-result.v2.schema.json")
        self.assertEqual(schema["properties"]["contract_version"]["const"], "2")
        overlay = schema["properties"]["runtime_overlay"]
        self.assertNotIn("patch_implementation_hash", overlay["required"])
        count_pattern = overlay["properties"]["runtime_assembly_count"]["pattern"]
        self.assertIsNotNone(re.fullmatch(count_pattern, "1"))
        self.assertIsNotNone(re.fullmatch(count_pattern, "2"))

    def test_v2_provenance_contract_remains_immutable_and_compatible(self):
        schema = self.load("packages/schemas/provenance-record.v2.schema.json")
        runtime = schema["properties"]["runtime_identity"]
        self.assertNotIn("patch_implementation_hash", runtime["required"])
        count_pattern = runtime["properties"]["runtime_assembly_count"]["pattern"]
        self.assertIsNotNone(re.fullmatch(count_pattern, "1"))
        self.assertIsNotNone(re.fullmatch(count_pattern, "2"))

    def test_v3_backtest_contract_binds_hardened_runtime_overlay(self):
        schema = self.load("packages/schemas/lean-backtest-result.v3.schema.json")
        self.assertEqual(schema["properties"]["contract_version"]["const"], "3")
        overlay = schema["properties"]["runtime_overlay"]
        self.assertIn("patch_implementation_hash", overlay["required"])
        count_pattern = overlay["properties"]["runtime_assembly_count"]["pattern"]
        self.assertIsNone(re.fullmatch(count_pattern, "2"))
        self.assertIsNotNone(re.fullmatch(count_pattern, "3"))
        self.assertIsNotNone(re.fullmatch(count_pattern, "191"))

    def test_v3_provenance_contract_binds_hardened_runtime_identity(self):
        schema = self.load("packages/schemas/provenance-record.v3.schema.json")
        self.assertEqual(schema["properties"]["contract_version"]["const"], "3")
        runtime = schema["properties"]["runtime_identity"]
        self.assertIn("patch_implementation_hash", runtime["required"])
        count_pattern = runtime["properties"]["runtime_assembly_count"]["pattern"]
        self.assertIsNone(re.fullmatch(count_pattern, "2"))
        self.assertIsNotNone(re.fullmatch(count_pattern, "3"))

    def test_manifest_registers_versioned_runtime_contracts(self):
        manifest = self.load("packages/contracts/contract-manifest.json")
        backtest_versions = {
            item["version"]
            for item in manifest["contracts"]
            if item["contract_id"] == "lean-backtest-result"
        }
        provenance_versions = {
            item["version"]
            for item in manifest["contracts"]
            if item["contract_id"] == "provenance-record"
        }
        self.assertEqual(backtest_versions, {"1", "2", "3"})
        self.assertEqual(provenance_versions, {"1", "2", "3"})


if __name__ == "__main__":
    unittest.main()
