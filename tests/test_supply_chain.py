import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SupplyChainFoundationTests(unittest.TestCase):
    def load(self,path):
        return json.loads((ROOT/path).read_text(encoding="utf-8"))

    def test_adopted_runtime_matches_sbom_and_lock(self):
        reg=self.load("config/dependency-registry.json")
        runtime=[d for d in reg["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
        self.assertEqual(len(runtime),13)
        bom=self.load("supply-chain/bom.cdx.json")
        purls={c["purl"] for c in bom["components"]}
        lock=(ROOT/"requirements/phase2.lock").read_text(encoding="utf-8")
        for d in runtime:
            self.assertIn(f"pkg:pypi/{d['package_name']}@{d['version_label']}",purls)
            needle=f"{d['package_name']}=="
            if d["package_name"]=="pandera":
                needle="pandera[pyarrow]=="
            self.assertIn(needle,lock)
            for digest in d["artifact_sha256"].values():
                self.assertIn(f"sha256:{digest}",lock)

    def test_only_phase2_runtime_is_introduced(self):
        reg=self.load("config/dependency-registry.json")
        runtime=[d for d in reg["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"]
        self.assertTrue(runtime)
        for d in runtime:
            self.assertEqual(d["phase"],"Phase 2")
            self.assertTrue(d["introduction_authorized"])
            self.assertEqual(d["pin_type"],"PYPI_EXACT_VERSION")

    def test_planned_dependencies_are_denied_until_pinned(self):
        reg=self.load("config/dependency-registry.json")
        planned=[d for d in reg["dependencies"] if d["status"].startswith("PLANNED_")]
        self.assertGreater(len(planned),0)
        for d in planned:
            self.assertEqual(d["version_label"],"UNSPECIFIED")
            self.assertFalse(d["introduction_authorized"])

    def test_project_license_is_not_assumed(self):
        lic=self.load("supply-chain/dependency-license-manifest.json")
        self.assertEqual(lic["project_source"]["license_status"],"NO_LICENSE_FILE")

    def test_sbom_runtime_count_is_truthful(self):
        bom=self.load("supply-chain/bom.cdx.json")
        props={p["name"]:p["value"] for p in bom["metadata"]["component"]["properties"]}
        self.assertEqual(int(props["qros:runtime-component-count"]),len(bom["components"]))
        self.assertEqual(len(bom["components"]),13)

    def test_supply_chain_hard_gates_closed(self):
        p=self.load("config/supply-chain-policy.json")
        for k,v in p["packaging_and_broker_gates"].items():
            self.assertFalse(v,k)

if __name__=="__main__":
    unittest.main()
