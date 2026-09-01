from __future__ import annotations

import argparse
import json
from pathlib import Path

from qros_lean.backtest import semantic_regression_hash

EXPECTED_SEMANTIC_HASH = (
    "sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1"
)
HISTORICAL_FULL_HASH = (
    "sha256:6da211cffdf7f667b212f9bf083d9f2d78e40b42895e6b6ed0342b76b5d6e5f1"
)


def validate(path: Path) -> None:
    result = json.loads(path.read_text(encoding="utf-8"))
    actual_semantic = semantic_regression_hash(result)
    fingerprint = {
        "normalized_hash": result["normalized_hash"],
        "algorithm_assembly_hash": result["algorithm_assembly_hash"],
        "input_hash": result["input_hash"],
        "config_hash": result["config_hash"],
        "statistics": result["statistics"],
        "classification": result["classification"],
        "research_only": result["research_only"],
        "gate_opened": result["gate_opened"],
        "semantic_regression_hash": actual_semantic,
    }
    print("Phase 3D non-secret result fingerprint: " + json.dumps(fingerprint, sort_keys=True))
    print("Phase 3B historical full normalized hash: " + HISTORICAL_FULL_HASH)
    if actual_semantic != EXPECTED_SEMANTIC_HASH:
        raise RuntimeError(
            "Phase 3B semantic regression mismatch: "
            f"expected {EXPECTED_SEMANTIC_HASH}, got {actual_semantic}"
        )
    print(f"Phase 3B semantic regression baseline: PASS ({actual_semantic})")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    validate(args.result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
