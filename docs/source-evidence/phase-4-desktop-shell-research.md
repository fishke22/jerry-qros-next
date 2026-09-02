# Phase 4 Desktop Shell Research Evidence

Date: 2026-09-02

Status: RESEARCH COMPLETE / DESIGN PROPOSED / IMPLEMENTATION NOT AUTHORIZED

Target: Windows 11 x64 only.

## Scope

This evidence evaluates the minimum zero-cost desktop-shell stack for Phase 4. It does not authorize dependency introduction, application implementation, packaging, release, Yuanta integration, or live trading.

The proposed first vertical slice is intentionally limited to:

- Tauri 2 desktop shell
- React client-side SPA
- Vite build/dev tooling
- TypeScript tooling
- npm package management
- Rust/MSVC/Node toolchains
- the system-installed Microsoft Edge WebView2 Evergreen Runtime

Workspace layout libraries, financial/analytics chart libraries, component kits, API-state libraries, i18n frameworks, and privileged Tauri plugins are deferred.

## Official evidence

### Tauri and Windows prerequisites

Official Tauri prerequisites state that Windows development requires Microsoft C++ Build Tools and Microsoft Edge WebView2. Tauri requires Rust and recommends the Node.js LTS line when a JavaScript frontend is used. The Windows MSVC host triple is required for full Tauri support.

Source:
- https://tauri.app/start/prerequisites/

Tauri's current ecosystem release page reported on 2026-09-02:

- tauri crate 2.11.5
- tauri-cli crate 2.11.4
- @tauri-apps/cli npm 2.11.4
- @tauri-apps/api npm 2.11.1
- tauri-build crate 2.6.3

Source:
- https://tauri.app/release/

Tauri declares MIT / Apache-2.0 licensing.

Source:
- https://github.com/tauri-apps/tauri

### Tauri security boundary

Tauri permissions are explicit command privileges, optionally scoped, and capabilities bind permissions to windows/webviews. Remote capability URLs are optional and the documented default use case is locally served application content.

Sources:
- https://tauri.app/security/permissions/
- https://tauri.app/reference/acl/capability/

QROS Phase 4 therefore proposes:

- local content only
- no remote capability URLs
- no remote scripts/CDNs
- no privileged Tauri plugins in the first slice
- minimal explicit capabilities
- CSP required
- no automatic updater

A 2026 Tauri advisory, GHSA-7gmj-67g7-phm9 / CVE-2026-42184, affected tauri >=2.0 through 2.11.0 on Windows/Android due to origin confusion that could expose local-only IPC commands to remote pages. The patched floor is 2.11.1. Candidate tauri 2.11.5 is above that floor, but exact implementation must still re-run current advisory checks.

Source:
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-7gmj-67g7-phm9

### WebView2

Microsoft documents Evergreen WebView2 as the recommended model for most apps. It updates automatically and is preinstalled on Windows 11. A Fixed Version runtime must be distributed with the application and adds roughly 100–250 MB.

Source:
- https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/webview2

Decision candidate:

- use the Windows system Evergreen Runtime
- do not redistribute Fixed Version WebView2
- do not auto-download a missing runtime
- fail closed with a visible error if the runtime is unavailable
- record the observed Evergreen version during authorized Windows validation
- exact WebView2 version remains intentionally UNKNOWN until runtime inventory

### Visual Studio / MSVC zero-cost status

Tauri requires Microsoft C++ Build Tools on Windows. Microsoft states that an individual developer may use Visual Studio Community to create their own free or paid applications.

Source:
- https://visualstudio.microsoft.com/vs/community/

For the current single-user project this provides a zero-license-cost candidate path for the C++ workload. Exact installed Visual Studio/MSVC toolset versions are UNKNOWN until Windows inventory and remain a pre-implementation gate.

MSI/VBSCRIPT prerequisites are explicitly outside Phase 4 because packaging is not authorized.

### React

npm and React upstream release evidence report React and React DOM 19.2.8 as the current stable line, with MIT licensing.

Sources:
- https://www.npmjs.com/package/react
- https://www.npmjs.com/package/react-dom
- https://github.com/facebook/react/releases

React Server Components and Server Functions had multiple 2025–2026 security advisories, including CVE-2026-44907. The 19.2 patched line for that advisory is 19.2.8. React's own security guidance also states that applications not using a server/RSC path are outside those RSC vulnerabilities.

Sources:
- https://github.com/react/react/security/advisories/GHSA-wx67-qw84-cm4g
- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components

Phase 4 therefore uses a local client SPA only and explicitly forbids:

- React Server Components
- React Server Functions
- react-server-dom-* packages
- SSR/server rendering architecture

### TypeScript

npm reports TypeScript 7.0.2 as the current stable package. Microsoft describes TypeScript 7 as a native Go port designed to preserve compiler behavior while providing large performance gains. TypeScript is Apache-2.0 licensed.

Sources:
- https://www.npmjs.com/package/typescript
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://github.com/microsoft/TypeScript/blob/main/LICENSE.txt

TypeScript 7.0.2 is only a candidate. The QROS React/Vite/Tauri graph has not been compiled with it yet. Current DefinitelyTyped package tags explicitly advertise React DOM compatibility through the TS 6.0 tag, not a TS7-specific tag. This is not evidence of incompatibility, but it is insufficient evidence to declare compatibility.

Therefore:

`TYPESCRIPT_7_QROS_COMPATIBILITY = UNVERIFIED / DENY UNTIL COMPILE VALIDATION`

### React type definitions

Current npm evidence:

- @types/react 19.2.18 — MIT
- @types/react-dom 19.2.5 — MIT

Sources:
- https://www.npmjs.com/package/@types/react
- https://www.npmjs.com/package/@types/react-dom

### Vite

npm reports Vite 8.2.2 as current and MIT licensed. Vite 8 uses Rolldown for production bundling.

Source:
- https://www.npmjs.com/package/vite

A 2026 high-severity Windows advisory, GHSA-fx2h-pf6j-xcff / CVE-2026-53571, affected Vite 8.0.0 through 8.0.15; the 8.x patched floor is 8.0.16. The described impact requires exposing the dev server to the network.

Source:
- https://github.com/vitejs/vite/security/advisories/GHSA-fx2h-pf6j-xcff

QROS controls:

- candidate Vite 8.2.2
- bind dev server to 127.0.0.1 only
- strictPort = true
- never use --host/network exposure
- no secrets in frontend environment
- do not expose a broad TAURI_ environment prefix

Current @vitejs/plugin-react npm evidence reports 6.1.1, MIT.

Source:
- https://www.npmjs.com/package/@vitejs/plugin-react

### Node.js and npm

Tauri recommends Node LTS. Node's official archive reports Node 24.20.0 (Krypton) with npm 11.19.0 and a Windows x64 artifact.

Source:
- https://nodejs.org/download/archive/v24.20.0

Node.js is MIT licensed, with third-party license notices.

Source:
- https://github.com/nodejs/node/blob/main/LICENSE

Phase 4 design uses npm rather than introducing pnpm/yarn/corepack as another toolchain.

### Rust and Cargo

The Rust project released Rust 1.98.0 on 2026-08-20. Rust is dual licensed MIT OR Apache-2.0 except where third-party notices apply.

Sources:
- https://blog.rust-lang.org/releases/latest/
- https://github.com/rust-lang/rust/blob/main/COPYRIGHT

Rust 1.96 contained fixes for Cargo CVE-2026-5222 and CVE-2026-5223; candidate 1.98.0 is newer than that security floor.

Sources:
- https://blog.rust-lang.org/2026/05/28/Rust-1.96.0/
- https://blog.rust-lang.org/2026/05/25/cve-2026-5222/
- https://blog.rust-lang.org/2026/05/25/cve-2026-5223/

On 2026-08-20, the Rust Security Response Team disclosed a supply-chain attack involving malicious or compromised crates. The exact deny set for QROS Phase 4 research is:

- arrayref 0.3.10
- append-only-vec 0.1.9
- internment 0.8.7
- proc-macro1 any version
- proc-macro-en any version
- aovine any version
- arone any version
- aronenao any version
- tinymember any version

Source:
- https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/

Implementation must commit Cargo.lock, examine the resolved crate graph, and fail if any denied entry is present.

## Minimal dependency decision candidate

Initial Phase 4 implementation candidate:

1. Tauri
2. React / React DOM
3. TypeScript
4. Vite / @vitejs/plugin-react
5. React type definitions
6. Node LTS + bundled npm
7. Rust stable + MSVC
8. system WebView2 Evergreen

Explicitly deferred:

- FlexLayout
- Lightweight Charts
- ECharts
- shadcn/ui
- TanStack Query
- i18next
- Tauri shell/fs/http/updater/opener/process plugins

The shell must not require network access in its production/static mode.

## Lock and provenance policy for the next gate

Implementation may not begin dependency use until it can produce and review:

- exact package.json versions with no floating ranges
- package-lock.json
- npm resolved integrity evidence
- rust-toolchain.toml pinned to the approved Rust version
- Cargo.lock
- resolved npm and Cargo SBOM/license evidence
- current vulnerability/advisory evidence
- malicious-crate deny validation
- exact Windows MSVC/WebView2 environment inventory
- Windows source-build smoke evidence

No installer, MSI, NSIS, MSIX, updater, signing, or release artifact is authorized.

## UNKNOWN / unresolved

- exact installed Microsoft C++/MSVC toolset version
- exact installed WebView2 Evergreen version
- TypeScript 7.0.2 compatibility with the final exact React/Vite/Tauri graph
- final npm transitive dependency graph and integrity values
- final Cargo transitive dependency graph and checksums
- exact CSP required by the final generated Tauri shell

Fail-closed disposition:

`UNKNOWN = DENY`

## Research decision

`PHASE_4_RESEARCH = COMPLETE`

`PHASE_4_DESIGN = PROPOSED_FOR_REVIEW`

`PHASE_4_IMPLEMENTATION = DENY_PENDING_DESIGN_REVIEW_AND_EXACT_LOCK_VALIDATION`

`PHASE_4_DEPENDENCY_INTRODUCTION = DENY`
