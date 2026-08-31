from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from qros_lean import DOTNET_SDK_VERSION,LEAN_REVISION,LEAN_TARGET_FRAMEWORK,LeanInstallation,LeanPinError
class LeanAdapterTests(unittest.TestCase):
    def test_exact_constants(self):
        self.assertEqual(LEAN_REVISION,"b692bf4788e8b54fc23bdcb5659666bf055ce89f");self.assertEqual(LEAN_TARGET_FRAMEWORK,"net10.0");self.assertEqual(DOTNET_SDK_VERSION,"10.0.400")
    def test_missing_launcher_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            i=LeanInstallation(Path(d))
            with patch.object(LeanInstallation,"revision",return_value=LEAN_REVISION):
                with self.assertRaises(LeanPinError):i.verify()
    def test_revision_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Launcher"/"QuantConnect.Lean.Launcher.csproj";p.parent.mkdir();p.write_text("<Project><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>",encoding="utf-8")
            i=LeanInstallation(Path(d))
            with patch.object(LeanInstallation,"revision",return_value="0"*40):
                with self.assertRaises(LeanPinError):i.verify()
    def test_build_command_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"Launcher"/"QuantConnect.Lean.Launcher.csproj";p.parent.mkdir();p.write_text("<Project><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>",encoding="utf-8")
            i=LeanInstallation(Path(d))
            with patch.object(LeanInstallation,"revision",return_value=LEAN_REVISION):cmd=i.build_command()
            self.assertEqual(cmd[:2],["dotnet","build"]);self.assertIn("Release",cmd);self.assertIn("-p:ContinuousIntegrationBuild=true",cmd)
if __name__=="__main__":unittest.main()
