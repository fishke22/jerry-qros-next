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
        self.assertEqual(
            cargo["build-dependencies"]["tauri-build"]["version"], "=2.6.3"
        )

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


if __name__ == "__main__":
    unittest.main()
