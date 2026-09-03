import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4CPythonInstallCandidateTests(unittest.TestCase):
    def setUp(self):
        self.policy=json.loads(
            (ROOT / "config" / "phase4c-python-sbom-install-candidate.json")
            .read_text(encoding="utf-8")
        )
        self.workflow=(
            ROOT / ".github" / "workflows" / "phase4c-python-sbom-install-candidate.yml"
        ).read_text(encoding="utf-8")

    def test_parent_gates_are_required(self):
        p=self.policy["prerequisites"]
        self.assertEqual(
            p["license_gate"],
            "PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY",
        )
        self.assertEqual(
            p["zero_cost_gate"],
            "PASS_FOR_CANDIDATE_INSTALL_TEST_ONLY",
        )
        self.assertEqual(
            p["pypi_vulnerability_gate"],
            "PASS_EXACT_PYPI_RELEASE_JSON",
        )
        self.assertEqual(p["pypi_yanked_gate"], "PASS")

    def test_install_is_exact_hash_locked_and_offline(self):
        i=self.policy["install_boundary"]
        self.assertTrue(i["isolated_venv_required"])
        self.assertTrue(i["no_index_during_install"])
        self.assertTrue(i["no_deps_during_install"])
        self.assertTrue(i["require_hashes"])
        self.assertFalse(i["pth_files_allowed"])
        self.assertFalse(i["unlisted_wheel_data_scripts_allowed"])\n        self.assertEqual(len(i["allowed_wheel_data_scripts"]), 1)\n        allowed=i["allowed_wheel_data_scripts"][0]\n        self.assertEqual(allowed["path"], "jsonpointer-3.1.1.data/scripts/jsonpointer")\n        self.assertEqual(\n            allowed["sha256"],\n            "4c9bda8829e436ce6c732194421f645240695bf647a75eb210f17256215f7b22",\n        )\n        self.assertEqual(\n            allowed["upstream_source_sha256"],\n            "0922c792b58faecab05e9010713eb5345b964848abeecd62d901a0f10ff1a0c6",\n        )\n        self.assertIn("ONLY_SHEBANG_CHANGED", allowed["wheel_transformation"])\n        self.assertIn("QROS_PHASE4C_WHEEL_DATA_SCRIPTS_EXACT_ALLOWLIST=PASS", self.workflow)
        self.assertIn("--no-index", self.workflow)
        self.assertIn("--no-deps", self.workflow)
        self.assertIn("--require-hashes", self.workflow)
        self.assertIn("python -m venv", self.workflow)

    def test_import_is_limited_and_ambient_capabilities_denied(self):
        i=self.policy["import_boundary"]
        self.assertTrue(i["empty_environment_required"])
        self.assertTrue(i["isolated_python_mode_required"])
        self.assertFalse(i["repo_cwd_allowed"])
        self.assertFalse(i["socket_operations_allowed"])
        self.assertFalse(i["subprocess_operations_allowed"])
        self.assertIn("env -i", self.workflow)
        self.assertIn("socket.socket=denied", self.workflow)
        self.assertIn("subprocess.Popen=denied", self.workflow)
        self.assertIn('"$vpy" -I', self.workflow)

    def test_conversion_calls_remain_absent(self):
        self.assertNotIn("Bom.from_json(", self.workflow)
        self.assertNotIn("JsonV1Dot7(", self.workflow)
        self.assertNotIn("validate_str(", self.workflow)
        self.assertIn(
            "QROS_PHASE4C_BOM_FROM_JSON_EXECUTION=NOT_PERFORMED",
            self.workflow,
        )
        self.assertIn(
            "QROS_PHASE4C_JSON_V1_7_GENERATION=NOT_PERFORMED",
            self.workflow,
        )

    def test_hard_gates_and_promotion_remain_closed(self):
        s=self.policy["scope"]
        self.assertTrue(s["candidate_install_authorized"])
        self.assertTrue(s["candidate_import_authorized"])
        for key in (
            "converter_execution_authorized",
            "semantic_fidelity_test_authorized",
            "permanent_tool_adoption_authorized",
            "dependency_registry_promotion_authorized",
            "canonical_sbom_1_7_promotion_authorized",
            "main_runtime_promotion_authorized",
            "production_readiness_authorized",
        ):
            self.assertFalse(s[key])
        g=self.policy["hard_gates"]
        self.assertTrue(g["zero_cost_required"])
        self.assertFalse(g["package_authorized"])
        self.assertFalse(g["release_authorized"])
        self.assertFalse(g["yuanta_integration_authorized"])
        self.assertFalse(g["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()
