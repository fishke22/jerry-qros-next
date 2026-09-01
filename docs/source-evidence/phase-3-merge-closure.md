# Phase 3 merge-closure evidence — 2026-09-01

## Scope

This record closes the engineering/governance merge gate for Phase 3 only. It does not authorize packaging, release, Yuanta integration, broker credentials, broker login, or live trading.

## Accepted source state

- final accepted head: `7b5f89a1972fd39abb78e0ad998eacf874e42739`
- exact LEAN gitlink: `b692bf4788e8b54fc23bdcb5659666bf055ce89f`
- accepted runtime scope: `LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH`
- unpatched upstream runtime: DENY
- patched graph: 55 NuGet packages / 19 project nodes
- patched graph semantic SHA-256: `165ba17fec034b417f4ae91b86544cbe9b2002f1c561f4908b0d43a76875f235`

## Independent reproducibility

Same exact head jobs `99846751986` and `99847616213` both produced the same algorithm assembly `sha256:e05ef74439000c2d1dd93cc8c5335576bed7a3fdac653172f40ba05c0d6bf399`, normalized result `sha256:832995016f9adaa7171424e509a7004284a13b9d0c85fed5101f29e3623aead2`, semantic regression `sha256:d786b5911e0f9e9d2c4959cf3aa7f87d92891c1370fbb276cbf7fff3bc2d15c1`, input `sha256:3921a0ab8ed226e6a404aca6024cf28e91100f97fb51766ecd78151c9e063e44`, config `sha256:4f2e7517fbf5dae1b6fe2275ce3e7fe8873d5209f7fa5b685a2f6cef9ff7e5b8`, and statistics rows 5 / sum 510.0000 / last 104.0000 / orders 0.

## Final main-targeted integration review

PR #13 was opened directly to `main` to avoid merging historical intermediate DENY states from PRs #6/#7.

Fresh PR #13 workflows:
- `qros-gate` run `33506997060`: SUCCESS
- `lean-security-research` run `33506996973`: SUCCESS
- `lean-integration` run `33506996908`, job `99853305836`: SUCCESS

## Merge and structural verification

GitHub rejected merge method `merge` with HTTP 405; no main change occurred from that failed attempt. PR #13 was then squash-merged with expected head `7b5f89a1972fd39abb78e0ad998eacf874e42739`.

- integration commit: `744b53c18ab433346ab01fb26d35c55e5633ba43`
- accepted-head tree: `303e1c043c2e56093641073ab19156f46028acd1`
- integration-commit tree: `303e1c043c2e56093641073ab19156f46028acd1`
- tree equivalence: PASS

Historical PRs #6, #7 and #11 are closed without merge. Their branches/history were not rewritten or deleted.

## Repository governance

Repository visibility is public and consistent with ADR-0002. This closure does not change visibility.

## Hard gates

- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`

## Disposition

`PHASE_3 = ACCEPTED_MERGED_LOCAL_RESEARCH_BACKTEST_ONLY`

Next gate: Phase 4 RESEARCH → DESIGN. Phase 4 dependencies remain DENY until separately verified and pinned.
