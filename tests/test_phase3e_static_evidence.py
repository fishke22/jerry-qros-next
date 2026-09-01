import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Phase3EStaticEvidenceTests(unittest.TestCase):
    def test_patched_sbom_and_license_review_are_frozen_and_non_promotional(self):
        sbom=json.loads((ROOT/"supply-chain"/"patched-lean-phase3e.cdx.json").read_text(encoding="utf-8"))
        review=json.loads((ROOT/"supply-chain"/"patched-lean-phase3e-license-review.json").read_text(encoding="utf-8"))
        self.assertEqual(sbom["bomFormat"],"CycloneDX")
        self.assertEqual(sbom["specVersion"],"1.7")
        self.assertEqual(len(sbom["components"]),59)
        self.assertEqual(review["package_count"],59)
        self.assertEqual(review["unknown_license_count"],0)
        self.assertFalse(review["release_clearance"])
        self.assertEqual(review["status"],"PASS_RESEARCH_IDENTIFICATION")
        for item in review["packages"]:
            self.assertFalse((item["license"].get("source") or "").startswith("/"))

if __name__=="__main__":
    unittest.main()
