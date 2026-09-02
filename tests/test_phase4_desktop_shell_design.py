import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4DesktopShellDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads(
            (ROOT / "config/phase4-desktop-shell-design.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(
            (ROOT / "config/dependency-registry.json").read_text(encoding="utf-8")
        )

    def test_only_implementation_candidate_is_authorized(self):
        auth = self.design["authorization"]
        self.assertTrue(auth["implementation_candidate_authorized"])
        self.assertTrue(auth["feature_branch_dependency_resolution_authorized"])
        self.assertTrue(auth["windows_source_build_authorized"])
        self.assertTrue(auth["development_executable_for_testing_authorized"])
        self.assertFalse(auth["dependency_adoption_authorized"])
        self.assertFalse(auth["main_runtime_promotion_authorized"])
        self.assertFalse(auth["package_authorized"])
        self.assertFalse(auth["release_authorized"])
        self.assertFalse(auth["yuanta_integration_authorized"])
        self.assertFalse(auth["live_trading_authorized"])
        self.assertTrue(auth["unknown_is_deny"])

    def test_candidate_is_windows_only_local_static_spa(self):
        target = self.design["target"]
        scope = self.design["candidate_scope"]
        self.assertEqual(target["desktop_os"], "Windows 11")
        self.assertEqual(target["architecture"], "x64")
        self.assertEqual(target["rust_target"], "x86_64-pc-windows-msvc")
        self.assertFalse(target["cross_platform_desktop_targets_authorized"])
        self.assertEqual(scope["frontend_model"], "LOCAL_STATIC_SPA_ONLY")
        self.assertFalse(scope["remote_content_allowed"])
        self.assertFalse(scope["production_outbound_network_required"])
        self.assertFalse(scope["ssr_allowed"])
        self.assertFalse(scope["react_server_components_allowed"])
        self.assertFalse(scope["server_functions_allowed"])
        self.assertFalse(scope["privileged_tauri_plugins_allowed"])

    def test_supply_chain_evidence_is_mandatory_before_adoption(self):
        req = self.design["implementation_candidate_requirements"]
        required_true = [
            "package_json_exact_versions_only",
            "package_lock_required",
            "npm_integrity_evidence_required",
            "npm_audit_required",
            "rust_toolchain_toml_required",
            "cargo_direct_versions_exact_equals_required",
            "cargo_lock_required",
            "cargo_resolved_graph_required",
            "cargo_license_evidence_required",
            "cargo_vulnerability_evidence_required",
            "malicious_crate_deny_validation_required",
            "typescript_7_compile_validation_required",
            "restrictive_csp_required",
            "minimal_tauri_capability_required",
            "windows_msvc_inventory_required",
            "windows_webview2_inventory_required",
            "windows_source_build_smoke_required",
            "antivirus_compatibility_review_required",
            "complete_npm_cargo_sbom_required_before_adoption",
            "complete_license_closure_required_before_adoption",
        ]
        for key in required_true:
            self.assertTrue(req[key], key)
        self.assertFalse(req["known_high_critical_vulnerability_allowed"])
        self.assertFalse(req["missing_audit_evidence_allowed"])
        self.assertFalse(req["remote_capability_urls_allowed"])
        self.assertFalse(req["production_network_endpoint_allowed"])

    def test_typescript_failure_does_not_auto_fallback(self):
        ts = self.design["typescript_7"]
        self.assertEqual(ts["candidate"], "7.0.2")
        self.assertEqual(ts["compatibility"], "UNVERIFIED_PENDING_EXACT_GRAPH_COMPILE")
        self.assertEqual(ts["on_failure"], "DENY_AND_RETURN_TO_DESIGN_REVIEW")
        self.assertFalse(ts["automatic_fallback_allowed"])

    def test_windows_validation_does_not_open_packaging_or_paid_ci(self):
        win = self.design["windows_validation"]
        self.assertTrue(win["standard_public_windows_runner_allowed"])
        self.assertFalse(win["scheduled_windows_runs_allowed"])
        self.assertFalse(win["paid_larger_gpu_runner_allowed"])
        self.assertFalse(win["webview2_redistribution_allowed"])
        self.assertFalse(win["webview2_auto_download_allowed"])
        self.assertFalse(win["msi_vbscript_setup_allowed"])

    def test_deferred_dependencies_remain_deferred(self):
        deferred = set(self.design["deferred_dependencies"])
        for item in {
            "FlexLayout", "Lightweight Charts", "ECharts", "shadcn/ui",
            "TanStack Query", "i18next", "Tauri shell plugin",
            "Tauri fs plugin", "Tauri http plugin", "Tauri updater plugin",
            "Tauri opener plugin", "Tauri process plugin",
        }:
            self.assertIn(item, deferred)

    def test_dependency_registry_still_denies_phase4_adoption(self):
        phase4 = [x for x in self.registry["dependencies"] if x.get("phase") == "Phase 4"]
        self.assertGreaterEqual(len(phase4), 3)
        for item in phase4:
            self.assertEqual(item["status"], "PLANNED_DENY_USE_UNTIL_PINNED")
            self.assertEqual(item["version_label"], "UNSPECIFIED")
            self.assertIsNone(item["revision"])
            self.assertFalse(item["introduction_authorized"])

    def test_promotion_gate_remains_fail_closed(self):
        gate = self.design["promotion_gate"]
        self.assertTrue(gate["implementation_candidate_may_be_built_on_feature_branch"])
        self.assertFalse(gate["dependency_registry_may_be_promoted_to_adopted_before_gate"])
        self.assertTrue(gate["merge_to_main_requires_supply_chain_review"])
        self.assertTrue(gate["merge_to_main_requires_windows_source_build_evidence"])
        self.assertTrue(gate["merge_to_main_requires_no_material_p1_p2_findings"])
        self.assertFalse(gate["production_readiness_claim_allowed"])


if __name__ == "__main__":
    unittest.main()
