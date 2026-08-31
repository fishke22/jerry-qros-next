from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pandera.pyarrow as pda
import pyarrow as pa
from pandera.errors import SchemaError

from .errors import DataQualityError
from .receipt import parse_aware_timestamp

PRICE_TYPE = pa.decimal128(18, 4)
BAR_SCHEMA = pda.DataFrameSchema({
    "schema_version": pda.Column(str, nullable=False),
    "dataset_id": pda.Column(str, nullable=False),
    "instrument_id": pda.Column(str, nullable=False),
    "timestamp": pda.Column(pa.timestamp("us", tz="UTC"), nullable=False),
    "open": pda.Column(PRICE_TYPE, nullable=False),
    "high": pda.Column(PRICE_TYPE, nullable=False),
    "low": pda.Column(PRICE_TYPE, nullable=False),
    "close": pda.Column(PRICE_TYPE, nullable=False),
    "volume": pda.Column(pa.int64(), nullable=False),
}, strict=True, ordered=True)


def validate_bars(table: pa.Table, *, source_timestamp: str) -> pa.Table:
    reasons: list[str] = []
    try:
        validated = BAR_SCHEMA.validate(table)
    except SchemaError as exc:
        raise DataQualityError([f"schema validation failed: {exc}"]) from exc
    source_dt = parse_aware_timestamp(source_timestamp, "source_timestamp")
    seen: set[tuple[str, datetime]] = set()
    zero = Decimal("0")
    for index, row in enumerate(validated.to_pylist()):
        key = (row["instrument_id"], row["timestamp"])
        if key in seen:
            reasons.append(f"row {index}: duplicate instrument/timestamp")
        seen.add(key)
        prices = [row["open"], row["high"], row["low"], row["close"]]
        if any(value <= zero for value in prices):
            reasons.append(f"row {index}: price must be positive")
        if row["high"] < max(row["open"], row["low"], row["close"]):
            reasons.append(f"row {index}: high is below OHLC member")
        if row["low"] > min(row["open"], row["high"], row["close"]):
            reasons.append(f"row {index}: low is above OHLC member")
        if row["volume"] < 0:
            reasons.append(f"row {index}: volume is negative")
        if row["timestamp"] > source_dt:
            reasons.append(f"row {index}: bar timestamp is after source_timestamp")
    if reasons:
        raise DataQualityError(reasons)
    return validated
