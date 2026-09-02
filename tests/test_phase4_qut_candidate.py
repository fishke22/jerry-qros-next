import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUT = ROOT / "apps" / "qut"


class Phase4QutCandidateTests(unittest.TestCase):
    def test_exact_frontend_versions_and_minimal_dependencies(self):
        package = json.loads((QUT / "package.json").read_text(encoding="utf-8"))
        self.assertTrue(package["private"])
        self.assertEqual(package["packageManager"], "npm@11.19.0")
        self.assertEqual(package["engines"]["node"], "=24.20.0")
        self.assertEqual(
            package["dependencies"],
            {
                "@tauri-apps/api": "2.11.1",
                "react": "19.2.8",
                "react-dom": "19.2.8",
            },
        )
        self.assertEqual(
            package["devDependencies"],
            {
                "@tauri-apps/cli": "2.11.4",
                "@types/react": "19.2.18",
                "@types/react-dom": "19.2.5",
                "@vitejs/plugin-react": "6.1.1",
                "typescript": "7.0.2",
                "vite": "8.2.2",
            },
        )
        for group in ("dependencies", "devDependencies"):
            for version in package[group].values():
                self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_exact_rust_toolchain_and_tauri_crates(self):
        toolchain = tomllib.loads(
            (QUT / "rust-toolchain.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(toolchain["toolchain"]["channel"], "1.98.0")
        self.assertEqual(toolchain["toolchain"]["profile"], "minimal")

        cargo = tomllib.loads(
            (QUT / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(cargo["dependencies"]["tauri"]["version"], "=2.11.5")
        self.assertFalse(cargo["dependencies"]["tauri"]["default-features"])
        self.assertEqual(cargo["dependencies"]["tauri"]["features"], ["wry"])
        self.assertEqual(
            cargo["build-dependencies"]["tauri-build"]["version"], "=2.6.3"
        )
        self.assertFalse(
            cargo["build-dependencies"]["tauri-build"]["default-features"]
        )
        self.assertFalse(cargo["package"]["publish"])

    def test_vite_is_loopback_only(self):
        vite = (QUT / "vite.config.ts").read_text(encoding="utf-8")
        self.assertIn('host: "127.0.0.1"', vite)
        self.assertIn("strictPort: true", vite)
        self.assertNotIn('host: "0.0.0.0"', vite)
        self.assertNotIn("TAURI_", vite)

    def test_tauri_config_keeps_package_and_network_boundaries_closed(self):
        conf = json.loads(
            (QUT / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")
        )
        self.assertFalse(conf["bundle"]["active"])
        self.assertEqual(conf["build"]["devUrl"], "http://127.0.0.1:1420")
        csp = conf["app"]["security"]["csp"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("connect-src ipc: http://ipc.localhost", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertNotIn("https:", csp)
        self.assertNotIn("wss:", csp)

    def test_capability_is_local_and_single_command(self):
        capability = json.loads(
            (QUT / "src-tauri" / "capabilities" / "main.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(capability["windows"], ["main"])
        self.assertEqual(capability["permissions"], ["allow-get-shell-status"])
        self.assertNotIn("remote", capability)

        permission = (
            QUT / "src-tauri" / "permissions" / "qut.toml"
        ).read_text(encoding="utf-8")
        self.assertIn('commands.allow = ["get_shell_status"]', permission)

    def test_no_privileged_tauri_plugins_or_phase5_runtime(self):
        cargo = (QUT / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
        for forbidden in (
            "tauri-plugin-shell",
            "tauri-plugin-fs",
            "tauri-plugin-http",
            "tauri-plugin-updater",
            "tauri-plugin-opener",
            "tauri-plugin-process",
        ):
            self.assertNotIn(forbidden, cargo)

        app = (QUT / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("Yuanta integration", app)
        self.assertIn("Disabled / Not Authorized", app)
        self.assertIn("Live Trading", app)
        self.assertIn("Packaging", app)
        self.assertIn("Release", app)
        self.assertNotRegex(app, re.compile(r"https?://"))

    def test_rust_command_has_no_input_or_privileged_io(self):
        lib = (QUT / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")
        self.assertIn("fn get_shell_status() -> String", lib)
        for forbidden in (
            "std::fs",
            "std::process",
            "Command::new",
            "reqwest",
            "TcpStream",
            "UdpSocket",
        ):
            self.assertNotIn(forbidden, lib)

    def test_rustsec_dispositions_are_exact_candidate_only_and_fail_closed(self):
        policy = json.loads(
            (ROOT / "config" / "phase4-qut-rustsec-dispositions.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(policy["target"], "x86_64-pc-windows-msvc")
        self.assertEqual(
            policy["status"], "CANDIDATE_ONLY_NOT_ADOPTION_AUTHORIZATION"
        )
        rules = policy["rules"]
        self.assertFalse(rules["windows_vulnerability_allowed"])
        self.assertFalse(rules["windows_unsound_warning_allowed"])
        self.assertFalse(rules["unknown_warning_allowed"])
        self.assertFalse(rules["unlisted_unmaintained_warning_allowed"])
        expected = {
            ("RUSTSEC-2025-0075", "unic-char-range", "0.9.0"),
            ("RUSTSEC-2025-0080", "unic-common", "0.9.0"),
            ("RUSTSEC-2025-0081", "unic-char-property", "0.9.0"),
            ("RUSTSEC-2025-0100", "unic-ucd-ident", "0.9.0"),
            ("RUSTSEC-2025-0098", "unic-ucd-version", "0.9.0"),
        }
        actual = {
            (x["advisory"], x["crate"], x["version"])
            for x in policy["temporary_unmaintained_dispositions"]
        }
        self.assertEqual(actual, expected)
        self.assertTrue(
            all(
                x["classification"] == "unmaintained" and x["patched_version"] is None
                for x in policy["temporary_unmaintained_dispositions"]
            )
        )
        scope = policy["acceptance_scope"]
        self.assertTrue(scope["candidate_ci_may_pass_with_exact_list_only"])
        self.assertFalse(scope["dependency_registry_promotion_authorized"])
        self.assertFalse(scope["main_runtime_promotion_authorized"])
        self.assertFalse(scope["production_readiness_authorized"])
        self.assertTrue(scope["must_revalidate_each_audit_run"])

    def test_candidate_ci_requires_webview2_inventory_and_no_packaging(self):
        workflow = (
            ROOT / ".github" / "workflows" / "phase4-qut-candidate.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("QROS_WEBVIEW2_RUNTIME_VERSION", workflow)
        self.assertIn("F3017226-FE2A-4295-8BDF-00C3A9A7E4C5", workflow)
        self.assertIn("WebView2 Evergreen Runtime registry inventory missing", workflow)
        self.assertIn("bundle.active=false", (QUT / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8").replace('"bundle": {\n    "active": false\n  }', "bundle.active=false"))
        self.assertNotIn("cargo tauri build", workflow)
        self.assertNotIn("npm run tauri build", workflow)
        self.assertIn("Parse local Windows validation harness without executing it", workflow)
        self.assertIn("[System.Management.Automation.Language.Parser]::ParseFile", workflow)


    def test_windows11_local_validation_harness_is_read_only_and_fail_closed(self):
        script = (
            ROOT / "scripts" / "phase4" / "windows11-local-validation.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("Get-CimInstance -ClassName Win32_OperatingSystem", script)
        self.assertIn("Microsoft.VisualStudio.Component.VC.Tools.x86.x64", script)
        self.assertIn("Get-MpComputerStatus", script)
        self.assertIn('root/SecurityCenter2', script)
        self.assertIn("F3017226-FE2A-4295-8BDF-00C3A9A7E4C5", script)
        self.assertIn("local-only\\phase4\\windows11-validation.json", script)
        self.assertIn("npm", script)
        self.assertIn('"ci", "--ignore-scripts", "--no-audit", "--no-fund"', script)
        self.assertIn('"build",', script)
        self.assertIn('"--locked",', script)
        self.assertIn(
            "e8c023a29dbbbc9fbaff86769998e05635ab140594eb53caff5bd082624ee4b8",
            script,
        )
        self.assertIn(
            "c9abfa64e57be2dd18efa91d8ae4abf43944bdbae75af94555ff28daa7601adb",
            script,
        )
        for forbidden in (
            "cargo tauri build",
            "npm run tauri build",
            "Invoke-WebRequest",
            "Start-BitsTransfer",
            "Start-Process",
            "Set-MpPreference",
            "Add-MpPreference",
            "Remove-MpPreference",
            "Start-MpScan",
            "Update-MpSignature",
            "pathToSignedProductExe",
            "COMPUTERNAME",
            "USERNAME",
            "YUANTA_AUTOPILOT",
        ):
            self.assertNotIn(forbidden, script)
        self.assertIn("package_authorized = $false", script)
        self.assertIn("release_authorized = $false", script)
        self.assertIn("yuanta_integration_authorized = $false", script)
        self.assertIn("live_trading_authorized = $false", script)
        self.assertIn("broad_filesystem_scan_performed = $false", script)
        self.assertIn("Microsoft.VisualStudio.Product.Community", script)
        self.assertIn("COMMUNITY_INDIVIDUAL_SCOPE_CANDIDATE", script)
        self.assertIn("Microsoft.VCToolsVersion.default.txt", script)
        self.assertIn("Hostx64\\x64\\cl.exe", script)
        self.assertIn('Invoke-NativeText -FilePath "rustc" -ArgumentList @("-Vv")', script)
        self.assertIn('x86_64-pc-windows-msvc', script)
        self.assertIn("toolchain = $toolchain", script)
        self.assertNotIn("-ExecutionPolicy Bypass", script)

    def test_phase4_local_build_network_endpoints_are_explicit(self):
        endpoints = (
            ROOT / "docs" / "security" / "NETWORK_ENDPOINTS.md"
        ).read_text(encoding="utf-8")
        self.assertIn("registry.npmjs.org", endpoints)
        self.assertIn("index.crates.io", endpoints)
        self.assertIn("static.crates.io", endpoints)
        self.assertIn("inventory-only validation mode performs no dependency bootstrap", endpoints)
        self.assertIn("Packaging, updater, signing, release, Yuanta and broker endpoints remain absent", endpoints)

    def test_remote_desktop_cost_unknown_is_denied(self):
        evidence = (
            ROOT
            / "docs"
            / "source-evidence"
            / "phase-4b-windows11-local-validation-gate.md"
        ).read_text(encoding="utf-8")
        self.assertIn("UNVERIFIED_ZERO_COST_REMOTE_SERVICE = DENY", evidence)
        self.assertIn("hosted/cloud relay", evidence)
        self.assertIn("proprietary", evidence)
        self.assertIn("local DesktopCommanderMCP implementation is open source under MIT", evidence)
        self.assertIn("WINDOWS_11_PHYSICAL_TARGET = UNKNOWN / DENY", evidence)


    def test_windows11_runner_and_execution_policy_boundaries(self):
        evidence = (
            ROOT
            / "docs"
            / "source-evidence"
            / "phase-4b-windows11-local-validation-gate.md"
        ).read_text(encoding="utf-8")
        runbook = (
            ROOT
            / "docs"
            / "runbooks"
            / "phase4-windows11-local-validation.md"
        ).read_text(encoding="utf-8")
        plan = (
            ROOT
            / "docs"
            / "validation"
            / "PHASE4_WINDOWS11_LOCAL_VALIDATION_PLAN.md"
        ).read_text(encoding="utf-8")
        self.assertIn("SELF_HOSTED_RUNNER_MONETARY_COST = ZERO", evidence)
        self.assertIn(
            "SELF_HOSTED_RUNNER_ON_PUBLIC_CANONICAL_REPO = REJECT", evidence
        )
        self.assertNotIn("-ExecutionPolicy Bypass -File", runbook)
        self.assertIn("do not use `-ExecutionPolicy Bypass`", runbook)
        self.assertIn("MANUAL_LOCAL_HARNESS = ACCEPT_FOR_VALIDATION_ONLY", plan)
        self.assertIn(
            "SELF_HOSTED_RUNNER_ON_PUBLIC_CANONICAL_REPO = REJECT", plan
        )
        self.assertIn("PHASE4_WINDOWS11_RUNTIME_SMOKE = UNKNOWN / DENY", plan)


if __name__ == "__main__":
    unittest.main()
