# Phase 3C — LEAN dependency remediation research evidence

## Scope

Research only. No LEAN gitlink/source/dependency override was changed.

## Official upstream state — 2026-09-01

- QuantConnect/Lean `master`: `abeb0a0627ec484b92291c45c3f2553726c26199`.
- Current master still directly pins `DotNetZip 1.16.0`.
- Issue #8795 remains OPEN.
- PR #8820 (drop-in DotNetZip replacement) was closed unmerged; maintainer direction is migration to runtime `System.IO.Compression` and removal of the old dependency.
- PR #9744 was merged and moved some read/update paths to `System.IO.Compression`, but current master still contains `Ionic.Zip` usages and the package reference remains.
- A maintainer comment on #8795 associates completion of the runtime-compression migration with .NET 11 capabilities. QROS remains on .NET 10.0.400; no toolchain change is authorized.

## Exact pinned dependency audit

GitHub Actions run `33449064111`, job `99674614880`, exact QROS pin `b692bf4788e8b54fc23bdcb5659666bf055ce89f`, .NET SDK `10.0.400`.

`dotnet list ... package --vulnerable --include-transitive` reported:

| Package | Resolved | Severity | Advisory |
| --- | --- | --- | --- |
| DotNetZip | 1.16.0 | HIGH | GHSA-xhg6-9j5j-w4vf |
| System.Drawing.Common | 4.7.0 | CRITICAL | GHSA-rxg9-xrhp-64gj |
| System.Net.Http.WinHttpHandler | 4.4.0 | HIGH | GHSA-6xh7-4v2w-36q6 |
| System.Private.ServiceModel | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 |
| System.ServiceModel.Primitives | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 |

The same ServiceModel packages also carried moderate advisory GHSA-p9wx-v264-q34p.

## Root-cause mapping

### Compression cluster

`dotnet nuget why` proves:

`QuantConnect.Common → QuantConnect.Compression → DotNetZip 1.16.0`

and:

`DotNetZip 1.16.0 → System.Security.Permissions 4.7.0 → System.Windows.Extensions 4.7.0 → System.Drawing.Common 4.7.0`

Therefore removing/replacing DotNetZip at the Compression source boundary is expected to remove both the HIGH DotNetZip blocker and this CRITICAL System.Drawing path. This is a candidate hypothesis, not an implemented remediation.

### Messaging cluster

`dotnet nuget why` proves:

`QuantConnect.Messaging → NetMQ 4.0.1.6 → System.ServiceModel.Primitives 4.4.0 → System.Private.ServiceModel 4.4.0 → System.Net.Http.WinHttpHandler 4.4.0`

The standard LEAN Launcher directly references the Messaging project. Merely choosing a different runtime messaging handler does not remove the vulnerable package from the standard Launcher build.

NuGet currently lists NetMQ 4.0.4.3 (2026-07-30) with substantially newer framework dependencies. It is only a research candidate: QROS has not verified LEAN API compatibility, full security status, or LGPLv3 obligations for a new introduction decision.

## Minimal-build conclusion

No supported no-source-change escape path was demonstrated:

- Launcher directly references Compression and Messaging.
- Common directly references Compression.
- Current master still compiles remaining `Ionic.Zip` consumers.

A custom Launcher/host, package override, source patch, fork, or toolchain upgrade would change the reviewed quant-engine build and therefore requires an architecture amendment before implementation.

## Phase 3C disposition

**RESEARCH ACCEPTED / SECURITY REMEDIATION UNAVAILABLE / HARD STOP ACTIVE.**

The dependency graph and root causes are now reproducibly mapped. This does not clear ADR-0007 and does not authorize Phase 3B merge or LEAN runtime promotion.

## Official upstream re-verification — 2026-09-01T13:45+08:00

Fresh official GitHub evidence was re-queried; no cached Phase 3C conclusion was assumed.

- `master` HEAD remains `abeb0a0627ec484b92291c45c3f2553726c26199`.
- Issue #8795 remains `OPEN` (upstream `updated_at`: `2026-08-31T02:39:13Z`).
- `Compression/QuantConnect.Compression.csproj` at that exact master revision still pins `DotNetZip 1.16.0`.
- Official code search at that exact master revision still returns active `Ionic.Zip` usages, including `Compression/Compression.cs`, `Common/Data/DiskDataCacheProvider.cs`, and Engine data-feed cache/transport code.
- PR #9744 is `MERGED` (`2026-08-24T14:50:27Z`) and is still only a partial `System.IO.Compression` migration; it did not remove the DotNetZip package.
- PR #8820 remains `CLOSED / UNMERGED`; the drop-in DotNetZip-fork path is not an accepted upstream remediation.
- No newer official merged/open PR was found that removes the remaining DotNetZip package and `Ionic.Zip` dependency surface.

Fail-closed result:

```text
security_remediation_available = false
hard_stop_active = true
official_candidate_revision = DENY
```

Because condition 2 (DotNetZip blocker removed) already fails, no candidate re-pin is proposed. Conditions 3–9 are therefore not promoted to ALLOW; unproven conditions remain UNKNOWN/DENY. No LEAN source, gitlink, NuGet override, .NET toolchain, Phase 3B merge, Phase 4 work, packaging, release, Yuanta integration, or live-trading work is authorized by this re-verification.
