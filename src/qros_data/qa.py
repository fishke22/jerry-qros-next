from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pandera.pyarrow as pda
import pyarrow as pa
from pandera.errors import SchemaError

from .errors import DataQualityError
from .receipt import parse_aware_timestamp

PRICE_TYPE = pa.decimal128(18, 4)
EXPECTED_ARROW_SCHEMA = pa.schema(
    [
        pa.field("schema_version", pa.string(), nullable=False),
        pa.field("dataset_id", pa.string(), nullable=False),
        pa.field("instrument_id", pa.string(), nullable=False),
        pa.field("timestamp", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("open", PRICE_TYPE, nullable=False),
        pa.field("high", PRICE_TYPE, nullable=False),
        pa.field("low", PRICE_TYPE, nullable=False),
        pa.field("close", PRICE_TYPE, nullable=False),
        pa.field("volume", pa.int64(), nullable=False),
    ]
)

# Pandera 0.33.0's PyArrow/Narwhals engine does not reliably resolve
# pa.decimal128(18, 4) on the verified Windows runtime. The complete
# physical schema is therefore enforced above with PyArrow, while Pandera
# validates a strict projection of types it demonstrably supports.
PANDERA_PROJECTION = ("schema_version", "dataset_id", "instrument_id", "timestamp", "volume")
BAR_PROJECTION_SCHEMA = pda.DataFrameSchema(
    {
        "schema_version": pda.Column(str, nullable=False),
        "dataset_id": pda.Column(str, nullable=False),
        "instrument_id": pda.Column(str, nullable=False),
        "timestamp": pda.Column(pa.timestamp("us", tz="UTC"), nullable=False),
        "volume": pda.Column(pa.int64(), nullable=False),
    },
    strict=True,
    ordered=True,
)


def validate_bars(table: pa.Table, *, source_timestamp: str) -> pa.Table:
    reasons: list[str] = []
    if not table.schema.equals(EXPECTED_ARROW_SCHEMA, check_metadata=False):
        raise DataQualityError(
            [
                "Arrow physical schema mismatch: "
                f"expected={EXPECTED_ARROW_SCHEMA} actual={table.schema}"
            ]
        )

    try:
        BAR_PROJECTION_SCHEMA.validate(table.select(PANDERA_PROJECTION))
    except (SchemaError, TypeError) as exc:
        raise DataQualityError([f"Pandera projection validation failed: {exc}"]) from exc

    source_dt = parse_aware_timestamp(source_timestamp, "source_timestamp")
    seen: set[tuple[str, datetime]] = set()
    zero = Decimal("0")
    for index, row in enumerate(table.to_pylist()):
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
    return table
