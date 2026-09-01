# Supply-chain Baseline — Phase 1B with current Phase 3D update

Verified/established baseline: 2026-08-31. Current Phase 3D update: 2026-09-01.

## Standards and controls

- SBOM format: CycloneDX JSON 1.7.
- GitHub Actions: full-length commit SHA required by repository policy and CI validator.
- Canonical evidence: SBOM, SHA256SUMS, dependency-license manifest, source revision, build environment, provenance manifest.
- Unknown license/cost/revision: DENY introduction.
- Packaging and release remain separately denied until explicitly authorized.

## Historical Phase 1B state

At Phase 1B, only the governance/supply-chain foundation had been introduced and QuantConnect/Lean was evidence-only. That historical state is retained for chronology; it is no longer the current dependency state.

## Current Phase 3D quant-engine state

QuantConnect/Lean is now an ADOPTED exact-pinned quant-engine dependency at gitlink `b692bf4788e8b54fc23bdcb5659666bf055ce89f` under Apache-2.0.

Runtime acceptance is narrower than dependency adoption:

- unpatched upstream runtime: **DENY**
- deterministic Phase 3D checkout-time patched runtime: **ALLOW only for local Research/Backtest**
- patched Launcher NuGet graph: 55 resolved packages / 19 project nodes
- transitive license gate: PASS (44 NuGet SPDX metadata dispositions + 11 manually reviewed dispositions)
- dedicated patched Launcher CycloneDX SBOM: PASS
- packaging/release: **DENY**
- Yuanta integration/live trading: **DENY**

Canonical current details are machine-enforced by `config/dependency-registry.json`, `config/lean-security-review.json`, `config/lean-nuget-license-dispositions.json`, `supply-chain/dependency-license-manifest.json`, and the dedicated patched Launcher evidence under `supply-chain/lean/`.

## Repository source license

The repository currently has no LICENSE file. Public visibility does not create an OSS license; therefore the machine manifest records `NO_LICENSE_FILE` and makes no redistribution assumption.
