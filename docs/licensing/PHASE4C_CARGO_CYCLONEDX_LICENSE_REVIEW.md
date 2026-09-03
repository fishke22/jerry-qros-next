# Phase 4C — cargo-cyclonedx license review

Verified: 2026-09-03

Status: **CONSERVATIVE DOWNSTREAM DISPOSITION**

Candidate:
- `cargo-cyclonedx 0.5.9`
- exact upstream release commit: `e58bd5590212f82c5b7e16dd3e2e819b0dbea5b1`
- upstream repository: `CycloneDX/cyclonedx-rust-cargo`

## Upstream declared license

The repository and package metadata declare Apache-2.0.

The exact release source file `cargo-cyclonedx/src/main.rs` also states that the plugin was derived from `sensorfu/cargo-bom v0.3.1` and embeds the full MIT license text and SensorFu copyright notice.

Upstream issue #864 remains open and explicitly discusses whether the effective package metadata should reflect both Apache-2.0 and MIT obligations.

Official evidence:
- https://github.com/CycloneDX/cyclonedx-rust-cargo/issues/864
- https://github.com/CycloneDX/cyclonedx-rust-cargo/blob/cargo-cyclonedx-0.5.9/cargo-cyclonedx/src/main.rs
- https://github.com/sensorfu/cargo-bom/blob/master/LICENSE

## QROS disposition

QROS does not attempt to resolve the upstream legal debate in its favor.

For fail-closed compliance, QROS records:

```text
UPSTREAM_DECLARED_LICENSE = Apache-2.0
INBOUND_DERIVED_CODE_NOTICE = MIT
QROS_EFFECTIVE_LICENSE = Apache-2.0 AND MIT
MIT_NOTICE_PRESERVATION_REQUIRED = true
```

Current use is a source-built CI/research tool. QROS is not distributing the tool binary.

Any future external distribution of the tool or a bundle containing it remains DENY until a separate distribution-license review verifies all required Apache NOTICE and MIT notice obligations.

## Cost

Both Apache-2.0 and MIT permit zero-cost use, modification and redistribution subject to their conditions. No mandatory usage fee was identified.

```text
ZERO_COST_GATE = PASS_FOR_INTERNAL_SOURCE_BUILT_TOOL_CANDIDATE
EXTERNAL_DISTRIBUTION = DENY_PENDING_REVIEW
```
