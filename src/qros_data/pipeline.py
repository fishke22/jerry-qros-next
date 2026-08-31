from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from .errors import DataQualityError, FailClosedError
from .qa import EXPECTED_ARROW_SCHEMA, validate_bars
from .receipt import RawReceiptStore, parse_aware_timestamp

DATASET_ID = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
SCHEMA_VERSION = "canonical-market-bar-row/v1"
NORMALIZER_VERSION = "bars-json-to-arrow-v1"
VALIDATOR_VERSION = "pandera-pyarrow-domain-v1"


@dataclass(frozen=True)
class PipelineResult:
    raw_path: Path
    receipt_path: Path
    parquet_path: Path
    validation_path: Path
    provenance_path: Path
    source_hash: str
    output_hash: str
    query_summary: dict


def _json_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise FailClosedError(f"immutable artifact conflict: {path.name}")


def _parse_price(value: object, field: str) -> Decimal:
    try:
        return Decimal(str(value)).quantize(Decimal("0.0001"))
    except (InvalidOperation, ValueError) as exc:
        raise DataQualityError([f"{field}: invalid decimal"]) from exc


def normalize_payload(payload: bytes, *, expected_dataset_id: str) -> pa.Table:
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FailClosedError("payload is not valid UTF-8 JSON") from exc
    if document.get("schema_version") != "bars-json-v1":
        raise FailClosedError("unsupported source schema_version")
    if document.get("dataset_id") != expected_dataset_id:
        raise FailClosedError("payload dataset_id does not match receipt")
    rows = document.get("bars")
    if not isinstance(rows, list) or not rows:
        raise FailClosedError("payload bars must be a non-empty list")
    normalized = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise FailClosedError(f"row {index} is not an object")
        try:
            timestamp = parse_aware_timestamp(row["timestamp"], f"row {index} timestamp").astimezone(timezone.utc)
            normalized.append({"schema_version":SCHEMA_VERSION,"dataset_id":expected_dataset_id,"instrument_id":str(row["instrument_id"]),"timestamp":timestamp,"open":_parse_price(row["open"],f"row {index} open"),"high":_parse_price(row["high"],f"row {index} high"),"low":_parse_price(row["low"],f"row {index} low"),"close":_parse_price(row["close"],f"row {index} close"),"volume":int(row["volume"])})
        except (KeyError, TypeError, ValueError) as exc:
            raise FailClosedError(f"row {index} cannot be normalized") from exc
    return pa.Table.from_pylist(normalized, schema=EXPECTED_ARROW_SCHEMA)


def _validation_record(source_hash: str, classification: str, reasons: list[str]) -> dict:
    return {"contract_id":"validation-result","contract_version":"1","subject_id":source_hash,"classification":classification,"blocking_reasons":reasons,"gate_opened":False,"research_only":True}


def _write_validation(workspace: Path, source_hash: str, classification: str, reasons: list[str]) -> Path:
    digest = source_hash.removeprefix("sha256:")
    path = workspace / "validations" / f"{digest}.validation.json"
    _write_once(path, _json_bytes(_validation_record(source_hash, classification, reasons)))
    return path


def _write_parquet(table: pa.Table, workspace: Path, dataset_id: str, source_hash: str) -> tuple[Path, str]:
    if not DATASET_ID.fullmatch(dataset_id):
        raise FailClosedError("dataset_id is not path-safe")
    digest = source_hash.removeprefix("sha256:")
    target = workspace / "canonical" / dataset_id / f"{digest}.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = workspace / "tmp" / f"{digest}.{uuid.uuid4().hex}.parquet"
    temp.parent.mkdir(parents=True, exist_ok=True)
    try:
        pq.write_table(table, temp, compression="zstd", version="2.6", write_statistics=True)
        output_hash = hashlib.sha256(temp.read_bytes()).hexdigest()
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != output_hash:
                raise FailClosedError("canonical parquet conflict")
        else:
            os.replace(temp, target)
        return target, f"sha256:{output_hash}"
    finally:
        if temp.exists():
            temp.unlink()


def query_parquet(path: Path) -> dict:
    connection = duckdb.connect(database=":memory:")
    try:
        connection.execute("SET autoinstall_known_extensions=false")
        connection.execute("SET autoload_known_extensions=false")
        row = connection.execute("SELECT count(*)::BIGINT, min(timestamp), max(timestamp), sum(volume)::HUGEINT FROM read_parquet(?)", [str(path)]).fetchone()
        return {"row_count":int(row[0]),"min_timestamp":row[1].isoformat() if row[1] is not None else None,"max_timestamp":row[2].isoformat() if row[2] is not None else None,"total_volume":int(row[3]) if row[3] is not None else 0}
    finally:
        connection.close()


def run_pipeline(*, payload: bytes, workspace: Path, dataset_id: str, source_id: str, source_timestamp: str | None, first_known_timestamp: str | None, received_at: str, code_revision: str) -> PipelineResult:
    store = RawReceiptStore(workspace)
    receipt, raw_path, receipt_path = store.receive(payload, dataset_id=dataset_id, source_id=source_id, source_timestamp=source_timestamp, first_known_timestamp=first_known_timestamp, received_at=received_at)
    source_hash = receipt["source_hash"]
    if receipt["quality_status"] != "PASS":
        validation_path = _write_validation(workspace, source_hash, "BLOCKED_INSUFFICIENT_EVIDENCE", ["receipt metadata is UNKNOWN or non-monotonic"])
        raise FailClosedError(f"receipt quality is not PASS: {validation_path.name}")
    try:
        table = validate_bars(normalize_payload(payload, expected_dataset_id=dataset_id), source_timestamp=source_timestamp or "")
    except DataQualityError as exc:
        _write_validation(workspace, source_hash, "FAIL_REQUIRES_REPAIR", list(exc.reasons))
        raise
    except FailClosedError as exc:
        _write_validation(workspace, source_hash, "BLOCKED_INSUFFICIENT_EVIDENCE", [str(exc)])
        raise
    parquet_path, output_hash = _write_parquet(table, workspace, dataset_id, source_hash)
    validation_path = _write_validation(workspace, source_hash, "PASS_REVIEW_ONLY", [])
    config_hash = "sha256:" + hashlib.sha256(f"{SCHEMA_VERSION}|{NORMALIZER_VERSION}|{VALIDATOR_VERSION}".encode("utf-8")).hexdigest()
    provenance = {"contract_id":"provenance-record","contract_version":"1","artifact_id":output_hash,"artifact_type":"canonical-parquet","source_artifacts":[source_hash],"source_hashes":{"raw_payload":source_hash},"output_hash":output_hash,"code_revision":code_revision,"config_hash":config_hash,"generated_at":received_at,"research_only":True,"validation_status":"PASS_REVIEW_ONLY"}
    provenance_path = workspace / "provenance" / f"{output_hash.removeprefix('sha256:')}.json"
    _write_once(provenance_path, _json_bytes(provenance))
    return PipelineResult(raw_path,receipt_path,parquet_path,validation_path,provenance_path,source_hash,output_hash,query_parquet(parquet_path))
