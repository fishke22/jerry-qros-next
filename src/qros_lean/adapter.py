from __future__ import annotations
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

LEAN_REVISION="b692bf4788e8b54fc23bdcb5659666bf055ce89f"
LEAN_TARGET_FRAMEWORK="net10.0"
DOTNET_SDK_VERSION="10.0.400"
LAUNCHER_PROJECT=Path("Launcher/QuantConnect.Lean.Launcher.csproj")
LAUNCHER_DLL=Path("Launcher/bin/Release/QuantConnect.Lean.Launcher.dll")

class LeanPinError(RuntimeError): pass

@dataclass(frozen=True)
class LeanProbe:
    revision:str
    target_framework:str
    launcher_project:Path
    launcher_dll:Path

class LeanInstallation:
    def __init__(self,root:Path): self.root=Path(root)
    def revision(self)->str:
        try:return subprocess.check_output(["git","-C",str(self.root),"rev-parse","HEAD"],text=True,stderr=subprocess.PIPE).strip()
        except (subprocess.CalledProcessError,FileNotFoundError) as exc: raise LeanPinError("LEAN git revision is unavailable") from exc
    def target_framework(self)->str:
        project=self.root/LAUNCHER_PROJECT
        if not project.is_file(): raise LeanPinError("LEAN Launcher project is missing")
        value=ET.parse(project).getroot().findtext(".//TargetFramework")
        if not value: raise LeanPinError("LEAN Launcher TargetFramework is unknown")
        return value.strip()
    def verify(self)->LeanProbe:
        revision=self.revision()
        if revision!=LEAN_REVISION: raise LeanPinError(f"LEAN revision mismatch: {revision}")
        framework=self.target_framework()
        if framework!=LEAN_TARGET_FRAMEWORK: raise LeanPinError(f"LEAN target framework mismatch: {framework}")
        return LeanProbe(revision,framework,self.root/LAUNCHER_PROJECT,self.root/LAUNCHER_DLL)
    def build_command(self)->list[str]:
        self.verify()
        return ["dotnet","build",str(self.root/LAUNCHER_PROJECT),"--configuration","Release","--nologo","-p:ContinuousIntegrationBuild=true"]
    def launcher_command(self)->list[str]:
        probe=self.verify()
        if not probe.launcher_dll.is_file(): raise LeanPinError("LEAN Launcher is not built")
        return ["dotnet",str(probe.launcher_dll)]
