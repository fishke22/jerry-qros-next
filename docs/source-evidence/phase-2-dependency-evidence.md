# Phase 2 dependency evidence — 2026-08-31

## Direct runtime

| Component | Pin | License | Compatibility / evidence | Decision |
|---|---:|---|---|---|
| CPython | 3.14.7 | PSF License v2 | Current 3.14 bugfix release; Windows x64 available | ADOPT toolchain |
| DuckDB | 1.5.5 | MIT | Python >=3.10; CPython 3.14 Windows x64 wheel | ADOPT |
| PyArrow | 25.0.1 | Apache-2.0 | Python >=3.10; CPython 3.14 Windows x64 wheel | ADOPT |
| Pandera | 0.33.0 | MIT | Python >=3.10; direct PyArrow backend added in 0.33.0 | ADOPT / Python QA only |

## Transitive runtime

The hash-locked dependency resolution contains Narwhals 2.25.0, packaging 26.3, typing-inspect 0.9.0, mypy-extensions 1.1.0, typing-extensions 4.16.0, Pydantic 2.13.5, pydantic-core 2.46.5, annotated-types 0.8.0, typing-inspection 0.4.4 and typeguard 4.6.0.

All have verified permissive license metadata. PyPI metadata for mypy-extensions did not declare a license, so it remained DENY until the official python/mypy_extensions tag 1.1.0 LICENSE was checked; that file states MIT.

## CI tooling

actions/setup-python v6.2.0 is pinned to commit a309ff8b426b58ec0e2a45f0f869d46889d02405 and its official repository LICENSE is MIT.

No paid service, paid runner, cloud database, broker SDK or external market-data feed is introduced.

## Verified implementation caveat

A Windows x64 smoke run with Python 3.14.6 and the exact Phase 2 dependency lock reproduced a Pandera 0.33.0/Narwhals limitation: constructing a Pandera PyArrow column with `pyarrow.decimal128(18, 4)` raises `TypeError: data type 'Decimal(precision=18, scale=4)' not understood by Engine`.

This conflicts with the documented general support for parameterized PyArrow data types. QROS therefore does not treat that documentation claim as verified capability for decimal columns. The canonical Arrow schema still requires decimal128(18,4); PyArrow enforces that physical type, Pandera validates a strict supported-column projection, and deterministic QROS checks validate OHLC semantics.

Status: `VERIFIED_LIMITATION / WORKAROUND_WITHOUT_SCHEMA_RELAXATION`.
