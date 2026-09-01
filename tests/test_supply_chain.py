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
 def test_sbom_count(self):self.assertEqual(len(self.load("supply-chain/bom.cdx.json")["components"]),14)
 def test_phase3d_patched_lean_evidence(self):
  g=self.load("supply-chain/lean/launcher-patched-nuget-graph.json");self.assertEqual(g["package_count"],55);self.assertEqual(g["project_count"],19)
  b=self.load("supply-chain/lean/launcher-patched-bom.cdx.json");p={x["purl"] for x in b["components"]};self.assertEqual(len(b["components"]),55);self.assertIn("pkg:nuget/ProDotNetZip@1.20.0",p);self.assertNotIn("pkg:nuget/DotNetZip@1.16.0",p);self.assertFalse(any(x.startswith("pkg:nuget/NetMQ@") for x in p))
  d=self.load("config/lean-nuget-license-dispositions.json");self.assertEqual(len(d["dispositions"]),11);self.assertTrue(all(x["review_status"]=="ACCEPTED" for x in d["dispositions"]))
 def test_phase3d_runtime_overlay_is_accepted_but_release_closed(self):
  d=next(x for x in self.load("config/dependency-registry.json")["dependencies"] if x["dependency_id"]=="quantconnect-lean");self.assertTrue(d["runtime_promotion_allowed"]);self.assertEqual(d["runtime_promotion_scope"],"LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH");self.assertFalse(d["unpatched_upstream_runtime_allowed"])
  p=self.load("supply-chain/provenance-manifest.json")["quant_engine_runtime_overlay"];self.assertEqual(p["status"],"ACCEPTED_PHASE3D_LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY");self.assertFalse(p["package_authorized"]);self.assertFalse(p["release_authorized"])
 def test_phase3_merge_closure_and_build_environment(self):
  e=self.load("supply-chain/build-environment.json");q=e["quant_engine"];self.assertEqual(q["status"],"ACCEPTED_PHASE3D_PATCHED_LOCAL_RESEARCH_RUNTIME");self.assertTrue(q["runtime_promotion_allowed"]);self.assertFalse(q["baseline_unpatched_upstream_runtime_allowed"]);self.assertEqual(q["synthetic_backtest"]["status"],"ACCEPTED_LOCAL_RESEARCH_BACKTEST_PHASE3D_PATCH_ONLY")
  c=e["phase3_merge_closure"];self.assertEqual(c["pr"],13);self.assertEqual(c["integration_commit"],"744b53c18ab433346ab01fb26d35c55e5633ba43");self.assertTrue(c["tree_equivalent"]);self.assertEqual(c["accepted_tree"],c["integration_tree"]);self.assertEqual(subprocess.check_output(["git","rev-parse",c["accepted_head"]+"^{tree}"],cwd=ROOT,text=True).strip(),c["accepted_tree"]);self.assertEqual(subprocess.check_output(["git","rev-parse",c["integration_commit"]+"^{tree}"],cwd=ROOT,text=True).strip(),c["integration_tree"])
 def test_phase3e_hardening_closure_is_git_verified(self):
  e=self.load("supply-chain/build-environment.json");h=e["phase3e_hardening_closure"];self.assertEqual(h["status"],"ACCEPTED_MERGED_LOCAL_RESEARCH_BACKTEST_HARDENING_ONLY");self.assertEqual(h["accepted_head_evidence_ref"],"refs/heads/evidence/phase-3e-accepted-head");self.assertTrue(h["tree_equivalent"]);self.assertEqual(h["accepted_tree"],h["integration_tree"]);self.assertEqual(subprocess.check_output(["git","rev-parse","refs/remotes/origin/evidence/phase-3e-accepted-head"],cwd=ROOT,text=True).strip(),h["accepted_head"]);self.assertEqual(subprocess.check_output(["git","rev-parse","refs/remotes/origin/evidence/phase-3e-accepted-head^{tree}"],cwd=ROOT,text=True).strip(),h["accepted_tree"]);self.assertEqual(subprocess.check_output(["git","rev-parse",h["integration_commit"]+"^{tree}"],cwd=ROOT,text=True).strip(),h["integration_tree"]);self.assertEqual(h["runtime_result_contract"],"lean-backtest-result/v2");self.assertEqual(h["runtime_assembly_count"],191)
 def test_future_planned_denied(self):
  for d in [x for x in self.load("config/dependency-registry.json")["dependencies"] if x["status"].startswith("PLANNED_")]:self.assertFalse(d["introduction_authorized"])
 def test_project_license_not_assumed(self):self.assertEqual(self.load("supply-chain/dependency-license-manifest.json")["project_source"]["license_status"],"NO_LICENSE_FILE")
 def test_hard_gates_closed(self):
  for v in self.load("config/supply-chain-policy.json")["packaging_and_broker_gates"].values():self.assertFalse(v)
if __name__=="__main__":unittest.main()
