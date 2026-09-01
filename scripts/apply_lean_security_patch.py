from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "external" / "lean"
EXPECTED_LEAN = "b692bf4788e8b54fc23bdcb5659666bf055ce89f"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    require(old in text, f"expected patch anchor missing: {path}")
    require(text.count(old) == 1, f"patch anchor is not unique: {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> int:
    head = subprocess.check_output(
        ["git", "-C", str(LEAN), "rev-parse", "HEAD"], text=True
    ).strip()
    require(head == EXPECTED_LEAN, f"LEAN revision drift: {head}")

    compression = LEAN / "Compression" / "QuantConnect.Compression.csproj"
    messaging = LEAN / "Messaging" / "QuantConnect.Messaging.csproj"

    replace_exact(
        compression,
        '    <PackageReference Include="DotNetZip" Version="1.16.0" />',
        '    <PackageReference Include="ProDotNetZip" Version="1.20.0" />',
    )
    replace_exact(
        messaging,
        '    <PackageReference Include="NetMQ" Version="4.0.1.6" />\n',
        '',
    )
    replace_exact(
        messaging,
        '  <ItemGroup>\n    <Compile Include="..\\Common\\Properties\\SharedAssemblyInfo.cs" Link="Properties\\SharedAssemblyInfo.cs" />\n  </ItemGroup>',
        '  <ItemGroup>\n    <Compile Remove="StreamingMessageHandler.cs" />\n    <Compile Include="..\\Common\\Properties\\SharedAssemblyInfo.cs" Link="Properties\\SharedAssemblyInfo.cs" />\n  </ItemGroup>',
    )

    compression_text = compression.read_text(encoding="utf-8")
    messaging_text = messaging.read_text(encoding="utf-8")
    require("DotNetZip\" Version=\"1.16.0" not in compression_text, "DotNetZip remained")
    require('ProDotNetZip" Version="1.20.0' in compression_text, "ProDotNetZip missing")
    require("NetMQ" not in messaging_text, "NetMQ remained in Messaging project")
    require('Compile Remove="StreamingMessageHandler.cs"' in messaging_text, "streaming handler exclusion missing")

    print("QROS LEAN security patch candidate: APPLIED")
    print(f"LEAN base revision: {head}")
    print("Compression: DotNetZip 1.16.0 -> ProDotNetZip 1.20.0")
    print("Messaging: NetMQ removed; StreamingMessageHandler excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
