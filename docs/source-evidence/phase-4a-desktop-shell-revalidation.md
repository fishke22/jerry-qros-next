# Phase 4A Desktop Shell Revalidation — 2026-09-02

Status: REVALIDATED / RESEARCH HARDENING ONLY

Baseline main: `aa2f149e916e5a3d47114ed2e0d3df6a9f5542ae`

This document does not reopen or duplicate the already-merged Phase 4 research/design work. It verifies that PR #23 and PR #24 are legitimate successors to the Phase 3E baseline and records one material zero-cost licensing refinement before implementation begins.

## Canonical repository re-check

- repository: `fishke22/jerry-qros-next`
- default branch: `main`
- current main at revalidation start: `aa2f149e916e5a3d47114ed2e0d3df6a9f5542ae`
- repository visibility: `public`
- visibility is governed by accepted ADR-0002, so this is not unknown drift
- Phase 4 research PR #23 merged as `5d00ba6d057e275fc66876deb2745fa31392eb50`
- Phase 4 design PR #24 merged as current main
- exact LEAN gitlink remains `b692bf4788e8b54fc23bdcb5659666bf055ce89f`
- hard gates remain closed:
  - `PACKAGE_AUTHORIZED=false`
  - `RELEASE_AUTHORIZED=false`
  - `YUANTA_INTEGRATION_AUTHORIZED=false`
  - `LIVE_TRADING_AUTHORIZED=false`

Directly observed PR-head CI:
- PR #23 head `9e5eb83e9ddc4d2a8ffbaa001a2f6a0616e4d355`
  - qros-gate 33622964920: SUCCESS
  - lean-integration 33622964983: SUCCESS
- PR #24 head `37438ef40b57559c7a174e4d68eca0eef790d574`
  - qros-gate 33626605535: SUCCESS
  - lean-security-research 33626605547: SUCCESS
  - lean-integration 33626605553: SUCCESS

The GitHub connector used for the re-check only returns pull-request-triggered workflow runs for a commit. Therefore current-main post-merge CI is not independently asserted by this document unless separately available as repository evidence.

## Official-source revalidation

### Tauri

Observed current candidate versions remain consistent with official/public upstream evidence:

- tauri 2.11.5
- @tauri-apps/cli 2.11.4
- @tauri-apps/api 2.11.1
- Tauri licensing: MIT OR Apache-2.0

Official sources:
- https://tauri.app/release/tauri/all-versions/
- https://www.npmjs.com/package/@tauri-apps/cli
- https://www.npmjs.com/package/@tauri-apps/api
- https://tauri.app/start/prerequisites/
- https://tauri.app/security/permissions/
- https://tauri.app/reference/acl/capability/
- https://tauri.app/security/csp/
- https://tauri.app/distribute/windows-installer/
- https://v2.tauri.app/plugin/updater/

Tauri capabilities remain a strong fit for fail-closed QROS boundaries because a window/webview that matches no capability has no IPC access. The first slice therefore keeps explicit local-only capabilities and does not add shell, filesystem, HTTP, updater, opener, or process plugins.

MSI/NSIS and updater capabilities exist upstream but are RESEARCH-ONLY for QROS. Packaging, update channels, signing, and release remain denied.

### React

- stable release observed: React 19.2.8
- license: MIT
- use: client-only local SPA

Official sources:
- https://github.com/facebook/react/releases
- https://github.com/facebook/react

QROS continues to forbid SSR, React Server Components, React Server Functions, `react-server-dom-*`, remote scripts, and remote CDN content in Phase 4.

### TypeScript

- npm stable observed: 7.0.2
- license: Apache-2.0

Official sources:
- https://www.npmjs.com/package/typescript
- https://github.com/microsoft/TypeScript/blob/main/LICENSE.txt

Decision remains fail-closed: TypeScript 7 is a candidate only. Exact QROS React/Vite/Tauri compatibility remains UNVERIFIED until the resolved graph compiles successfully.

### Vite

- stable observed: 8.2.2
- license: MIT
- current production build uses Rolldown

Official source:
- https://www.npmjs.com/package/vite

Vite remains build/dev tooling only. Development must bind to `127.0.0.1`, use `strictPort=true`, avoid LAN exposure, and production must use built static assets with no Vite process.

### Node.js and npm

- Node LTS candidate: 24.20.0 (Krypton)
- Windows x64 distribution is available
- npm candidate: 11.19.0
- npm application license: Artistic-2.0

Official sources:
- https://nodejs.org/download/release/latest-krypton/
- https://github.com/npm/cli/blob/latest/LICENSE
- https://docs.npmjs.com/cli/commands/npm-ci/

`npm ci` requires a committed lockfile and fails rather than rewriting a mismatched `package-lock.json`. This is adequate for the minimal first slice. pnpm is therefore not required.

Node and npm are BUILD/DEV ONLY. They must not appear in the production QROS process tree.

### Rust

- stable observed: Rust 1.98.0, released 2026-08-20
- license: MIT OR Apache-2.0, with third-party license metadata

Official sources:
- https://blog.rust-lang.org/2026/08/20/Rust-1.98.0/
- https://rust-lang.org/policies/licenses/

The existing 2026-08-20 malicious-crate deny set remains mandatory. `Cargo.lock`, exact direct requirements, vulnerability evidence, license closure, and resolved-graph review remain implementation gates.

### Microsoft Edge WebView2 Runtime

Microsoft continues to recommend Evergreen for most applications. The Evergreen Runtime is preinstalled on Windows 11 and cannot be source-pinned to a single exact runtime version; Fixed Version transfers servicing and packaging responsibility to the application.

Official sources:
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/evergreen-vs-fixed-version
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/release-notes/runtime/
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/process-model
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/measures

Latest stable runtime listed by Microsoft at revalidation time: 151.0.4129.50 (2026-08-03). QROS does not pin that number; it records the installed Evergreen version during Windows validation.

Expected process model must be documented honestly. The QROS host executable will be accompanied by WebView2 child processes. Microsoft documents a WebView2 process group with one browser process, one or more renderers, and helper processes such as GPU/audio/network/Crashpad depending on use. This is normal and must not be mistaken for opaque QROS daemons.

QROS antivirus rules remain:
- do not inject DLLs
- do not terminate or hook WebView2 child processes
- do not hide PowerShell
- do not download-and-execute
- do not runtime-unpack-and-execute
- no undocumented persistence

### Microsoft C++ toolchain — material license refinement

Tauri requires the Windows C++/MSVC toolchain.

Microsoft explicitly states that any individual developer may use Visual Studio Community to create their own free or paid applications.

Official sources:
- https://visualstudio.microsoft.com/vs/community/
- https://visualstudio.microsoft.com/license-terms/
- https://learn.microsoft.com/en-us/visualstudio/releases/2026/vs-system-requirements

However, standalone Build Tools are governed by separate Microsoft terms and should not be treated as independently free in all circumstances merely because the download is available. Microsoft licensing guidance ties Build Tools usage to a valid Visual Studio license basis, with specific open-source dependency exceptions in licensing materials.

Therefore the fail-closed QROS interpretation is:

- `Visual Studio Community 2026 + Desktop development with C++`:
  `ACCEPT_CURRENT_INDIVIDUAL_USE_SCOPE`
- standalone `Build Tools for Visual Studio 2026`:
  `DENY_UNLESS_VALID_LICENSE_BASIS_VERIFIED`

This is a licensing hardening, not a desktop architecture replacement.

## Alternative shell review

| Candidate | Official current state | Phase 4 decision | Reason |
|---|---|---|---|
| Tauri 2 | stable 2.x, system webview, Rust host | ACCEPT candidate | smallest accepted privilege/runtime model; explicit capability boundary |
| Electron | mature, Chromium + Node multi-process | REJECT first slice | Node main process and bundled browser/runtime surface are unnecessary for QROS |
| Wails v3 | beta | DEFER | pre-release and adds Go toolchain |
| Wails v2 | stable | NOT SELECTED | credible WebView2 alternative, but adds Go without demonstrated advantage |
| Avalonia | mature .NET/XAML alternative | NOT SELECTED | credible option, but replaces accepted React/web UI stack and adds another UI stack without proven gain |
| Neutralinojs | lightweight C++ core + local HTTP/WebSocket native API | REJECT first slice | creates local HTTP/WebSocket endpoint boundary that Tauri IPC can avoid |

Official sources:
- Electron process model: https://www.electronjs.org/docs/latest/tutorial/process-model
- Wails: https://wails.io/docs/introduction/
- Wails v3 status: https://v3.wails.io/status/
- Neutralino architecture: https://neutralino.js.org/docs/contributing/architecture/
- Avalonia releases: https://github.com/AvaloniaUI/Avalonia/releases

Conclusion: there is no verified 2026 alternative that materially improves QROS zero-cost, Windows-first, local-first, fail-closed objectives enough to justify replacing the accepted Tauri 2 + React architecture before implementation evidence exists.

## Package manager review

npm remains the minimum necessary package manager because it is already bundled with the selected Node LTS toolchain and supports frozen CI installs through `package-lock.json` + `npm ci`.

pnpm is a credible permissive alternative, but adds another package-manager toolchain. No demonstrated Phase 4 value justifies that addition.

Decision:
- npm: ACCEPT build/dev-only
- pnpm: DEFER

## UI component strategy

The first vertical slice needs navigation, status cards, hard-gate surfaces, and local system status only.

Decision:
- native CSS + small QROS-owned components: ACCEPT
- Tailwind CSS: DEFER
- shadcn/ui: DEFER
- charting/workspace libraries: DEFER to their actual phase

The objective is not to reject those projects; it is to keep the Phase 4 dependency surface minimal.

## i18n / zh-TW

zh-TW remains first-class.

For the small Phase 4 shell, use a typed local message catalog owned by QROS. Do not introduce i18next until pluralization, runtime language switching, namespace loading, or other i18n features create a concrete requirement.

Decision:
- typed local zh-TW catalog: ACCEPT
- i18next: DEFER

## Architecture answers

1. **Tauri 2 + React remains the preferred Phase 4 shell.** No researched alternative has demonstrated a better combined fit for the accepted constraints.
2. **Lower-complexity alternatives exist but do not win overall.** Neutralino lowers native-code surface but adds local HTTP/WebSocket transport; Wails adds Go; Electron adds bundled Chromium/Node; Avalonia changes the entire UI stack.
3. **Node must not be in production.** It is build/dev tooling only.
4. **Expected Phase 4 production process tree:** one QROS Tauri host plus the documented WebView2 process group. No Node, Vite, updater, broker, Yuanta, or opaque QROS daemon.
5. **Tauri command boundary:** local-only capability matching, explicit command allow-list, schema validation, no arbitrary paths/URLs/commands, and deny on malformed/unknown input.
6. **Frontend privileged access:** no broker, credentials, arbitrary filesystem, shell execution, or arbitrary network access.
7. **Research/Data/Backtest communication:** through versioned internal QROS contracts and a Rust-side adapter boundary; UI receives status/typed DTOs, not raw privileged handles.
8. **Phase 4 scope:** shell + navigation + status surfaces only. Phase 5 workspace functionality remains out of scope.
9. **AV behavior:** no injection, hidden PowerShell, self-modification, runtime download/execute, runtime unpack/execute, or persistence. WebView2 child processes must be documented.
10. **Governance:** ADR-0012 remains accepted; this revalidation proposes only a license-boundary hardening ADR and does not alter LEAN, broker, package, release, or live-trading decisions.

## Final revalidation decision

`PHASE_4_RESEARCH = KEEP_ACCEPTED`

`PHASE_4_DESIGN = KEEP_ACCEPTED`

`TAURI_REACT_ARCHITECTURE = KEEP`

`VISUAL_STUDIO_COMMUNITY_2026_INDIVIDUAL_SCOPE = ACCEPT`

`STANDALONE_BUILD_TOOLS_LICENSE_BASIS = DENY_UNLESS_VERIFIED`

`PHASE_4_DEPENDENCY_ADOPTION = DENY_PENDING_IMPLEMENTATION_EVIDENCE`

`PHASE_4_MAIN_RUNTIME_PROMOTION = DENY_PENDING_IMPLEMENTATION_REVIEW`

`NEXT_GATE = PHASE_4_IMPLEMENTATION_CANDIDATE`

This is not a production-readiness claim.
