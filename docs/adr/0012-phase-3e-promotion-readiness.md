# ADR-0012 — Phase 3E promotion-readiness evidence

- Status: RESEARCH / PROMOTION NOT APPROVED
- Date: 2026-09-01
- Parents: ADR-0010, ADR-0011

Phase 3E may improve the Option B research candidate and collect promotion-readiness evidence, but it does not authorize runtime promotion or a canonical LEAN gitlink change.

The in-memory ZipFile compatibility implementation is replaced in the experiment by a stream-backed ZipArchiveEntry wrapper. Existing-entry reads and saves are streamed; byte arrays remain only for entries explicitly added by callers.

Required cloud evidence:
- no HIGH/CRITICAL advisories in the patched Launcher graph;
- deterministic quant regression;
- targeted compression behavior regression;
- patched transitive CycloneDX 1.7 inventory and license review;
- standard GitHub-hosted Windows compatibility.

A GitHub Windows runner is not equivalent to the Windows 11 x64 desktop target. Physical Windows 11 validation remains a separate hard gate.

Promotion remains denied until the evidence is reviewed and a later promotion ADR is explicitly approved.
