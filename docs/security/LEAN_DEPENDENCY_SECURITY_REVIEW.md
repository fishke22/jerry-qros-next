# LEAN dependency security review — Phase 3B

## Disposition

`DENY_RUNTIME_PROMOTION`

This review is fail-closed. Functional correctness does not override known HIGH/CRITICAL dependency advisories.

## Confirmed blockers

| Package | Version | Severity | Advisory | Current disposition |
| --- | --- | --- | --- | --- |
| DotNetZip | 1.16.0 | HIGH | GHSA-xhg6-9j5j-w4vf | BLOCK |
| System.Drawing.Common | 4.7.0 | CRITICAL | GHSA-rxg9-xrhp-64gj | BLOCK |
| System.Net.Http.WinHttpHandler | 4.4.0 | HIGH | GHSA-6xh7-4v2w-36q6 | BLOCK |
| System.Private.ServiceModel | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 | BLOCK |
| System.ServiceModel.Primitives | 4.4.0 | HIGH | GHSA-jc8g-xhw5-6x46 | BLOCK |

DotNetZip 1.16.0 is directly referenced by LEAN Compression. The other entries were observed by NuGet in the exact pinned build.

System.Drawing.Common CVE-2021-24112 is documented as macOS/Linux-specific. That does not make the dependency acceptable for QROS promotion: the canonical verification build currently runs on Linux and QROS requires a traceable, security-reviewed dependency graph.

## Required remediation evidence

A future promotion review requires either an official LEAN pin without these blockers, or an explicitly authorized independently reviewed engine patch/minimal build. It must also include a complete transitive NuGet SBOM and deterministic regression evidence.

No suppression such as `NoWarn=NU1903/NU1904` is accepted as remediation.
