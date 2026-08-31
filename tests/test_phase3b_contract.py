import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase3BContractTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_backtest_contract_is_fail_closed(self):
        schema = self.load("packages/schemas/lean-backtest-result.v1.schema.json")
        props = schema["properties"]
        self.assertEqual(props["classification"]["const"], "PASS_REVIEW_ONLY")
        self.assertTrue(props["research_only"]["const"])
        self.assertFalse(props["gate_opened"]["const"])
        self.assertEqual(props["statistics"]["properties"]["total_orders"]["const"], "0")

    def test_manifest_registers_backtest_contract(self):
        manifest = self.load("packages/contracts/contract-manifest.json")
        matches = [
            item for item in manifest["contracts"]
            if item["contract_id"] == "lean-backtest-result" and item["version"] == "1"
        ]
        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
