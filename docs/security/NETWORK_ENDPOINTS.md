# Network Endpoints — Phase 2

Runtime data processing is local-only and makes no network request.

CI dependency bootstrap may access only the standard package/tool distribution endpoints required by GitHub Actions and PyPI:

- github.com / api.github.com / actions.githubusercontent.com — GitHub-hosted Actions and setup-python distribution path
- pypi.org — Python package metadata/index
- files.pythonhosted.org — exact hash-locked wheel downloads

No QROS runtime code performs arbitrary download-and-execute. DuckDB extension auto-install and auto-load are explicitly disabled in the Phase 2 query path.

Yuanta/broker endpoints are absent and unauthorized.

## Phase 3A LEAN build

Development/CI may access github.com for the exact public LEAN gitlink, NuGet endpoints for dependencies declared by pinned upstream projects, and Microsoft .NET distribution endpoints used by full-SHA-pinned setup-dotnet. QROS runtime does not auto-download LEAN. Yuanta/broker endpoints remain absent.

## Phase 3B deterministic backtest runtime

The actual synthetic backtest requires no external market-data or broker endpoint. The custom data source permits LocalFile only and throws if invoked in live mode. The config points the otherwise-unused LEAN API base URL to `127.0.0.1:9` as a fail-closed sentinel. Build-time GitHub/NuGet/.NET endpoints remain the only external endpoints in CI.

## Phase 4 QUT source-build candidate

QUT runtime remains local-only. The Phase 4 shell has no arbitrary HTTP capability and no broker endpoint.

CI and an explicitly requested physical-Windows `-BuildSmoke` may restore the exact locked dependency graph from:

- registry.npmjs.org — npm public registry for exact `package-lock.json` packages
- index.crates.io — crates.io sparse registry index
- static.crates.io — crates.io package download CDN
- github.com / api.github.com / actions.githubusercontent.com — pinned GitHub Actions and reviewed CI tool source/distribution paths

The local Windows inventory-only validation mode performs no dependency bootstrap and requires no remote MCP/relay service.

No Phase 4 runtime code downloads or executes arbitrary content. Packaging, updater, signing, release, Yuanta and broker endpoints remain absent and unauthorized.
