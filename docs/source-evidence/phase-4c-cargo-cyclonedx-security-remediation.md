# Phase 4C — cargo-cyclonedx security remediation research

Verified: 2026-09-03

Status: **RESEARCH / LOCK-ONLY / NO ADOPTION**

PR #33 removed the known yanked `xml-rs 0.8.19` blocker by moving only its lock entry to `xml-rs 0.8.27`, while preserving the exact QUT CycloneDX 1.5 output.

A subsequent reachable-graph RustSec review rejected that patched graph.

## Exact security blockers

Reachable findings:

| crate | current | advisory | class | required remediation |
|---|---:|---|---|---|
| time | 0.3.36 | RUSTSEC-2026-0009 | vulnerability | >=0.3.47 |
| anyhow | 1.0.80 | RUSTSEC-2026-0190 | unsound | >=1.0.103 |
| rand | 0.8.5 | RUSTSEC-2026-0097 | unsound | 0.8.6 within 0.8 line |

These findings are not eligible for QROS warning dispositions.

Official RustSec:
- https://rustsec.org/advisories/RUSTSEC-2026-0009.html
- https://rustsec.org/advisories/RUSTSEC-2026-0190
- https://rustsec.org/advisories/RUSTSEC-2026-0097

## Dev-only warning correction

The first PR #33 traversal included development edges.

Observed unmaintained paths were:
- `number_prefix <- indicatif <- ui_test`
- `yaml-rust <- insta`

The permanent-tool graph must represent what `cargo install` compiles, therefore the revised traversal includes only Cargo metadata normal/build dependency edges and excludes dev-only edges.

This is not an advisory ignore. If either crate remains reachable through a normal/build edge, the gate fails.

## Lock-only remediation candidate

Starting lock:

`supply-chain/tool-locks/cargo-cyclonedx-0.5.9-qros.lock`

SHA-256:

`f24c56121784fe36ee9f14868b7f6386f1dd3fe640a3d2ee3e5aed4fea986e7a`

Research-only resolver updates:

```text
anyhow -> 1.0.103
rand   -> 0.8.6
time   -> 0.3.47
```

No source or manifest edits are authorized.

The resulting lock is accepted as research evidence only if:
1. changed package names are limited to the reviewed remediation closure;
2. reachable RustSec vulnerabilities/warnings are zero;
3. reachable license metadata is complete;
4. the patched tool builds with `--locked`;
5. generated QUT CycloneDX 1.5 remains byte-identical to `50e315...`.

If successful, the next step is to preserve the resulting lock as another QROS-owned immutable tool lock before any adoption decision.

```text
PERMANENT_TOOL_ADOPTION = DENY
DEPENDENCY_REGISTRY_PROMOTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
```
