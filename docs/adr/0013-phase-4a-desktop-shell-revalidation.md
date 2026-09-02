# ADR-0013 — Phase 4A Desktop Shell Revalidation Hardening

- Status: PROPOSED
- Date: 2026-09-02
- Scope: Phase 4 research/design hardening only

## Context

Phase 4 research and design have already been merged through PR #23 and PR #24. The current roadmap gate is an implementation candidate, not a repeat of architecture research.

A fresh official-source revalidation found no reason to replace the accepted Tauri 2 + React client-SPA architecture. It did identify one material zero-cost licensing ambiguity: the repository research grouped Microsoft C++ Build Tools and Visual Studio Community as a single zero-cost path. Microsoft clearly permits individual developers to use Visual Studio Community for their own free or paid applications, while standalone Build Tools are subject to a separate license basis and must not be assumed free merely from download availability.

Evidence:
- `config/phase4-desktop-shell-revalidation.json`
- `docs/source-evidence/phase-4a-desktop-shell-revalidation.md`

## Decision proposal

1. Keep ADR-0012 and the Tauri 2 + React + TypeScript + Vite architecture.
2. Keep Node/npm as build/dev tooling only; production must not require `node.exe` or the Vite dev server.
3. Keep system WebView2 Evergreen as the Windows runtime model. Record the observed version during Windows validation rather than treating it as a source pin.
4. For the current individual developer scope, prefer `Visual Studio Community 2026 + Desktop development with C++` as the zero-license-cost MSVC path.
5. Treat standalone `Build Tools for Visual Studio 2026` as `DENY_UNLESS_VALID_LICENSE_BASIS_VERIFIED`.
6. Keep native CSS and a QROS-owned typed zh-TW message catalog for the first shell slice.
7. Keep Tailwind, shadcn/ui, i18next, charting/workspace packages, and privileged Tauri plugins deferred.
8. Keep Electron rejected for the first slice because its production main process runs Node and it brings the Chromium/Electron runtime surface.
9. Keep Wails v3 deferred while it is beta; Wails v2 and Avalonia remain credible alternatives but not selected absent demonstrated advantage.
10. Reject Neutralinojs for the first slice because its native API architecture uses a local HTTP/WebSocket router, which introduces a local endpoint boundary the accepted Tauri IPC model does not require.

## Security consequences

The documented production shell process tree is expected to contain:
- the QROS Tauri host executable;
- the system WebView2 process group, including browser/renderer and required helper processes.

It must not contain QROS-owned production:
- Node/Vite processes;
- updater processes;
- shell/process helpers;
- broker/Yuanta processes;
- hidden PowerShell;
- arbitrary download-and-execute helpers.

No frontend capability may grant direct broker, credential, arbitrary filesystem, arbitrary network, or arbitrary shell access.

## Cost consequence

No paid dependency or service is introduced.

The Build Tools clarification is intentionally fail-closed:
`DOWNLOAD_AVAILABLE != ZERO_COST_LICENSE_VERIFIED`.

## Compatibility consequence

TypeScript 7.0.2 remains unverified for the exact future lockfile graph. This ADR does not promote it. A failed compile returns to design review; there is no automatic fallback.

## Hard gates

- `ZERO_COST_REQUIRED = true`
- `PACKAGE_AUTHORIZED = false`
- `RELEASE_AUTHORIZED = false`
- `YUANTA_INTEGRATION_AUTHORIZED = false`
- `LIVE_TRADING_AUTHORIZED = false`

## Next gate

If this proposal is accepted through normal review, the roadmap does not change:

`NEXT_GATE = PHASE_4_IMPLEMENTATION_CANDIDATE`

Dependency adoption and main runtime promotion remain denied until the implementation evidence gate passes.

This ADR is not a production-readiness decision.
