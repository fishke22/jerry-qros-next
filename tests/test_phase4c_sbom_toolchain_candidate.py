import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4CSbomToolchainCandidateTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (ROOT / "config" / "phase4c-sbom-toolchain-candidate.json").read_text(
                encoding="utf-8"
            )
        )
        self.workflow = (
            ROOT / ".github" / "workflows" / "phase4c-sbom-toolchain-research.yml"
        ).read_text(encoding="utf-8")

    def test_restore_inventory_scope_only(self):
        self.assertEqual(self.policy["status"], "RESTORE_INVENTORY_ONLY")
        scope = self.policy["scope"]
        self.assertTrue(scope["restore_and_inventory_authorized"])
        for key in (
            "build_cli_authorized",
            "execute_cli_authorized",
            "sbom_conversion_authorized",
            "permanent_tool_adoption_authorized",
            "canonical_sbom_1_7_promotion_authorized",
            "dependency_adoption_authorized",
            "main_runtime_promotion_authorized",
            "production_readiness_authorized",
        ):
            self.assertFalse(scope[key])

    def test_exact_source_and_dotnet_pins(self):
        cli = self.policy["cyclonedx_cli"]
        self.assertEqual(cli["version"], "0.33.1")
        self.assertEqual(
            cli["source_revision"],
            "b3cfa4b0edc356dad07e0b6e7ab6da0a94af0246",
        )
        self.assertEqual(self.policy["dotnet"]["sdk"], "10.0.400")
        self.assertEqual(
            self.policy["dotnet"]["setup_action_revision"],
            "a98b56852c35b8e3190ac28c8c2271da59106c68",
        )
        self.assertIn(cli["source_revision"], self.workflow)
        self.assertIn("dotnet-version: \"10.0.400\"", self.workflow)

    def test_restore_is_locked_audited_and_single_source(self):
        restore = self.policy["restore"]
        self.assertTrue(restore["generate_qros_lock_evidence"])
        self.assertTrue(restore["locked_restore_required"])
        self.assertTrue(restore["nuget_audit"])
        self.assertEqual(restore["nuget_audit_mode"], "all")
        self.assertEqual(restore["nuget_audit_level"], "low")
        self.assertIn("--use-lock-file", self.workflow)
        self.assertIn("--locked-mode", self.workflow)
        self.assertIn("-p:NuGetAuditMode=all", self.workflow)
        self.assertIn("-p:NuGetAuditLevel=low", self.workflow)
        self.assertIn("https://api.nuget.org/v3/index.json", self.workflow)

    def test_no_build_execute_or_conversion_command(self):
        for forbidden in (
            "dotnet build",
            "dotnet run",
            "dotnet publish",
            "cyclonedx convert",
            "cyclonedx validate",
            "docker ",
            "Invoke-WebRequest",
            "curl ",
            "wget ",
        ):
            self.assertNotIn(forbidden, self.workflow)
        self.assertIn("QROS_PHASE4C_CLI_BUILD_EXECUTION=NOT_PERFORMED", self.workflow)
        self.assertIn("QROS_PHASE4C_CONVERSION=NOT_PERFORMED", self.workflow)

    def test_restore_time_execution_surface_is_denied(self):
        source_eval = self.policy["source_evaluation"]
        self.assertFalse(source_eval["directory_build_targets_allowed"])
        self.assertFalse(source_eval["exec_task_allowed"])
        self.assertFalse(source_eval["using_task_allowed"])
        self.assertFalse(source_eval["restore_hook_allowed"])
        self.assertIn("Restore-time/custom MSBuild execution surface found", self.workflow)
        self.assertIn("ET.parse(p)", self.workflow)
        self.assertIn('{"Exec", "UsingTask"}', self.workflow)
        self.assertIn("RestoreAdditionalProjectSources", self.workflow)
        self.assertIn("RemoteImport", self.workflow)

    def test_hard_gates_remain_closed(self):
        gates = self.policy["hard_gates"]
        self.assertTrue(gates["zero_cost_required"])
        self.assertFalse(gates["package_authorized"])
        self.assertFalse(gates["release_authorized"])
        self.assertFalse(gates["yuanta_integration_authorized"])
        self.assertFalse(gates["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()
