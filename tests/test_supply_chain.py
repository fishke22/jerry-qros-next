import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SupplyChainFoundationTests(unittest.TestCase):
    def load(self,path):
        return json.loads((ROOT/path).read_text(encoding="utf-8"))

    def test_no_runtime_dependency_is_introduced(self):
        reg=self.load("config/dependency-registry.json")
        adopted_runtime=[d for d in reg["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
        self.assertEqual(adopted_runtime,[])

    def test_planned_dependencies_are_denied_until_pinned(self):
        reg=self.load("config/dependency-registry.json")
        planned=[d for d in reg["dependencies"] if d["status"].startswith("PLANNED_")]
        self.assertGreater(len(planned),0)
        for d in planned:
            self.assertEqual(d["version_label"],"UNSPECIFIED")
            self.assertFalse(d["introduction_authorized"])

    def test_sbom_has_no_fake_runtime_components(self):
        bom=self.load("supply-chain/bom.cdx.json")
        self.assertEqual(bom["bomFormat"],"CycloneDX")
        self.assertEqual(bom["specVersion"],"1.7")
        self.assertEqual(bom["components"],[])

    def test_project_license_is_not_assumed(self):
        lic=self.load("supply-chain/dependency-license-manifest.json")
        self.assertEqual(lic["project_source"]["license_status"],"NO_LICENSE_FILE")

    def test_supply_chain_hard_gates_closed(self):
        p=self.load("config/supply-chain-policy.json")
        for k,v in p["packaging_and_broker_gates"].items():
            self.assertFalse(v,k)

if __name__=="__main__":
    unittest.main()
