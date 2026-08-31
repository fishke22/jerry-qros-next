from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qros_lean_patch_experiment import CANDIDATES, apply


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", choices=sorted(CANDIDATES), required=True)
    args = parser.parse_args()
    path = apply(args.candidate)
    print(f"QROS LEAN patch experiment applied: {args.candidate}")
    print(path.relative_to(ROOT / "external" / "lean"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
