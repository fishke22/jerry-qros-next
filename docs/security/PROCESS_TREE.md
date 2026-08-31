# Process Tree — Phase 2

## Local data slice

Expected runtime process:

```text
user shell / future QROS host
└─ CPython 3.14.x
   ├─ PyArrow (in-process native extension)
   ├─ Pandera / Narwhals / Pydantic (in-process Python libraries)
   └─ DuckDB (in-process native extension)
```

No child process is required by the Data Receipt → QA → Parquet → DuckDB path.

## CI

```text
GitHub standard hosted runner
└─ actions/checkout (full-SHA pinned)
└─ actions/setup-python (full-SHA pinned)
└─ CPython 3.14.7
   ├─ pip hash-locked wheel installation
   ├─ governance / contract / supply-chain validators
   └─ unittest suite
```

This document does not authorize packaging, persistence, broker login, Yuanta integration or live trading.
