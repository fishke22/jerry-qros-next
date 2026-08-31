from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LEAN_REVISION = "b692bf4788e8b54fc23bdcb5659666bf055ce89f"
ALGORITHM_ID = "qros-phase3b-synthetic"
EXPECTED = {
    "QROS Rows": "5",
    "QROS Sum": "510.0000",
    "QROS Last": "104.0000",
    "Total Orders": "0",
}


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def normalize_result(
    raw: dict, *, algorithm_hash: str, input_hash: str, config_hash: str
) -> dict:
    stats = raw.get("Statistics")
    if not isinstance(stats, dict):
        raise RuntimeError("LEAN result Statistics missing")
    for key, expected in EXPECTED.items():
        actual = str(stats.get(key))
        if actual != expected:
            raise RuntimeError(
                f"LEAN statistic mismatch {key}: expected {expected!r}, got {actual!r}"
            )

    result = {
        "contract_id": "lean-backtest-result",
        "contract_version": "1",
        "engine": "QuantConnect/Lean",
        "engine_revision": LEAN_REVISION,
        "algorithm_id": ALGORITHM_ID,
        "algorithm_assembly_hash": algorithm_hash,
        "input_hash": input_hash,
        "config_hash": config_hash,
        "classification": "PASS_REVIEW_ONLY",
        "research_only": True,
        "gate_opened": False,
        "statistics": {
            "qros_rows": EXPECTED["QROS Rows"],
            "qros_sum": EXPECTED["QROS Sum"],
            "qros_last": EXPECTED["QROS Last"],
            "total_orders": EXPECTED["Total Orders"],
        },
    }
    result["normalized_hash"] = (
        "sha256:" + hashlib.sha256(canonical_bytes(result)).hexdigest()
    )
    return result


def run_once(
    root: Path,
    algorithm_dll: Path,
    fixture: Path,
    config: Path,
    run_root: Path,
) -> tuple[dict, str]:
    results = run_root / "results"
    results.mkdir(parents=True)
    launcher = (
        root
        / "external"
        / "lean"
        / "Launcher"
        / "bin"
        / "Release"
        / "QuantConnect.Lean.Launcher.dll"
    )
    if not launcher.is_file():
        raise RuntimeError("LEAN Launcher is not built")
    if not algorithm_dll.is_file():
        raise RuntimeError("QROS synthetic algorithm is not built")

    env = os.environ.copy()
    env["QROS_SYNTHETIC_DATA_FILE"] = str(fixture.resolve())
    command = [
        "dotnet",
        str(launcher),
        "--config",
        str(config.resolve()),
        "--environment",
        "backtesting",
        "--algorithm-type-name",
        "QrosSyntheticBacktestAlgorithm",
        "--algorithm-language",
        "CSharp",
        "--algorithm-location",
        str(algorithm_dll.resolve()),
        "--data-folder",
        str((root / "external" / "lean" / "Data").resolve()),
        "--results-destination-folder",
        str(results.resolve()),
        "--close-automatically",
        "true",
        "--algorithm-id",
        ALGORITHM_ID,
        "--backtest-name",
        ALGORITHM_ID,
    ]
    completed = subprocess.run(
        command,
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        timeout=90,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "LEAN backtest failed\nSTDOUT:\n"
            + completed.stdout
            + "\nSTDERR:\n"
            + completed.stderr
        )

    result_file = results / f"{ALGORITHM_ID}.json"
    if not result_file.is_file():
        raise RuntimeError(
            "LEAN result file missing\nSTDOUT:\n" + completed.stdout
        )

    raw = json.loads(result_file.read_text(encoding="utf-8"))
    normalized = normalize_result(
        raw,
        algorithm_hash=sha256_file(algorithm_dll),
        input_hash=sha256_file(fixture),
        config_hash=sha256_file(config),
    )
    return normalized, sha256_file(result_file)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    fixture = root / "fixtures_synthetic" / "lean" / "qros-synthetic-daily.csv"
    config = root / "integration" / "lean" / "backtest-config.json"
    algorithm_dll = (
        root
        / "integration"
        / "lean"
        / "QrosSyntheticAlgorithm"
        / "bin"
        / "Release"
        / "net10.0"
        / "Qros.Lean.SyntheticAlgorithm.dll"
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="qros-lean-a-") as a:
        first, raw_a = run_once(
            root, algorithm_dll, fixture, config, Path(a)
        )
    with tempfile.TemporaryDirectory(prefix="qros-lean-b-") as b:
        second, raw_b = run_once(
            root, algorithm_dll, fixture, config, Path(b)
        )

    if first != second:
        raise RuntimeError("normalized LEAN result is not deterministic")

    result_path = args.output_dir / "lean-backtest-result.v1.json"
    result_path.write_bytes(canonical_bytes(first) + b"\n")

    provenance = {
        "contract_id": "provenance-record",
        "contract_version": "1",
        "artifact_id": first["normalized_hash"],
        "artifact_type": "lean-backtest-result/v1",
        "source_artifacts": [
            first["input_hash"],
            first["algorithm_assembly_hash"],
        ],
        "source_hashes": {
            "synthetic_input": first["input_hash"],
            "algorithm_assembly": first["algorithm_assembly_hash"],
            "lean_raw_result_run_a": raw_a,
            "lean_raw_result_run_b": raw_b,
        },
        "output_hash": sha256_file(result_path),
        "code_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "config_hash": first["config_hash"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_only": True,
        "validation_status": "PASS_REVIEW_ONLY",
    }
    provenance_path = args.output_dir / "lean-backtest-provenance.json"
    provenance_path.write_bytes(canonical_bytes(provenance) + b"\n")

    validation = {
        "contract_id": "validation-result",
        "contract_version": "1",
        "subject_id": first["normalized_hash"],
        "classification": "PASS_REVIEW_ONLY",
        "blocking_reasons": [],
        "gate_opened": False,
        "research_only": True,
    }
    validation_path = args.output_dir / "lean-backtest-validation.json"
    validation_path.write_bytes(canonical_bytes(validation) + b"\n")

    print(json.dumps(first, sort_keys=True))
    print("QROS Phase 3B deterministic LEAN backtest: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
