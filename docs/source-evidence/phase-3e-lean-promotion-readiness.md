# Phase 3E — LEAN promotion-readiness evidence

Status: PENDING_CI.

This phase inherits the user's Option B research authorization. It changes no canonical gitlink and authorizes no runtime promotion.

The principal Phase 3D source-review blocker was full-entry buffering in the QROS compatibility bridge. Phase 3E changes the experimental bridge to keep the source ZipArchive open and return ZipArchiveEntry.Open() streams on demand. Existing source entries are copied stream-to-stream during Save; only newly added caller-provided byte[] entries remain buffered.

Cloud CI will collect:
- Linux exact-toolchain security/build/quant evidence;
- standard Windows hosted-runner compatibility;
- targeted compression regressions;
- a CycloneDX 1.7 inventory generated from the patched Launcher's project.assets.json;
- license evidence extracted from restored NuGet .nuspec metadata.

Windows 11 x64 physical smoke remains PENDING and cannot be satisfied by the hosted Windows runner.

## Initial cloud evidence

Run `33456276421` completed the substantive gates before the intentionally failing promotion-deny step.

Linux job `99696792445`:
- stream-backed bridge source gate — PASS;
- patched Launcher HIGH/CRITICAL advisory audit — PASS;
- patched LEAN build — PASS;
- targeted compression regression — PASS;
- existing path-traversal/compatibility smoke — PASS;
- deterministic two-run backtest — PASS;
- normalized result hash `sha256:6605a67123b8551dab847d58efe237971e73582f7a6a3ea9946f7d1d74ac7f7d`;
- CycloneDX 1.7 patched Launcher graph — 59 components.

Windows standard job `99696792663`:
- runner image: Microsoft Windows Server 2025 / `windows-2025-vs2026`;
- patched vulnerability audit — PASS;
- patched LEAN build + compression regressions + deterministic backtest — PASS;
- normalized result hash `sha256:7b925ce0e40f81e58dfdb24b1369c8c9207aa219f1920ceb68aa80f3588098ba`;
- Windows 11 x64 physical target smoke — NOT PERFORMED.

Both normalized hashes differ because compiled assembly bytes differ across operating systems; the normalized quant statistics remain identical: rows 5, sum 510.0000, last 104.0000, total orders 0.

## License metadata reconciliation

The first generator pass identified 57/59 licenses from restored NuGet metadata and left two UNKNOWN.

- CloneExtensions 1.3.0: exact source commit `3a14000a39880cee62daa06b20dbe38a611b05aa`, dated 2017-03-12, contains `CloneExtensions.csproj` with `Version=1.3.0` and an Apache-2.0 LICENSE. Classified VERIFIED_EXACT_SOURCE_VERSION.
- AsyncIO 0.1.69: the exact NuGet page links `somdoron/AsyncIO` as project/source repository. The last observed source commit before the 2018-12-24 package publication, `0b0cf4c65b049b2e483b172e530f4db970db25e4`, carries MPL-2.0; no later repository commit was observed through 2019-01-15. Independent third-party component notices also identify AsyncIO 0.1.69 as MPL-2.0. Classified VERIFIED_WITH_SOURCE_AND_COMPONENT_NOTICE_CROSSCHECK, with the caveat that the package nuspec itself lacks usable license metadata.

These exact overrides identify license terms for research review only. They do not constitute release/redistribution clearance.

## Frozen patched supply-chain evidence

Linux run `33457059553`, job `99699166911`, reproduced the complete Phase 3E cloud path with path-normalized evidence:

- patched Launcher vulnerability audit — no HIGH/CRITICAL advisories;
- stream-backed bridge source gate — PASS;
- patched LEAN build — PASS;
- targeted compression regression — PASS;
- compression security smoke — PASS;
- deterministic quant regression — PASS;
- normalized result hash `sha256:87c031f5214f0f40589f1e232a42438e7533b2009638c3a9abf3a38b88ec8afd`;
- CycloneDX 1.7 components — 59;
- package license identification — 59/59;
- unknown licenses — 0;
- absolute runner paths in license evidence — 0;
- release clearance — false.

The generated artifacts are frozen at:
- `supply-chain/patched-lean-phase3e.cdx.json`
- `supply-chain/patched-lean-phase3e-license-review.json`

This clears the Phase 3D transitive-SBOM and unknown-license evidence blockers for research evaluation only. It does not clear physical Windows 11 validation, divergence ownership, release obligations, or promotion authorization.
