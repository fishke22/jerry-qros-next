from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qros_data import DataQualityError, FailClosedError, run_pipeline


def payload(*, invalid_ohlc: bool = False, future_bar: bool = False) -> bytes:
    high = "98.0000" if invalid_ohlc else "102.0000"
    timestamp = "2026-08-31T07:00:00+00:00" if future_bar else "2026-08-29T05:30:00+00:00"
    document = {"schema_version":"bars-json-v1","dataset_id":"synthetic.twse.daily","bars":[{"instrument_id":"2330.TW","timestamp":"2026-08-28T05:30:00+00:00","open":"100.0000","high":high,"low":"99.0000","close":"101.0000","volume":1000},{"instrument_id":"2330.TW","timestamp":timestamp,"open":"101.0000","high":"103.0000","low":"100.0000","close":"102.0000","volume":1200}]}
    return json.dumps(document, sort_keys=True).encode("utf-8")


def run_valid(workspace: Path, data: bytes):
    return run_pipeline(payload=data,workspace=workspace,dataset_id="synthetic.twse.daily",source_id="SYNTHETIC_TEST",source_timestamp="2026-08-30T06:00:00+00:00",first_known_timestamp="2026-08-30T06:05:00+00:00",received_at="2026-08-30T06:05:01+00:00",code_revision="phase2-test-revision")


class Phase2DataPipelineTests(unittest.TestCase):
    def test_valid_slice_writes_receipt_parquet_provenance_and_duckdb_query(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_valid(Path(directory), payload())
            self.assertTrue(result.raw_path.is_file())
            self.assertTrue(result.receipt_path.is_file())
            self.assertTrue(result.parquet_path.is_file())
            self.assertTrue(result.validation_path.is_file())
            self.assertTrue(result.provenance_path.is_file())
            self.assertEqual(result.query_summary["row_count"], 2)
            self.assertEqual(result.query_summary["total_volume"], 2200)
            self.assertEqual(pq.read_table(result.parquet_path).num_rows, 2)
            validation = json.loads(result.validation_path.read_text(encoding="utf-8"))
            self.assertEqual(validation["classification"], "PASS_REVIEW_ONLY")
            self.assertFalse(validation["gate_opened"])

    def test_same_input_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            first = run_valid(Path(directory), payload())
            second = run_valid(Path(directory), payload())
            self.assertEqual(first.source_hash, second.source_hash)
            self.assertEqual(first.output_hash, second.output_hash)
            self.assertEqual(first.parquet_path, second.parquet_path)

    def test_unknown_receipt_timestamp_fails_closed_before_canonical_write(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            with self.assertRaises(FailClosedError):
                run_pipeline(payload=payload(),workspace=workspace,dataset_id="synthetic.twse.daily",source_id="SYNTHETIC_TEST",source_timestamp=None,first_known_timestamp=None,received_at="2026-08-30T06:05:01+00:00",code_revision="phase2-test-revision")
            self.assertTrue(any((workspace / "raw").rglob("*.raw")))
            self.assertFalse((workspace / "canonical").exists())
            record = json.loads(next((workspace / "validations").glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(record["classification"], "BLOCKED_INSUFFICIENT_EVIDENCE")
            self.assertFalse(record["gate_opened"])

    def test_invalid_ohlc_is_rejected_and_no_parquet_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            with self.assertRaises(DataQualityError):
                run_valid(workspace, payload(invalid_ohlc=True))
            self.assertFalse((workspace / "canonical").exists())
            record = json.loads(next((workspace / "validations").glob("*.json")).read_text(encoding="utf-8"))
            self.assertEqual(record["classification"], "FAIL_REQUIRES_REPAIR")

    def test_future_bar_is_rejected_as_point_in_time_violation(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            with self.assertRaises(DataQualityError):
                run_valid(workspace, payload(future_bar=True))
            self.assertFalse((workspace / "canonical").exists())


if __name__ == "__main__":
    unittest.main()
