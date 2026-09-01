import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class PatchedLeanLicenseOverrideTests(unittest.TestCase):
    def test_overrides_are_exact_and_not_release_clearance(self):
        r=json.loads((ROOT/"config"/"patched-lean-license-overrides.json").read_text(encoding="utf-8"))
        self.assertFalse(r["release_clearance"])
        by={(x["package"],x["version"]):x for x in r["overrides"]}
        self.assertEqual(by[("AsyncIO","0.1.69")]["spdx"],"MPL-2.0")
        self.assertEqual(by[("CloneExtensions","1.3.0")]["spdx"],"Apache-2.0")
        self.assertEqual(len(by),2)

if __name__=="__main__":
    unittest.main()
