# Phase 4 Desktop Shell Design Review Evidence

Date: 2026-09-02

Status: DESIGN ACCEPTED / IMPLEMENTATION CANDIDATE AUTHORIZED / DEPENDENCY ADOPTION DENIED

## Inputs reviewed

- PR #23 merged research head `9e5eb83e9ddc4d2a8ffbaa001a2f6a0616e4d355`.
- main research integration commit `5d00ba6d057e275fc66876deb2745fa31392eb50`.
- PR #23 qros-gate run `33622964920` — SUCCESS.
- PR #23 lean-integration run `33622964983` — SUCCESS.
- post-merge qros-gate run `33623360034` — SUCCESS.
- final Codex review on the research head reported no major issue.

## External fact re-check

Immediately before design acceptance, the researched frontend candidates were rechecked against current public package/official sources:

- React `19.2.8` — MIT.
- TypeScript `7.0.2` — Apache-2.0.
- Vite `8.2.2` — MIT.
- `@vitejs/plugin-react 6.1.1` — MIT.
- `@tauri-apps/api 2.11.1` — MIT OR Apache-2.0.
- `@types/react 19.2.18` and `@types/react-dom 19.2.5` — MIT.
- Node.js `24.20.0` remains the LTS candidate with bundled npm `11.19.0`.
- Rust `1.98.0` remains the stable candidate.
- Tauri Windows prerequisites still require Microsoft C++ Build Tools and WebView2.
- Windows 11 includes the Evergreen WebView2 Runtime; its exact installed runtime version is intentionally treated as environment inventory, not a source dependency pin.

The research record remains authoritative for full URLs and advisory detail.

## Review conclusion

The architecture is accepted for a single minimal vertical slice:

- Tauri Rust shell with no domain logic.
- React client-side SPA only.
- Vite development/build tooling.
- TypeScript candidate compile validation.
- npm and Cargo exact lockfiles.
- system WebView2 Evergreen.
- Windows 11 x64 / MSVC only.

The following distinction is mandatory:

`IMPLEMENTATION_CANDIDATE_AUTHORIZED != DEPENDENCY_ADOPTION_AUTHORIZED`

A feature branch may now create exact manifests, resolve lockfiles, compile the shell, and collect supply-chain evidence. No dependency may be promoted to `ADOPTED` and no Phase 4 runtime may be merged to main until the promotion gate passes.

## Fail-closed blockers carried into implementation

- TypeScript 7.0.2 exact-graph compatibility is still UNVERIFIED.
- exact npm transitive graph and integrity values are UNKNOWN until lock generation.
- exact Cargo transitive graph/checksums are UNKNOWN until lock generation.
- exact installed MSVC toolset is UNKNOWN until Windows inventory.
- exact installed WebView2 Evergreen version is UNKNOWN until Windows inventory.
- exact final CSP is UNKNOWN until generated shell review.

Each remains `UNKNOWN = DENY` for runtime promotion.

## Required implementation evidence

1. exact direct versions with no floating ranges;
2. package-lock.json and npm integrity evidence;
3. npm audit with incomplete evidence rejected;
4. rust-toolchain.toml pinned to Rust 1.98.0;
5. Cargo direct dependencies pinned with exact `=` requirements;
6. Cargo.lock and resolved crate graph;
7. Rust malicious-crate deny validation;
8. Cargo/npm license and vulnerability closure;
9. complete npm/Cargo SBOM before adoption;
10. TypeScript 7 exact-graph compile validation;
11. Vite bound only to 127.0.0.1 with strictPort;
12. restrictive CSP and minimal local-only Tauri capabilities;
13. no shell/fs/http/updater/opener/process plugins;
14. Windows 11 x64 source-build smoke;
15. observed MSVC and WebView2 environment inventory;
16. antivirus compatibility review.

## Cost and hard gates

- incremental design-review cost: 0;
- only standard public GitHub runners may be used;
- no scheduled Windows workflow;
- no paid/larger/GPU runner;
- no installer/package/release/signing;
- no Yuanta integration;
- no live trading.

## Decision

`PHASE_4_RESEARCH = ACCEPTED`

`PHASE_4_DESIGN = ACCEPTED`

`PHASE_4_IMPLEMENTATION_CANDIDATE = AUTHORIZED_ON_FEATURE_BRANCH`

`PHASE_4_DEPENDENCY_ADOPTION = DENY_PENDING_IMPLEMENTATION_EVIDENCE`

`PHASE_4_MAIN_RUNTIME_PROMOTION = DENY_PENDING_IMPLEMENTATION_REVIEW`

This is not a production-readiness claim.
