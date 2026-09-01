from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qros_lean.runtime_overlay import LEAN_REVISION, apply_patch


def main() -> int:
    apply_patch(ROOT)
    print("QROS LEAN security patch: APPLIED / EXACT POST-PATCH DIFF VERIFIED")
    print(f"LEAN base revision: {LEAN_REVISION}")
    print("Compression: DotNetZip 1.16.0 -> ProDotNetZip 1.20.0")
    print("Messaging: NetMQ removed; StreamingMessageHandler excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
