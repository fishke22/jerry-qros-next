# Phase 4 — Windows 11 local validation runbook

Status: candidate runbook. This does **not** authorize packaging, release, Yuanta, or live trading.

## Purpose

Collect reproducible, sanitized evidence on the physical Windows 11 x64 target and optionally run the already-approved development/source-build smoke path.

The script is:

```text
scripts/phase4/windows11-local-validation.ps1
```

Evidence is written by default to:

```text
local-only/phase4/windows11-validation.json
```

`local-only/` is Git-ignored. Review the JSON before copying any result into durable repository evidence.

## Preconditions

1. Run from the canonical `fishke22/jerry-qros-next` checkout.
2. Use a visible PowerShell window. Do not use hidden PowerShell.
3. Do not run from or point the script at broker/Yuanta directories.
4. Do not add antivirus exclusions.
5. Packaging/release/broker/live-trading gates must remain false.
6. For `-BuildSmoke`, tracked Git files must be clean.
7. Exact Node/npm/Rust versions must already be installed:
   - Node 24.20.0
   - npm 11.19.0
   - Rust 1.98.0

## Step A — inventory only

No QROS dependency bootstrap is performed.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\phase4\windows11-local-validation.ps1
```

Review:

- Windows 11 / x64 result;
- Visual Studio / VC x86+x64 tools;
- WebView2 Evergreen version;
- Defender status;
- SecurityCenter2 antivirus product names/states;
- whether Norton/Symantec is detected.

`ExecutionPolicy Bypass` is process-scoped for this explicit visible invocation and does not modify machine policy. If local policy forbids it, use the environment approved script execution method instead.

## Step B — source-build smoke

Only after Step A is understood:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\phase4\windows11-local-validation.ps1 -BuildSmoke
```

This additionally:

- verifies exact `package-lock.json` and `Cargo.lock` SHA-256 values;
- verifies Node/npm/Rust exact versions;
- runs `npm ci --ignore-scripts --no-audit --no-fund`;
- runs TypeScript/Vite build;
- validates the locked Windows Cargo graph;
- runs `cargo build --locked` only;
- hashes the development test executable;
- fails if MSI/MSIX/setup installer artifacts appear;
- fails if tracked files change.

It does **not** run `cargo tauri build`, packaging, signing, release, updater, broker, or live-trading commands.

Dependency restoration may access only the documented npm/crates.io build endpoints if the local caches do not already contain the exact lock graph.

## Evidence review

Do not treat script exit code 0 as production readiness.

Required review fields include:

```text
target.windows_11
target.x64
visual_studio.vc_tools_x86_x64_required_component_resolved
webview2.evergreen_runtime_present
defender.query_succeeded
security_center.query_succeeded
security_center.norton_or_symantec_detected
build_smoke.performed
build_smoke.development_exe_sha256
hard_gates.*
privacy.*
```

Norton absence is not silently converted to PASS. It remains an unresolved compatibility item unless a Norton-installed target is explicitly validated.

## Fail-closed result

Until physical-target evidence is captured and reviewed:

```text
PHASE4_WINDOWS11_LOCAL_VALIDATION = DENY
DEPENDENCY_ADOPTION = DENY
MAIN_RUNTIME_PROMOTION = DENY
PRODUCTION_READINESS = DENY
```
