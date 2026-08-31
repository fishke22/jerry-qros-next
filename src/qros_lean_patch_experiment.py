from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "external" / "lean"

CANDIDATES = {
    "messaging-netmq-4.0.4.3": {
        "path": LEAN / "Messaging" / "QuantConnect.Messaging.csproj",
        "old": '<PackageReference Include="NetMQ" Version="4.0.1.6" />',
        "new": '<PackageReference Include="NetMQ" Version="4.0.4.3" />',
    }
}


def apply(candidate: str) -> Path:
    cfg = CANDIDATES[candidate]
    path = cfg["path"]
    text = path.read_text(encoding="utf-8-sig")
    if cfg["new"] in text:
        raise RuntimeError("candidate already applied; refusing ambiguous state")
    if text.count(cfg["old"]) != 1:
        raise RuntimeError("expected exact old dependency line not found once")
    path.write_text(text.replace(cfg["old"], cfg["new"]), encoding="utf-8")
    return path
