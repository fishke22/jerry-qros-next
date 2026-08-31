from __future__ import annotations

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", choices=sorted(CANDIDATES), required=True)
    args = parser.parse_args()
    path = apply(args.candidate)
    print(f"QROS LEAN patch experiment applied: {args.candidate}")
    print(path.relative_to(LEAN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
