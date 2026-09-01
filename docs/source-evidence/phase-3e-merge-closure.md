# Phase 3E merge-closure evidence — 2026-09-01

## Scope

This record closes Phase 3E post-merge security/provenance hardening. It accepts only the deterministic patched LEAN local Research/Backtest runtime. It does not authorize packaging, release, Yuanta integration, broker access, credentials, login, or live trading.

## Accepted candidate and merge

- PR: #18
- final sealed candidate head: `1598c320eeacf452519b8fd7ae8195d928ec74e5`
- squash merge commit: `6b08e0cd0bb3536e2f01d88e2bf540d20db54a23`
- candidate tree: `dee4a39e3bc4caf937755768d2ed7278191415ff`
- merge tree: `dee4a39e3bc4caf937755768d2ed7278191415ff`
- post-merge tree equivalence: PASS
- exact LEAN gitlink: `b692bf4788e8b54fc23bdcb5659666bf055ce89f`

## Fresh exact-head CI

At candidate head `1598c320eeacf452519b8fd7ae8195d928ec74e5`:

- qros-gate run `33529365184`, job `99928262098`: SUCCESS
- lean-security-research run `33529365278`, job `99929955725`: SUCCESS
- lean-integration run `33529364975`, attempt 1 job `99928609619`: SUCCESS
- lean-integration same-head attempt 2 job `99929572680`: SUCCESS

Post-merge main:

- qros-gate run `33530330017`, job `99931568789`: SUCCESS

## Same-head reproducibility

Both independent LEAN jobs reproduced:

- engine revision: `b692bf4788e8b54fc23bdcb5659666bf055ce89f`
- contract version: `3`
- algorithm assembly: `sha256:8da207beca34d7caeea556a8b4ad61178275f18583ad59ef3dc998f2bc3dd60e`
- input: `sha256:3921a0ab8ed226e6a404aca6024cf28e91100f97fb51766ecd78151c9e063e44`
- config: `sha256:4f2e7517fbf5dae1b6fe2275ce3e7fe8873d5209f7fa5b685a2f6cef9ff7e5b8`
- normalized result: `sha256:43153f0cc229a6c55005581678cbcf02002e9377c4939115e92d4fd5c48e2881`
- overlay identity: `sha256:cd78ab7cea3f10608989c44be1f9bd4c162c04895a21cca77de55ccee5901525`
- patch wrapper: `sha256:0cdd79a6b9a88b8c9bb01f7451a8a1dee4e44efd4e8b9624354f6ec469a1338e`
- patch implementation: `sha256:3880d38003443024458e060bba06fd06090c4fffa3e4698cfd7e5fab33a4fc3c`
- patched graph: `sha256:4b9abb8a71d5197cb54994f5662c249d6ac157bc5239bf5facf8bc0e73d113a8`
- Launcher assembly: `sha256:7338f2253306a45b0dd039c5e0d266102a9b38df79a5f411b636e75756a81c19`
- runtime assembly count: `191`
- runtime assembly manifest: `sha256:3a7b926de7e6420de31d942508662061c5e5717fa0df9de86743010374614355`
- semantic regression: `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`
- statistics: rows 5 / sum 510.0000 / last 104.0000 / total orders 0

## Review closure

Sealed-head Codex review explicitly reviewed commit `1598c320ee`.

- P1/P2 unresolved findings: 0
- P3: changelog literal escaped newline; tracked as Issue #19 and corrected by this governance closure.
- No green-test-only production-readiness claim is made.

## Contract and provenance disposition

- Existing `lean-backtest-result/v2` and `provenance-record/v2` were restored byte-for-byte and remain immutable.
- Hardened runtime identity is published as v3.
- `patch_script_hash` is the actual patch wrapper digest.
- `patch_implementation_hash` separately binds implementation bytes.
- NuGet vulnerability evidence treats explicit null/unknown severity as DENY.
- Runtime identity includes the full Launcher DLL closure and requires Launcher, Compression, and Messaging outputs.

## License and cost

- New runtime dependencies introduced by Phase 3E: 0
- Patched Launcher SBOM: 55 NuGet components
- Manual license dispositions: 11 accepted, unknown = DENY
- Incremental service/dependency cost: 0
- Paid runners/services/data/LLM/storage/code-signing: not authorized

## Hard gates

- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`
- unpatched upstream LEAN runtime: DENY

## Disposition

`PHASE_3E = ACCEPTED_MERGED_LOCAL_RESEARCH_BACKTEST_HARDENED`

Next gate: Phase 4 RESEARCH → DESIGN. All Phase 4 dependencies remain DENY until separately verified and pinned.
