import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SupplyChainFoundationTests(unittest.TestCase):
 def load(self,p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
 def test_python_runtime_matches_lock(self):
  r=[d for d in self.load("config/dependency-registry.json")["dependencies"] if d["runtime_scope"]=="RUNTIME" and d["status"]=="ADOPTED"];self.assertEqual(len(r),13)
 def test_lean_exact_gitlink(self):
  d=next(x for x in self.load("config/dependency-registry.json")["dependencies"] if x["dependency_id"]=="quantconnect-lean");self.assertEqual(d["revision"],"b692bf4788e8b54fc23bdcb5659666bf055ce89f")
  t=subprocess.check_output(["git","ls-tree","HEAD","external/lean"],cwd=ROOT,text=True);self.assertIn("160000 commit b692bf4788e8b54fc23bdcb5659666bf055ce89f",t)
 def test_dotnet_exact(self):
  g=self.load("global.json")["sdk"];self.assertEqual(g["version"],"10.0.400");self.assertEqual(g["rollForward"],"disable")
 def test_sbom_count(self):
  b=self.load("supply-chain/bom.cdx.json");self.assertEqual(len(b["components"]),14)
 def test_future_planned_denied(self):
  for d in [x for x in self.load("config/dependency-registry.json")["dependencies"] if x["status"].startswith("PLANNED_")]:self.assertFalse(d["introduction_authorized"])
 def test_project_license_not_assumed(self):self.assertEqual(self.load("supply-chain/dependency-license-manifest.json")["project_source"]["license_status"],"NO_LICENSE_FILE")
 def test_hard_gates_closed(self):
  for v in self.load("config/supply-chain-policy.json")["packaging_and_broker_gates"].values():self.assertFalse(v)
if __name__=="__main__":unittest.main()
