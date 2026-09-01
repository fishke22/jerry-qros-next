# ADR-0012 — Phase 3E LEAN candidate promotion review boundary

- Status: REVIEW
- Date: 2026-09-01
- Parent: ADR-0011

## Purpose

Phase 3D established technical feasibility for an isolated Option B security-patch candidate. Phase 3E reviews whether enough evidence exists to even propose promotion.

This phase does **not** authorize promotion.

## Required evidence

1. Generate a full transitive CycloneDX 1.7 inventory from the patched Launcher's restored `project.assets.json`.
2. Extract NuGet package license metadata and explicitly review the NetMQ 4.0.4.3 LGPLv3 + project-specific linking exception evidence.
3. Execute upstream LEAN `CompressionTests` against the patched source tree.
4. Probe the compatibility bridge's high-compression resource behavior; full-entry buffering remains a blocker unless bounded or replaced with a streaming design.
5. Run the patched engine on a standard GitHub-hosted Windows runner using exact .NET SDK 10.0.400 and the deterministic QROS backtest.

## Hard gates

Regardless of test outcome:

- canonical LEAN gitlink remains unchanged;
- main merge remains denied;
- runtime promotion remains denied;
- package/release remains denied;
- Yuanta/live trading remain denied.

A future positive Phase 3E review would only create a promotion proposal. Actual adoption requires a separate explicit architecture authorization.
