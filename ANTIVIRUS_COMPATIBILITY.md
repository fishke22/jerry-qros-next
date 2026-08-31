# Antivirus Compatibility

Target: Windows 11 x64 with Defender, Norton and other endpoint antivirus.

Avoid: process/DLL injection, self-modifying executables, hidden PowerShell core flow, arbitrary download-and-execute, temp unpack-and-run, packers/obfuscation, undocumented startup persistence, credential embedding and opaque child processes.

Candidate builds progressively require documented process tree/network endpoints, dependency manifest, SBOM, SHA-256 and provenance.

False-positive flow: Detection → artifact hash → reproduce from source/build → vendor submission → re-test → evidence.

Permanent antivirus exclusions are not a deployment solution. Paid trusted code signing remains OPTIONAL_FUTURE_PAID_REQUIREMENT and is not authorized.

## Phase 2 data runtime

The Phase 2 slice runs inside one foreground CPython process. DuckDB is an in-process library; there is no database daemon, background service, DLL/process injection, persistence mechanism, runtime unpack-and-execute flow or broker process.

Canonical runtime data processing makes no network request. CI downloads are limited to pinned GitHub Actions and hash-locked PyPI wheels documented in `docs/security/NETWORK_ENDPOINTS.md`.

Local raw receipts, Parquet, Arrow, DuckDB/SQLite files and Python virtual environments are excluded from Git tracking.
