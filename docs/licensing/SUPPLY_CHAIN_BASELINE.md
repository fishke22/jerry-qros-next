# Supply-chain Baseline — Phase 1B

Verified/established 2026-08-31.

## Standards and controls

- SBOM format: CycloneDX JSON 1.7.
- GitHub Actions: full-length commit SHA required by repository policy and CI validator.
- Candidate evidence: SBOM, SHA256SUMS, dependency-license manifest, source revision, build environment, provenance manifest.
- Unknown license/cost/revision: DENY introduction.
- No product runtime dependency exists in Phase 1B.

## Current adopted dependency

| Component | Revision | Role | License | Cost | Status |
|---|---|---|---|---|---|
| actions/checkout | de0fac2e4500dabe0009e67214ff5f5447ce83dd (v6.0.2) | CI-only | MIT | public standard CI / no extra charge | ADOPTED |

QuantConnect/Lean remains evidence-only and is not introduced. All later architecture-listed runtime components remain UNSPECIFIED and denied until their own phase verifies official source, current version, license and zero-cost status.

## Repository source license

The repository currently has no LICENSE file. Public visibility does not create an OSS license; therefore the machine manifest records `NO_LICENSE_FILE` and makes no redistribution assumption.
