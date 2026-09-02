# ADR-0012: Phase 4 Windows-First QUT Shell Foundation

Status: PROPOSED / REVIEW REQUIRED

Date: 2026-09-02

## Context

Phase 3E is accepted and merged. The next gate is Phase 4 RESEARCH → DESIGN for the QUT desktop shell. The architecture baseline recommends Tauri 2 + React + TypeScript, but dependencies must be reverified before introduction.

## Decision candidate

Adopt a minimal Windows-first shell vertical slice with:

- Tauri core `2.11.5`;
- `tauri-build 2.6.3`;
- `@tauri-apps/cli 2.11.4`;
- `@tauri-apps/api 2.11.1`;
- React / react-dom `19.2.8`;
- TypeScript `7.0.2`;
- Vite `8.2.2`;
- Node.js `24.20.0` LTS;
- pnpm `11.25.0`;
- Rust `1.98.0`, target `x86_64-pc-windows-msvc`.

The first slice deliberately excludes FlexLayout, chart libraries, shadcn/ui, TanStack Query, i18next, and all Tauri plugins.

## Rationale

1. Tauri remains aligned with Windows 11 because it uses WebView2 and exposes a narrow Rust/native boundary.
2. React/Vite keeps the frontend conventional and testable without requiring SSR or React Server Components.
3. Node 24 LTS is preferred over Node 26 Current.
4. pnpm 11.25.0 is preferred over newly released pnpm 12.x to reduce major-version churn during the first shell slice.
5. TypeScript 7.0.2 is a current stable candidate, but it remains fail-closed until the Windows compile/integration gate proves compatibility.
6. No optional UI framework is justified before the shell itself is proven.

## Security boundary

The first QUT window must have no application/plugin IPC capability unless an explicit reviewed need appears.

Required defaults:

- local bundled assets only;
- no CDN/remote script;
- restrictive CSP;
- no updater;
- no shell/process/fs/dialog/http plugins;
- no custom command bridge;
- no arbitrary child process;
- no persistence;
- no embedded secret;
- documented network endpoint set = none for the shell slice.

Any permission expansion requires a separate reviewed change.

## Build and packaging boundary

`PACKAGE_AUTHORIZED=false` and `RELEASE_AUTHORIZED=false` remain unchanged.

Allowed validation:

- frontend typecheck/build;
- Rust `cargo check` / `cargo build`;
- Tauri `build --no-bundle`;
- development executable for tests;
- standard public GitHub Windows compile job.

Denied:

- `tauri bundle`;
- MSI/NSIS/MSIX;
- updater artifacts;
- code signing;
- GitHub Release.

## Host prerequisites

- Windows 11 x64 target;
- Evergreen WebView2 OS-managed runtime;
- Microsoft C++ toolchain via a valid zero-cost individual Visual Studio Community 2026 license;
- exact installed MSVC, Windows SDK, and WebView2 versions must be captured during Windows validation.

These host components are not treated as repo-pinned package dependencies.

## Acceptance gate for implementation authorization

Before any Phase 4 dependency becomes `ADOPTED`:

1. create exact `package.json` pins and a committed pnpm lockfile;
2. create exact Cargo.toml pins and committed Cargo.lock;
3. produce transitive SBOM and license manifest for npm + Cargo graphs;
4. reject unknown, restrictive, HIGH/CRITICAL vulnerable components;
5. pass Linux/frontend static gates where applicable;
6. pass standard public Windows x64 source compile with `--no-bundle`;
7. prove no installer/bundle/release artifact is produced;
8. verify capability/CSP fail-closed configuration;
9. record Node/pnpm/Rust/MSVC/Windows SDK/WebView2 versions;
10. review antivirus-sensitive process/network behavior.

Until then:

`PHASE4_DEPENDENCY_INTRODUCTION = DENY`

## Next gate

If this ADR and research evidence are accepted, proceed to **Phase 4A IMPLEMENT — minimal QUT shell vertical slice**. Passing that slice does not imply production readiness.
