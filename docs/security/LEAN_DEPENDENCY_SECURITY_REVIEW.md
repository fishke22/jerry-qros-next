# LEAN dependency security review — Phase 3D acceptance

## Disposition

`ALLOW_LOCAL_RESEARCH_BACKTEST_WITH_PHASE3D_PATCH_ONLY`

The exact unmodified upstream LEAN revision remains `DENY` because its baseline graph contains known HIGH/CRITICAL dependency findings. QROS accepts only the deterministic checkout-time Phase 3D runtime overlay validated by repository gates.

## Baseline blockers retained as evidence

| Package | Baseline version | Severity | Advisory | Phase 3D patched runtime |
| --- | --- | --- | --- | --- |
| DotNetZip | 1.16.0 | HIGH | GHSA-xhg6-9j5j-w4vf | ABSENT |
| System.Drawing.Common | 4.7.0 | CRITICAL | GHSA-rxg9-xrhp-64gj | ABSENT |
| System.Net.Http.WinHttpHandler | 4.4.0 | HIGH | GHSA-6xh7-4v2w-36q6 | ABSENT |
| System.Private.ServiceModel | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 | ABSENT |
| System.ServiceModel.Primitives | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 | ABSENT |

These rows describe the denied baseline upstream graph; they do not claim the original LEAN revision was remediated upstream.

## Accepted patched runtime evidence

The accepted QROS runtime overlay leaves `external/lean` at `b692bf4788e8b54fc23bdcb5659666bf055ce89f`, applies an exact-anchor checkout-time patch, freezes a 55-package / 19-project NuGet graph, verifies all 55 package licenses, verifies a dedicated 55-package CycloneDX SBOM, rejects any NuGet HIGH/CRITICAL vulnerability record, builds the standard Launcher and QROS synthetic algorithm with zero errors, runs the deterministic backtest twice, and preserves the Phase 3B semantic regression hash.

Exact prerequisite head `4050b640f54fab9b0fda28c7d73145a0e44a4294` passed both `qros-gate` and `lean-integration`.

## Fail-closed boundary

Runtime ALLOW applies only to:

`LOCAL_RESEARCH_BACKTEST_RUNTIME_ONLY_WITH_PHASE3D_PATCH`

Any unknown or drift in the patch, graph, license evidence, SBOM, vulnerability audit, regression evidence, or hard gates returns to DENY.

Warning suppression such as `NoWarn=NU1903/NU1904` remains prohibited. Packaging, release, Yuanta integration, broker credentials, broker login, and live trading remain unauthorized.
