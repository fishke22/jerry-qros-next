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
