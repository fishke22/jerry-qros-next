import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4DesktopShellResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.research = json.loads(
            (ROOT / "config/phase4-desktop-shell-research.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(
            (ROOT / "config/dependency-registry.json").read_text(encoding="utf-8")
        )

    def test_research_does_not_authorize_implementation_or_hard_gates(self):
        auth = self.research["authorization"]
        self.assertFalse(auth["implementation_authorized"])
        self.assertFalse(auth["dependency_introduction_authorized"])
        self.assertFalse(auth["package_authorized"])
        self.assertFalse(auth["release_authorized"])
        self.assertFalse(auth["yuanta_integration_authorized"])
        self.assertFalse(auth["live_trading_authorized"])
        self.assertTrue(auth["unknown_is_deny"])

    def test_windows_target_is_exact_and_cross_platform_is_not_authorized(self):
        target = self.research["target"]
        self.assertEqual(target["desktop_os"], "Windows 11")
        self.assertEqual(target["architecture"], "x64")
        self.assertEqual(target["rust_target"], "x86_64-pc-windows-msvc")
        self.assertFalse(target["cross_platform_desktop_targets_authorized"])

    def test_all_component_and_toolchain_candidates_remain_denied(self):
        for item in self.research["candidate_components"]:
            self.assertFalse(item["use_authorized"], item["id"])
        for item in self.research["toolchain_candidates"]:
            self.assertFalse(item["use_authorized"], item["id"])

    def test_webview2_is_system_evergreen_and_not_redistributed(self):
        webview = next(
            item for item in self.research["toolchain_candidates"]
            if item["id"] == "webview2"
        )
        self.assertEqual(webview["distribution"], "EVERGREEN_SYSTEM_RUNTIME")
        self.assertFalse(webview["redistribute"])
        self.assertFalse(webview["exact_pin_possible"])
        self.assertEqual(
            self.research["security_controls"]["webview2"]["missing_runtime_action"],
            "FAIL_CLOSED_WITH_USER_VISIBLE_ERROR",
        )

    def test_remote_content_network_and_privileged_plugins_are_denied(self):
        design = self.research["design_candidate"]
        self.assertFalse(design["remote_content_allowed"])
        self.assertFalse(design["ssr_allowed"])
        self.assertFalse(design["react_server_components_allowed"])
        self.assertFalse(design["server_functions_allowed"])
        self.assertFalse(design["outbound_network_required"])
        self.assertFalse(design["auto_download_or_update_allowed"])
        self.assertFalse(design["plugin_introduction_allowed"])
        self.assertTrue(design["vite_loopback_only"])
        self.assertTrue(design["vite_strict_port"])
        self.assertFalse(design["vite_network_host_allowed"])
        self.assertFalse(design["broad_tauri_env_prefix_allowed"])

        security = self.research["security_controls"]
        self.assertEqual(security["remote_capability_urls"], [])
        self.assertEqual(
            set(security["forbidden_tauri_plugins"]),
            {"shell", "fs", "http", "updater", "opener", "process"},
        )

    def test_known_malicious_rust_supply_chain_entries_are_denied(self):
        deny = {
            (entry["crate"], tuple(entry["versions"]))
            for entry in self.research["rust_supply_chain_deny"]
        }
        expected = {
            ("arrayref", ("0.3.10",)),
            ("append-only-vec", ("0.1.9",)),
            ("internment", ("0.8.7",)),
            ("proc-macro1", ("*",)),
            ("proc-macro-en", ("*",)),
            ("aovine", ("*",)),
            ("arone", ("*",)),
            ("aronenao", ("*",)),
            ("tinymember", ("*",)),
        }
        self.assertEqual(deny, expected)

    def test_typescript_7_is_candidate_only_and_requires_compile_validation(self):
        typescript = next(
            item for item in self.research["candidate_components"]
            if item["id"] == "typescript"
        )
        self.assertEqual(typescript["version"], "7.0.2")
        self.assertFalse(typescript["use_authorized"])
        self.assertTrue(typescript["compile_validation_required"])
        self.assertEqual(
            typescript["compatibility_status"],
            "UNVERIFIED_FOR_QROS_TAURI_REACT_BUILD",
        )

    def test_deferred_ui_and_tauri_plugins_remain_deferred(self):
        deferred = set(self.research["deferred_dependencies"])
        required = {
            "FlexLayout",
            "Lightweight Charts",
            "ECharts",
            "shadcn/ui",
            "TanStack Query",
            "i18next",
            "Tauri shell plugin",
            "Tauri fs plugin",
            "Tauri http plugin",
            "Tauri updater plugin",
            "Tauri opener plugin",
            "Tauri process plugin",
        }
        self.assertTrue(required.issubset(deferred))

    def test_phase4_dependency_registry_is_unchanged_planned_deny(self):
        phase4 = [
            item for item in self.registry["dependencies"]
            if item.get("phase") == "Phase 4"
        ]
        self.assertGreaterEqual(len(phase4), 3)
        for item in phase4:
            self.assertEqual(item["status"], "PLANNED_DENY_USE_UNTIL_PINNED")
            self.assertEqual(item["version_label"], "UNSPECIFIED")
            self.assertIsNone(item["revision"])
            self.assertFalse(item["introduction_authorized"])


if __name__ == "__main__":
    unittest.main()
