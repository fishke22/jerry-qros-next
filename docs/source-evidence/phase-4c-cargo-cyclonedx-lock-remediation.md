# Phase 4C — cargo-cyclonedx lock-only remediation research

Verified: 2026-09-03

Status: **RESEARCH / NOT PERMANENT ADOPTION**

## Why this research exists

Phase 4C semantic-fidelity conversion passed with:
- exact QUT CycloneDX 1.5 input SHA-256 `50e315c02680106ff3004e6e194f58d4cbbd8732fab33aff08ff122972da3623`
- canonical CycloneDX 1.7 output SHA-256 `b1bee226f7df007a243b6114c13fe1e22f5e0e2083f26ae261a68357b419d668`

The remaining permanent-toolchain blocker is the input generator.

Official upstream state on 2026-09-03:
- latest `cargo-cyclonedx` release remains `0.5.9` from 2026-03-19;
- exact release commit: `e58bd5590212f82c5b7e16dd3e2e819b0dbea5b1`;
- upstream main still locks `xml-rs 0.8.19`;
- native CycloneDX 1.6/1.7 support remains open in PR #872.

Official references:
- https://github.com/CycloneDX/cyclonedx-rust-cargo/releases/tag/cargo-cyclonedx-0.5.9
- https://github.com/CycloneDX/cyclonedx-rust-cargo/pull/872

## Lock-only remediation hypothesis

The exact source declares `xml-rs = "0.8.16"`, so a later compatible 0.8.x can be selected without changing source code.

This research tests exactly:

```text
xml-rs 0.8.19 (yanked)
→ xml-rs 0.8.27
```

Allowed change:
- the `xml-rs` package entry in upstream `Cargo.lock`.

Denied:
- any Rust source edit;
- any manifest dependency edit;
- any additional package/version drift;
- disabling `--locked`;
- accepting a different QUT SBOM hash.

The patched tool must build using the resulting exact lock and must regenerate the same QUT CycloneDX 1.5 bytes.

## License review

Upstream declares Apache-2.0, but issue #864 remains open because `cargo-cyclonedx` was derived from MIT-licensed `sensorfu/cargo-bom`.

The exact 0.5.9 `cargo-cyclonedx/src/main.rs` contains:
- Apache-2.0 header;
- acknowledgement of `sensorfu/cargo-bom v0.3.1`;
- the full MIT license text and SensorFu copyright notice.

QROS therefore uses the conservative downstream disposition:

```text
CARGO_CYCLONEDX_EFFECTIVE_LICENSE = Apache-2.0 AND MIT
MIT_NOTICE_PRESERVATION_REQUIRED = true
```

This avoids relying on the unresolved upstream metadata interpretation.

Official issue:
- https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/864

## Decision boundary

```text
LOCK_ONLY_REMEDIATION_RESEARCH = ALLOW
PATCHED_TOOL_BUILD_TEST = ALLOW
PATCHED_TOOL_SBOM_FIDELITY_TEST = ALLOW

PATCHED_LOCK_ADOPTION = DENY_PENDING_EVIDENCE
PERMANENT_TOOL_ADOPTION = DENY
DEPENDENCY_REGISTRY_PROMOTION = DENY
CANONICAL_SBOM_1_7_PROMOTION = DENY
PACKAGE/RELEASE/YUANTA/LIVE = DENY
```
