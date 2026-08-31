import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ContractFoundationTests(unittest.TestCase):
    def load(self,path):
        return json.loads((ROOT/path).read_text(encoding="utf-8"))

    def test_contract_manifest_unique_and_versioned(self):
        manifest=self.load(Path("packages/contracts/contract-manifest.json"))
        seen=set()
        for item in manifest["contracts"]:
            key=(item["contract_id"],item["version"])
            self.assertNotIn(key,seen)
            seen.add(key)
            schema=self.load(Path(item["schema_path"]))
            self.assertIn(f"/{item['contract_id']}/v{item['version']}",schema["$id"])
            self.assertFalse(schema["additionalProperties"])

    def test_pass_never_means_gate_opened(self):
        value=self.load(Path("tests/fixtures/contracts/validation-result.pass-review-only.v1.json"))
        self.assertEqual(value["classification"],"PASS_REVIEW_ONLY")
        self.assertFalse(value["gate_opened"])
        self.assertTrue(value["research_only"])

    def test_unknown_receipt_is_explicit_and_not_pass(self):
        value=self.load(Path("tests/fixtures/contracts/data-receipt.unknown.v1.json"))
        self.assertEqual(value["quality_status"],"UNKNOWN")
        self.assertIsNone(value["source_timestamp"])
        self.assertNotEqual(value["quality_status"],"PASS")

    def test_yuanta_autopilot_boundary_remains_denied(self):
        value=self.load(Path("config/local-source-promotion-policy.json"))
        y=value["source_boundaries"]["yuanta_autopilot_local"]
        self.assertEqual(y["access_mode"],"DENY")
        self.assertFalse(y["inspection_allowed"])
        self.assertFalse(y["upload_allowed"])

if __name__=="__main__":
    unittest.main()
