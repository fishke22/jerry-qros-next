# Phase 4 — Windows 11 x64 Local Validation Plan

Status: `PLANNED / EXECUTION DENIED UNTIL ZERO-COST REMOTE PATH IS VERIFIED`

## Scope

This plan closes the remaining physical-target evidence gap for the Phase 4 QUT desktop shell candidate.

Target only:
- Windows 11 x64
- source build / development executable for testing
- no installer, package, release, signing, updater, Yuanta, broker login, or live trading

Hard gates remain:
- `ZERO_COST_REQUIRED = true`
- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`
- `UNKNOWN != ALLOW`
- `UNKNOWN = DENY`

## Current hosted evidence already closed

Exact Phase 4 candidate head `06096a37f3cb324cd46a4bd2a3b35beec7d40f24` has successful:
- `qros-gate`
- `phase4-qut-candidate`
- `phase4-qut-cargo-sbom`

Hosted Windows evidence is not a substitute for physical Windows 11 validation because GitHub hosted validation ran on Windows Server 2025.

## Remote execution cost gate

Remote Desktop Commander is a cloud-based Remote MCP service. Public documentation identifies the local Desktop Commander MCP as free/open-source, but does not provide a sufficiently explicit Remote MCP free quota, billing cap, or no-auto-overage guarantee for this project.

The connected account exposes an authenticated online device but does not expose a verified plan, free quota, billing cap, or overage control in the account metadata available to QROS.

Decision:
- `REMOTE_DESKTOP_COMMANDER_REMOTE_MCP_COST = UNKNOWN`
- `REMOTE_DESKTOP_COMMANDER_EXECUTION = DENY`

Do not execute local commands through the hosted Remote MCP until cost status is explicitly verified as zero-cost with no automatic paid overage.

References checked 2026-09-02:
- https://desktopcommander.app/mcp/
- https://desktopcommander.app/pricing/
- https://github.com/desktop-commander/remote-desktop-commander
- https://legal.desktopcommander.app/

## Required local evidence

### 1. OS and architecture

Collect:
- Windows edition
- Windows version/build
- architecture

Acceptance:
- Windows 11
- x64 / AMD64

Fail closed on any mismatch or UNKNOWN.

### 2. Node/npm inventory

Read-only commands only.

Required candidate versions:
- Node `24.20.0`
- npm `11.19.0`

Do not install or upgrade automatically during inventory.

### 3. Rust inventory

Read-only inventory first:
- `rustc -Vv`
- `cargo -V`
- `rustup show`

Required candidate Rust version:
- Rust `1.98.0`
- target `x86_64-pc-windows-msvc`

Do not modify default toolchains during inventory.

### 4. MSVC / Visual Studio inventory

Read-only discovery only.

Collect:
- `vswhere.exe` result
- Visual Studio edition/version
- VC x86/x64 tools presence
- MSVC toolset path/version

No Visual Studio installation or component changes are authorized by this phase.

### 5. WebView2 inventory

Read-only registry/process-safe inventory only.

Collect WebView2 Evergreen Runtime version from documented Microsoft registry locations.

No download/install/update is authorized automatically.

### 6. Repository validation boundary

Allowed repository:
- `fishke22/jerry-qros-next`

Forbidden during Phase 4 local validation:
- reading or modifying `D:\YUANTA_AUTOPILOT`
- broker credentials
- certificates
- account IDs
- passwords
- tokens
- live brokerage endpoints

If local checkout state contains user changes, do not reset, clean, or overwrite them.

### 7. Source build

Only after inventory gates pass:
- exact lock verification
- `npm ci --ignore-scripts --no-audit --no-fund`
- TypeScript typecheck/build
- `cargo metadata --locked --filter-platform x86_64-pc-windows-msvc`
- `cargo build --locked`

Development executable is allowed strictly for validation.

Forbidden:
- `tauri build` if it produces bundle/installers
- MSI
- NSIS
- MSIX
- GitHub Release
- signing
- auto-update publication

### 8. Runtime smoke

Minimum smoke evidence:
- application launches on Windows 11 x64
- main zh-TW shell renders
- navigation/status surfaces render
- disabled Phase 5 functions remain disabled
- `get_shell_status` returns expected non-sensitive status
- no unexpected child process tree
- no unexpected network endpoint
- clean exit

No broker/Yuanta action is permitted.

### 9. Endpoint security validation

Collect evidence separately for:
- Windows Defender
- Norton, if installed and active on the target machine

Validation must not disable, exclude, pause, or weaken antivirus protection.

Required observations:
- source build does not trigger known malware/quarantine event
- development executable launch does not trigger quarantine
- process tree remains documented and explainable
- no injection, self-modification, hidden PowerShell, persistence, or download-and-execute behavior

Any AV detection is a blocker until independently reviewed.

## Evidence output schema

Record only non-secret evidence:

```text
PHASE4_LOCAL_VALIDATION_TIMESTAMP=
WINDOWS_EDITION=
WINDOWS_VERSION=
WINDOWS_BUILD=
ARCH=
NODE_VERSION=
NPM_VERSION=
RUSTC_VERSION=
CARGO_VERSION=
MSVC_VERSION=
WEBVIEW2_VERSION=
PACKAGE_LOCK_SHA256=
CARGO_LOCK_SHA256=
DEV_EXE_SHA256=
TYPECHECK_RESULT=
VITE_BUILD_RESULT=
CARGO_METADATA_RESULT=
CARGO_BUILD_RESULT=
RUNTIME_SMOKE_RESULT=
DEFENDER_RESULT=
NORTON_RESULT=
UNEXPECTED_NETWORK_ENDPOINTS=
UNEXPECTED_CHILD_PROCESSES=
```

Never record:
- credentials
- auth tokens
- certificate private material
- broker account identifiers
- Remote Desktop Commander auth/session identifiers

## Acceptance gate

Phase 4 physical target may advance to dependency-adoption review only if all are true:
- exact-head hosted CI remains green
- Windows 11 x64 confirmed
- toolchain inventory matches or deviations are explicitly reviewed
- WebView2 present and compatible
- exact locks unchanged
- source build passes
- runtime smoke passes
- AV validation passes or has no installed-product requirement applicable
- no new privilege/network surface appears
- no package/release artifact is produced
- no zero-cost rule is violated

Otherwise:
- `PHASE4_WINDOWS11_PHYSICAL_VALIDATION = DENY`

Passing this gate still does not authorize packaging, release, Yuanta integration, live trading, or production readiness.
