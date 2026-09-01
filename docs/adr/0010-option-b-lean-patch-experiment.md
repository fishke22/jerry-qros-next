# ADR-0010 — Authorize Option B research-only LEAN patch experiment

- Status: APPROVED_FOR_RESEARCH_EXPERIMENT_ONLY
- Date: 2026-09-01
- User authorization: `Option B`
- Parents: ADR-0007, ADR-0008, ADR-0009

## Authorization

The user explicitly selected Option B after ADR-0009 presented:

> research-only, upstream-aligned LEAN security patch experiment

This authorizes source/dependency modifications only inside isolated research branches and CI working copies for the purpose of evaluating security remediation.

## Still denied

This authorization does **not** authorize:

- merging Phase 3B into main;
- changing the canonical LEAN gitlink;
- promoting a QROS-maintained LEAN fork;
- runtime promotion;
- .NET toolchain upgrade;
- Yuanta integration or live trading;
- packaging or release.

## Experimental order

1. Messaging root cause: update the already-present NetMQ dependency from 4.0.1.6 to the current 4.0.4.3 and verify whether the obsolete ServiceModel/WinHttpHandler vulnerability chain disappears without changing LEAN behavior.
2. Compression root cause: independently evaluate an upstream-aligned migration away from DotNetZip/Ionic.Zip toward System.IO.Compression.

Each candidate must be independently attributable and must pass exact-pinned build, dependency audit, and the existing deterministic QROS → LEAN regression.

A successful experiment is evidence for a later amendment. It is not runtime approval.
