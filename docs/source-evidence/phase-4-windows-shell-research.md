# Phase 4 Windows Shell Research Evidence

Date: 2026-09-02
Scope: RESEARCH → DESIGN only
Decision status: RESEARCHED / IMPLEMENTATION NOT YET AUTHORIZED

## Baseline

QROS Next remains Windows 11 x64 first, local-first, single-user first, zh-TW first, zero-cost required, and fail-closed. Phase 4 must not authorize packaging, release, Yuanta integration, or live trading.

## Candidate stack

| Component | Observed current stable | Phase 4 candidate | License | Decision |
| --- | --- | --- | --- | --- |
| Tauri core | 2.11.5 | 2.11.5 | Apache-2.0 OR MIT | KEEP / candidate |
| tauri-build | 2.6.3 | 2.6.3 | Apache-2.0 OR MIT | KEEP / candidate |
| @tauri-apps/cli | 2.11.4 | 2.11.4 | Apache-2.0 OR MIT | KEEP / candidate |
| @tauri-apps/api | 2.11.1 | 2.11.1 | Apache-2.0 OR MIT | KEEP / candidate |
| React / react-dom | 19.2.8 | 19.2.8 | MIT | KEEP / candidate |
| TypeScript | 7.0.2 | 7.0.2 | Apache-2.0 | candidate; Windows validation required |
| Vite | 8.2.2 | 8.2.2 | MIT | KEEP / candidate |
| Node.js | 26.8.1 Current / 24.20.0 LTS | 24.20.0 LTS | MIT | choose LTS |
| pnpm | 12.2.1 latest / 11.25.0 maintained | 11.25.0 | MIT | choose mature major |
| Rust | 1.98.0 stable | 1.98.0 | MIT OR Apache-2.0 | KEEP / candidate |

## Exact source evidence

- Tauri 2.11.5 tag commit: `7cd71369c00978a3783b6ae3e9972358abbe4ae6`.
- Tauri package metadata at that commit declares `x86_64-pc-windows-msvc`, `tauri = 2.11.5`, `tauri-build = 2.6.3`, `@tauri-apps/cli = 2.11.4`, and `@tauri-apps/api = 2.11.1`.
- React 19.2.8 tag commit: `1dd4ecbdabf826f527fc9a58c05ea70375b7d170`.
- TypeScript 7.0.2 tag commit: `1e4744d68260a7cb91b62b12edc3f6a2187faaf1`.
- Vite 8.2.2 tag commit: `de1111ab0be00879b404e7ed3b2a80e264edddc1`.
- pnpm 11.25.0 tag commit: `6d90c71efdffbc909b499490b64c66badc720327`.
- Node.js 24.20.0 tag commit: `71b8b174857e25106d39b61a9e6f30d927da8b01`.
- Rust 1.98.0 tag commit: `88d9e12ae178fab0fb5cc050a94da85685d449ea`.

## Official Windows prerequisites

Tauri uses Microsoft Edge WebView2 on Windows and documents Microsoft C++ Build Tools as a Windows prerequisite. Tauri's published package metadata targets `x86_64-pc-windows-msvc`.

Microsoft states that the Evergreen WebView2 Runtime is included with Windows 11 and recommends Evergreen for most applications. It updates independently and therefore is not a repo-pinned package. QROS should treat it as an OS-managed host runtime: detect presence/version, record it in environment evidence, and fail closed if unavailable.

Microsoft's 2026 download page states Visual Studio Community is free for individual developers. Build Tools require a valid Visual Studio license except for building open-source dependencies. For this personal single-developer project, the zero-cost local path is Visual Studio Community 2026 / its licensed C++ toolchain. Exact installed MSVC and Windows SDK versions must be inventoried before Phase 4 implementation acceptance.

## Security design constraints

Tauri 2.11.5 resolves `tauri-runtime-wry 2.11.4`, which declares `wry 0.55.0`. Current WRY Windows source injects `--disable-features=msWebOOUI,msPdfOOUI,msSmartScreenProtection` into WebView2 by default. QROS therefore must not treat WebView SmartScreen as a security control; the Phase 4A shell must keep remote content disabled and rely on local assets, CSP, ACL/capability denial, dependency review, and endpoint AV. This does not change the separate Windows executable reputation/signing gate.

The full Cargo/npm transitive vulnerability graph has not yet been generated for the QROS lockfiles. Under fail-closed policy this remains `UNKNOWN = DENY`; Tauri/WRY is a research candidate, not an adopted runtime.


Tauri 2 capability ACLs can leave a window with no IPC access if no capability matches it. The first vertical slice should exploit this:

- one main window only;
- bundled local HTML/JS/CSS only;
- no remote page navigation;
- no Tauri plugins;
- no custom Rust commands exposed to frontend;
- no filesystem, shell, dialog, updater, process, or HTTP plugin permissions;
- no remote-domain IPC;
- CSP required, no remote scripts/CDNs, no `unsafe-eval`;
- devtools only in debug/development;
- updater disabled;
- no startup persistence;
- no hidden PowerShell;
- no download-and-execute.

Tauri recommends restrictive CSP and warns against remote scripts/CDNs. Capabilities are the IPC boundary and should remain empty/minimal for the first slice.

## Packaging boundary

Tauri `build` bundles by default, but official CLI supports `--no-bundle`. Because `PACKAGE_AUTHORIZED=false`, Phase 4 validation may use:

- `cargo check`;
- `cargo build`;
- `pnpm tauri build --no-bundle`;
- development executable only when required for testing.

It must not invoke `tauri bundle`, MSI, NSIS, MSIX, updater artifacts, signing, or GitHub Release.

## CI cost

GitHub documents standard hosted runners as free and unlimited for public repositories. A Phase 4 Windows compile gate may therefore use a standard x64 Windows runner such as `windows-2025-vs2026`, with no larger runner and no paid overage. This is compile/integration evidence only; Windows 11 desktop smoke remains a later local gate.

## Deliberately deferred candidates

The following remain `DENY` and are not required for the first shell vertical slice:

- FlexLayout;
- Lightweight Charts;
- ECharts;
- shadcn/ui;
- TanStack Query;
- i18next;
- any Tauri plugin.

They should be researched only when a concrete Phase 4 feature requires them.

## Research decision

`TAURI_2_WINDOWS_SHELL = KEEP_AS_MINIMAL_VERTICAL_SLICE_CANDIDATE`

`PHASE4_DEPENDENCY_INTRODUCTION = DENY_PENDING_DESIGN_REVIEW_AND_LOCKFILE/SBOM_CLOSURE`

`PACKAGE = DENY`
`RELEASE = DENY`
`YUANTA = DENY`
`LIVE_TRADING = DENY`

## Official references

- https://v2.tauri.app/start/prerequisites/
- https://v2.tauri.app/security/csp/
- https://v2.tauri.app/reference/acl/capability/
- https://v2.tauri.app/distribute/
- https://github.com/tauri-apps/tauri/releases
- https://github.com/react/react/releases
- https://github.com/microsoft/TypeScript/releases
- https://vite.dev/
- https://nodejs.org/en/about/previous-releases
- https://github.com/pnpm/pnpm/releases
- https://blog.rust-lang.org/releases/latest/
- https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution
- https://visualstudio.microsoft.com/downloads/
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
