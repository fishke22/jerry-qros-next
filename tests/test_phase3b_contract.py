import json
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

    def test_v2_backtest_contract_binds_runtime_overlay(self):
        schema = self.load("packages/schemas/lean-backtest-result.v2.schema.json")
        self.assertEqual(schema["properties"]["contract_version"]["const"], "2")
        self.assertIn("runtime_overlay", schema["required"])
        self.assertIn("overlay_identity", schema["required"])
        overlay = schema["properties"]["runtime_overlay"]
        self.assertFalse(overlay["additionalProperties"])
        self.assertEqual(set(overlay["required"]), {
            "mode",
            "patch_script_hash",
            "patched_graph_hash",
            "launcher_assembly_hash",
            "runtime_assembly_manifest_hash",
            "runtime_assembly_count",
        })

    def test_v2_provenance_contract_binds_runtime_identity(self):
        schema = self.load("packages/schemas/provenance-record.v2.schema.json")
        self.assertIn("runtime_identity", schema["required"])
        runtime = schema["properties"]["runtime_identity"]
        self.assertFalse(runtime["additionalProperties"])
        self.assertIn("runtime_overlay_identity", runtime["required"])

    def test_manifest_registers_v1_and_v2_backtest_contracts(self):
        manifest = self.load("packages/contracts/contract-manifest.json")
        versions = {item["version"] for item in manifest["contracts"] if item["contract_id"] == "lean-backtest-result"}
        self.assertEqual(versions, {"1", "2"})


if __name__ == "__main__":
    unittest.main()
