# ADR-0012: Phase 4 Windows Desktop Shell Foundation

Status: ACCEPTED / IMPLEMENTATION CANDIDATE ONLY

Date: 2026-09-02

## Context

Phase 3E is accepted and merged. The next roadmap gate is Phase 4 `RESEARCH → DESIGN` for a Windows 11 x64, local-first, zh-TW-first desktop shell.

The architecture baseline named Tauri/React as the preferred shell, but Phase 4 dependencies were intentionally left `PLANNED_DENY_USE_UNTIL_PINNED`. Current versions, licenses, Windows prerequisites, security advisories, system-runtime assumptions, and supply-chain risks therefore had to be independently revalidated before implementation.

Research evidence is recorded in:

- `config/phase4-desktop-shell-research.json`
- `docs/source-evidence/phase-4-desktop-shell-research.md`

This ADR was proposed without implementation authority. The design review recorded in `config/phase4-desktop-shell-design.json` now authorizes only construction and validation of a minimal implementation candidate on a feature branch; dependency adoption and main runtime promotion remain denied.

## Decision

### 1. Keep the first vertical slice deliberately small

The first Phase 4 implementation candidate is limited to:

- Tauri 2
- React / React DOM client-side SPA
- TypeScript
- Vite / @vitejs/plugin-react
- React type definitions
- Node LTS with npm
- Rust stable with the MSVC target
- system Microsoft Edge WebView2 Evergreen Runtime

Do not introduce workspace-layout, charting, component-kit, query-state, or i18n frameworks in the first slice.

### 2. Windows-only implementation

The active desktop target is:

`Windows 11 x64 / x86_64-pc-windows-msvc`

No Linux or macOS desktop implementation, CI matrix, package, or release is introduced by Phase 4.

### 3. System WebView2, not a bundled Fixed Version runtime

Use the Windows system Evergreen WebView2 Runtime.

- Do not redistribute Fixed Version WebView2.
- Do not download or install WebView2 automatically.
- Treat missing WebView2 as a startup/validation failure.
- Record the observed WebView2 version during authorized Windows validation.
- Do not treat the observed Evergreen version as a source dependency pin.

This avoids prematurely creating a large proprietary runtime distribution and packaging obligation.

### 4. Local static SPA only

The Phase 4 shell is a local static SPA.

Forbidden in the first slice:

- SSR
- React Server Components
- React Server Functions
- react-server-dom-* packages
- remote scripts/CDNs
- remote webview content
- remote Tauri capability URLs

Production shell operation must not require an outbound network endpoint.

### 5. Minimal Tauri authority

The shell must use explicit least-privilege capabilities.

The first slice does not introduce:

- shell plugin
- filesystem plugin
- HTTP plugin
- updater plugin
- opener plugin
- process plugin

No capability may grant remote content access to local IPC.

No arbitrary process spawning or download-and-execute behavior is permitted.

### 6. CSP is mandatory

The Tauri shell must define and test a restrictive Content Security Policy.

The exact final CSP remains implementation evidence, not research speculation. It must deny remote scripts and remote CDN dependencies and permit only resources actually required by the generated local shell.

### 7. Loopback-only Vite development server

Development configuration must:

- bind only to `127.0.0.1`
- use `strictPort: true`
- never use `--host` or LAN exposure
- avoid broad frontend exposure of `TAURI_` environment variables
- contain no secrets

Production uses built static assets and not the Vite dev server.

### 8. Toolchain candidates are researched, not adopted

Research candidates:

- Node.js 24.20.0 LTS / npm 11.19.0
- Rust 1.98.0 / target `x86_64-pc-windows-msvc`
- Tauri core 2.11.5
- tauri CLI 2.11.4
- @tauri-apps/api 2.11.1
- tauri-build 2.6.3
- React / React DOM 19.2.8
- TypeScript 7.0.2
- Vite 8.2.2
- @vitejs/plugin-react 6.1.1
- @types/react 19.2.18
- @types/react-dom 19.2.5

Every research item remains `use_authorized=false` in the immutable research record. Design acceptance permits exact candidate resolution only on a feature branch; it does not promote any item to `ADOPTED`.

TypeScript 7.0.2 is especially conditional because the exact QROS React/Vite/Tauri graph has not yet been compile-validated with the native TypeScript 7 compiler.

### 9. Exact lockfiles are an implementation gate

Before any candidate can be promoted to `ADOPTED`, the implementation candidate must generate and review:

- exact package versions without floating ranges
- `package-lock.json`
- npm integrity/resolution evidence
- `rust-toolchain.toml`
- `Cargo.lock`
- complete resolved npm and Cargo dependency graphs
- license evidence
- vulnerability evidence
- SBOM evidence

Missing audit evidence is DENY.

### 10. Rust malicious-crate deny set is mandatory

The implementation gate must reject the 2026-08-20 malicious/compromised crate set recorded in `config/phase4-desktop-shell-research.json`, including `arrayref@0.3.10` and the other named entries.

### 11. Existing Phase 4 dependency registry remains unchanged

Research does not convert any `config/dependency-registry.json` Phase 4 candidate to `ADOPTED`.

Existing Phase 4 records remain:

`PLANNED_DENY_USE_UNTIL_PINNED`

with introduction authorization false until implementation lock/provenance review succeeds.

## Security boundaries

The Phase 4 shell must not:

- connect to Yuanta or any broker
- contain broker credentials
- enable live trading
- create an updater/release channel
- perform hidden PowerShell
- perform process/DLL injection
- download and execute arbitrary binaries
- create undocumented persistence
- expose development servers to the LAN
- embed secrets in JavaScript/frontend assets

## Cost and licensing

Research identified a zero-license-cost candidate path for the current individual/single-user scenario using permissive OSS plus Visual Studio Community/MSVC tooling and the system WebView2 Runtime.

This is not a blanket future organizational license determination. If project usage changes from the current individual scenario, Microsoft tool licensing must be re-reviewed.

No paid service, paid runner, cloud runtime, or code signing is introduced.

## Packaging boundary

Phase 4 may produce only source builds and a development executable when strictly required for testing.

Still prohibited:

- MSI
- NSIS
- MSIX
- production EXE packaging
- GitHub Release
- auto-update channel
- release signing

MSI-specific VBSCRIPT setup is therefore not part of Phase 4.

## Design review acceptance

Design review accepted the architecture because:

1. PR #23 research evidence passed qros-gate, lean-integration, post-merge qros-gate, and final review with no major issue;
2. current package/source re-checks remained consistent with the research candidate;
3. the minimal slice defers nonessential UI/chart/query/i18n and privileged Tauri plugins;
4. exact npm/Cargo graphs, TypeScript 7 compile compatibility, MSVC inventory, WebView2 inventory, and final CSP remain explicit fail-closed promotion gates;
5. dependency-registry entries remain deny-only and are not promoted by design acceptance.

## Authorized next gate

`Phase 4 DESIGN = ACCEPTED`

`Phase 4 IMPLEMENTATION_CANDIDATE = AUTHORIZED_ON_FEATURE_BRANCH`

`Phase 4 DEPENDENCY_ADOPTION = DENY_PENDING_IMPLEMENTATION_EVIDENCE`

`Phase 4 MAIN_RUNTIME_PROMOTION = DENY_PENDING_IMPLEMENTATION_REVIEW`

The implementation candidate must begin on a new feature branch and prove exact lockfiles, source-build compatibility, supply-chain/license closure, Windows toolchain inventory, CSP/capability boundaries, and zero-cost compliance.

Passing design or implementation tests alone is not production readiness.
