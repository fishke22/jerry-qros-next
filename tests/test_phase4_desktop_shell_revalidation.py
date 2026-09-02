import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase4DesktopShellRevalidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = json.loads(
            (ROOT / "config/phase4-desktop-shell-revalidation.json").read_text(
                encoding="utf-8"
            )
        )

    def test_revalidation_is_anchored_to_current_phase4_design_main(self):
        self.assertEqual(
            self.review["baseline_main_sha"],
            "aa2f149e916e5a3d47114ed2e0d3df6a9f5542ae",
        )
        self.assertEqual(self.review["repository"]["phase4_research_pr"], 23)
        self.assertEqual(self.review["repository"]["phase4_design_pr"], 24)
        self.assertEqual(
            self.review["repository"]["current_gate"], "IMPLEMENTATION_CANDIDATE"
        )

    def test_lean_pin_is_not_changed(self):
        self.assertEqual(
            self.review["lean"]["gitlink"],
            "b692bf4788e8b54fc23bdcb5659666bf055ce89f",
        )
        self.assertFalse(self.review["lean"]["change_authorized"])

    def test_hard_gates_remain_closed(self):
        gates = self.review["hard_gates"]
        self.assertTrue(gates["zero_cost_required"])
        self.assertFalse(gates["package_authorized"])
        self.assertFalse(gates["release_authorized"])
        self.assertFalse(gates["yuanta_integration_authorized"])
        self.assertFalse(gates["live_trading_authorized"])

    def test_node_and_vite_are_not_production_processes(self):
        inv = self.review["architecture_invariants"]
        self.assertFalse(inv["production_node_process_allowed"])
        self.assertFalse(inv["production_vite_process_allowed"])
        self.assertTrue(inv["webview2_child_processes_expected"])

    def test_privileged_frontend_paths_remain_denied(self):
        inv = self.review["architecture_invariants"]
        for key in (
            "remote_webview_content_allowed",
            "arbitrary_network_access_allowed",
            "arbitrary_filesystem_access_allowed",
            "arbitrary_shell_execution_allowed",
            "broker_frontend_access_allowed",
            "credential_frontend_access_allowed",
            "privileged_tauri_plugins_allowed",
            "phase5_workspace_functionality_allowed_in_phase4",
        ):
            self.assertFalse(inv[key], key)

    def test_webview2_version_stays_unknown_until_windows_inventory(self):
        decisions = {x["name"]: x for x in self.review["decisions"]}
        webview = decisions["Microsoft Edge WebView2 Runtime"]
        self.assertEqual(
            webview["current_version"], "UNKNOWN_LOCAL_INVENTORY_REQUIRED"
        )
        self.assertIsNone(webview["candidate_exact_pin"])

    def test_visual_studio_license_boundary_is_fail_closed(self):
        decisions = {x["name"]: x for x in self.review["decisions"]}
        community = decisions["Visual Studio Community 2026"]
        build_tools = decisions["Build Tools for Visual Studio 2026"]
        self.assertEqual(
            community["decision"], "ACCEPT_CURRENT_INDIVIDUAL_USE_SCOPE"
        )
        self.assertTrue(community["license_verified"])
        self.assertEqual(
            build_tools["decision"], "DENY_UNLESS_VALID_LICENSE_BASIS_VERIFIED"
        )
        self.assertFalse(build_tools["license_verified"])

    def test_architecture_is_kept_without_dependency_promotion(self):
        self.assertEqual(
            self.review["decision"],
            "KEEP_TAURI_REACT_ARCHITECTURE_WITH_TOOLCHAIN_LICENSE_HARDENING",
        )
        decisions = {x["name"]: x for x in self.review["decisions"]}
        self.assertEqual(
            decisions["TypeScript"]["decision"],
            "DEFER_ADOPTION_PENDING_EXACT_GRAPH_COMPILE",
        )
        self.assertEqual(
            decisions["Wails v3"]["decision"], "DEFER"
        )
        self.assertEqual(
            decisions["Neutralinojs"]["decision"], "REJECT_PHASE4_FIRST_SLICE"
        )
        self.assertEqual(
            self.review["next_gate"], "PHASE_4_IMPLEMENTATION_CANDIDATE"
        )


if __name__ == "__main__":
    unittest.main()
