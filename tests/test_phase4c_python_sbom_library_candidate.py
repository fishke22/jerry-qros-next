import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4CPythonSbomLibraryCandidateTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (ROOT / "config" / "phase4c-python-sbom-library-candidate.json")
            .read_text(encoding="utf-8")
        )
        self.workflow = (
            ROOT / ".github" / "workflows" / "phase4c-python-sbom-library-research.yml"
        ).read_text(encoding="utf-8")

    def test_exact_candidate_and_existing_python_toolchain(self):
        c = self.policy["candidate"]
        self.assertEqual(c["component"], "cyclonedx-python-lib")
        self.assertEqual(c["version"], "11.12.0")
        self.assertEqual(
            c["source_release_commit"],
            "52cb3c94f023df887ac65a6125bce4d63ab7857e",
        )
        self.assertEqual(
            c["pypi_wheel_sha256"],
            "0e807521a921a5c3cb8ce1153f8a61d29eedfe76a46aac2796b7c6b573391a54",
        )
        self.assertEqual(c["license"], "Apache-2.0")
        self.assertEqual(c["python"], "3.14.7")
        self.assertIn(
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
            self.workflow,
        )

    def test_resolution_is_wheel_only_and_non_executing(self):
        r = self.policy["resolution"]
        self.assertTrue(r["wheel_only"])
        self.assertFalse(r["sdist_allowed"])
        self.assertFalse(r["install_allowed"])
        self.assertFalse(r["package_import_allowed"])
        self.assertFalse(r["build_allowed"])
        self.assertIn("--only-binary=:all:", self.workflow)
        self.assertIn("--require-hashes", self.workflow)
        for forbidden in (
            "pip install",
            "python -m build",
            "setup.py",
            "cyclonedx.model",
            "Bom.from_json(",
            "JsonV1Dot7(",
        ):
            self.assertNotIn(forbidden, self.workflow)

    def test_rejected_dotnet_route_does_not_become_allowed(self):
        rejected = self.policy["rejected_predecessor"]
        self.assertEqual(rejected["status"], "REJECT_ZERO_COST")
        scope = self.policy["scope"]
        self.assertFalse(scope["dependency_adoption_authorized"])
        self.assertFalse(scope["converter_execution_authorized"])
        self.assertFalse(scope["canonical_sbom_1_7_promotion_authorized"])
        self.assertFalse(scope["main_runtime_promotion_authorized"])
        self.assertFalse(scope["production_readiness_authorized"])

    def test_hard_gates_remain_closed(self):
        g = self.policy["hard_gates"]
        self.assertTrue(g["zero_cost_required"])
        self.assertFalse(g["package_authorized"])
        self.assertFalse(g["release_authorized"])
        self.assertFalse(g["yuanta_integration_authorized"])
        self.assertFalse(g["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()
