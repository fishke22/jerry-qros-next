# Phase 3D — LEAN security patch experiment evidence

## Authorization boundary

User selected **Option B** on 2026-09-01. ADR-0010 limits that authorization to research-only source/dependency experiments.

Canonical LEAN remains pinned at `b692bf4788e8b54fc23bdcb5659666bf055ce89f`. The gitlink is not changed.

## Candidate 1 — Messaging / NetMQ

Current pinned LEAN uses `NetMQ 4.0.1.6` in `Messaging/QuantConnect.Messaging.csproj`.

Official NetMQ/NuGet evidence observed 2026-09-01:

- current version: `4.0.4.3`;
- .NET 10 compatible;
- release date: 2026-07-30;
- current .NET dependency includes `System.ServiceModel.Primitives >= 10.0.652802`;
- project remains LGPLv3, the same license family already present through LEAN's existing NetMQ dependency.

The experiment changes only that version line in the CI checkout. Acceptance requires the old ServiceModel/WinHttpHandler HIGH advisories to disappear, while the unrelated Compression/DotNetZip blockers remain detectable.

No dependency version is adopted into QROS by this experiment.

## Candidate 1 result — Messaging / NetMQ

CI run `33452583461`, job `99685556630`:

- exact source-change scope — PASS;
- restore — PASS;
- old Messaging HIGH advisories absent — PASS;
- NetMQ resolved to `4.0.4.3`;
- System.ServiceModel.Primitives resolved to `10.0.652802`;
- unrelated DotNetZip HIGH and System.Drawing.Common CRITICAL remained visible — PASS;
- patched LEAN Launcher build — PASS, 0 errors;
- QROS synthetic algorithm build — PASS, 0 errors;
- deterministic synthetic backtest — PASS, rows 5 / sum 510.0000 / last 104.0000 / total orders 0.

The experiment's final runtime-promotion step intentionally returned DENY. Candidate status: **RESEARCH_CANDIDATE_PASS**, not adopted.

## Candidate 2 — Compression runtime bridge

The next experiment removes the DotNetZip package and injects a QROS-owned research-only compatibility bridge implemented exclusively with `System.IO.Compression`. It preserves only the LEAN `Ionic.Zip` call surface required by the current source tree so the security hypothesis can be tested without adding another ZIP library.

This is not proposed as the final upstream design. Acceptance requires a dedicated ZIP read/write smoke test in addition to Launcher build and the deterministic backtest.
