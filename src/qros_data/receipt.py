from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from .errors import FailClosedError

RECEIPT_NORMALIZER_VERSION = "raw-receipt-v1"
RECEIPT_VALIDATOR_VERSION = "receipt-metadata-v1"


def parse_aware_timestamp(value: str | None, field: str) -> datetime:
    if not value:
        raise ValueError(f"{field} is unknown")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise FailClosedError(f"immutable artifact conflict: {path.name}")


class RawReceiptStore:
    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)

    def receive(self, payload: bytes, *, dataset_id: str, source_id: str, source_timestamp: str | None, first_known_timestamp: str | None, received_at: str) -> tuple[dict, Path, Path]:
        digest = hashlib.sha256(payload).hexdigest()
        source_hash = f"sha256:{digest}"
        raw_path = self.workspace / "raw" / "sha256" / f"{digest}.raw"
        _write_once(raw_path, payload)
        quality_status = "PASS"
        try:
            source_dt = parse_aware_timestamp(source_timestamp, "source_timestamp")
            known_dt = parse_aware_timestamp(first_known_timestamp, "first_known_timestamp")
            received_dt = parse_aware_timestamp(received_at, "received_at")
            if not (source_dt <= known_dt <= received_dt):
                raise ValueError("receipt timestamps are not monotonic")
        except ValueError:
            quality_status = "UNKNOWN"
        receipt = {"contract_id":"data-receipt","contract_version":"1","dataset_id":dataset_id,"source_id":source_id,"source_timestamp":source_timestamp,"first_known_timestamp":first_known_timestamp,"received_at":received_at,"source_hash":source_hash,"normalizer_version":RECEIPT_NORMALIZER_VERSION,"validator_version":RECEIPT_VALIDATOR_VERSION,"quality_status":quality_status}
        receipt_bytes = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        receipt_path = self.workspace / "receipts" / f"{digest}.receipt.json"
        _write_once(receipt_path, receipt_bytes)
        return receipt, raw_path, receipt_path
