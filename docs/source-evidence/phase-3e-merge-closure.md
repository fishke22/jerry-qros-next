# Phase 3E Merge Closure Evidence

Date: 2026-09-01

Disposition: `PHASE_3E = ACCEPTED_MERGED`

## Scope

Phase 3E closes post-merge security and provenance findings without expanding runtime authorization beyond the already-approved patched local Research/Backtest scope.

## Accepted source

- PR: `#18`
- sealed source head: `1598c320eeacf452519b8fd7ae8195d928ec74e5`
- squash merge commit: `6b08e0cd0bb3536e2f01d88e2bf540d20db54a23`
- accepted head tree: `dee4a39e3bc4caf937755768d2ed7278191415ff`
- merge commit tree: `dee4a39e3bc4caf937755768d2ed7278191415ff`
- post-merge tree equivalence: `PASS`
- LEAN gitlink: `b692bf4788e8b54fc23bdcb5659666bf055ce89f`

## Fresh exact-head CI

- `qros-gate`: run `33529365184` — `SUCCESS`
- `lean-security-research`: run `33529365278` — `SUCCESS`
- `lean-integration`: run `33529364975`, attempt 1 / job `99928609619` — `SUCCESS`
- independent same-head rerun: run `33529364975`, attempt 2 / job `99929572680` — `SUCCESS`

## Same-head runtime fingerprint

Both LEAN integration attempts reproduced:

- algorithm assembly: `sha256:8da207beca34d7caeea556a8b4ad61178275f18583ad59ef3dc998f2bc3dd60e`
- normalized result: `sha256:43153f0cc229a6c55005581678cbcf02002e9377c4939115e92d4fd5c48e2881`
- overlay identity: `sha256:cd78ab7cea3f10608989c44be1f9bd4c162c04895a21cca77de55ccee5901525`
- patch wrapper: `sha256:0cdd79a6b9a88b8c9bb01f7451a8a1dee4e44efd4e8b9624354f6ec469a1338e`
- patch implementation: `sha256:3880d38003443024458e060bba06fd06090c4fffa3e4698cfd7e5fab33a4fc3c`
- patched graph: `sha256:4b9abb8a71d5197cb54994f5662c249d6ac157bc5239bf5facf8bc0e73d113a8`
- Launcher assembly: `sha256:7338f2253306a45b0dd039c5e0d266102a9b38df79a5f411b636e75756a81c19`
- runtime assembly manifest: `sha256:3a7b926de7e6420de31d942508662061c5e5717fa0df9de86743010374614355`
- runtime assembly count: `191`
- input: `sha256:3921a0ab8ed226e6a404aca6024cf28e91100f97fb51766ecd78151c9e063e44`
- config: `sha256:4f2e7517fbf5dae1b6fe2275ce3e7fe8873d5209f7fa5b685a2f6cef9ff7e5b8`
- semantic regression: `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`
- rows: `5`
- sum: `510.0000`
- last: `104.0000`
- total orders: `0`

## Contract closure

- issued `lean-backtest-result/v2` preserved at Git blob `f5d4b469f67e7e43683cc138de8903c5ed10693e`
- issued `provenance-record/v2` preserved at Git blob `96a5799c80fc4f238d4f5f531ac172d203527ed6`
- hardened `lean-backtest-result/v3` Git blob `7db27211f635ca2bc94657b0dcade99b85bc76be`
- hardened `provenance-record/v3` Git blob `f21d8e58db68a9c2cb306102ed3bb5834a5bf121`

## Post-merge verification

- current merge commit after PR #18: `6b08e0cd0bb3536e2f01d88e2bf540d20db54a23`
- post-merge `qros-gate`: run `33530330017` — `SUCCESS`
- exact LEAN gitlink preserved
- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`
- zero-cost policy preserved
- no new dependency or license impact introduced

## Decision

`LOCAL_PATCHED_RESEARCH_RUNTIME = ALLOW_WITHIN_EXISTING_RESTRICTED_SCOPE`

`UNPATCHED_UPSTREAM_RUNTIME = DENY`

This is not a production-readiness claim.

Next gate: Phase 4 `RESEARCH → DESIGN`; Phase 4 dependencies remain `DENY` until independently verified and pinned.
