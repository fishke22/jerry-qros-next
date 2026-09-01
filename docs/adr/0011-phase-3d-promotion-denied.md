# ADR-0011 — Phase 3D patch candidate promotion remains denied

- Status: PROPOSED / NOT APPROVED
- Date: 2026-09-01
- Parent: ADR-0010

## Evidence

The Option B research experiment demonstrated that a combined candidate can remove the known NuGet HIGH/CRITICAL advisory graph while preserving the deterministic QROS synthetic backtest.

The repaired security run `33454221962` additionally forced analyzer rebuilds and verified path-traversal rejection through both LEAN Compression extraction APIs.

## Candidate

Research-only combined candidate:

1. NetMQ 4.0.1.6 → 4.0.4.3.
2. Remove DotNetZip 1.16.0 from Compression.
3. Supply the current LEAN `Ionic.Zip` compatibility surface through a QROS-owned bridge backed by runtime `System.IO.Compression` plus the already-present SharpZipLib BZip2 support.
4. Harden both archive-to-folder extraction paths with canonical destination-boundary validation.

## Why promotion is still denied

Passing the synthetic backtest is not sufficient coverage for a quant engine patch.

The compatibility bridge currently materializes complete ZIP entry contents in memory. This can create resource-exhaustion risk and is not a faithful final replacement for a streaming archive implementation.

Promotion also lacks:
- full patched transitive SBOM/license freeze;
- targeted LEAN compression regression coverage beyond the QROS smoke;
- resource/ZIP-bomb limits;
- Windows 11 x64 patched-engine validation;
- an approved long-term ownership model for divergence from upstream LEAN.

## Decision

**Do not promote.**

Phase 3D may be accepted as evidence that Option B is technically feasible. A future promotion proposal must replace or bound the in-memory bridge, complete the listed evidence, and receive a separate architecture approval.

The canonical LEAN gitlink and all runtime/live/package gates remain unchanged.
