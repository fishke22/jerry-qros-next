# Network Endpoints — Phase 2

Runtime data processing is local-only and makes no network request.

CI dependency bootstrap may access only the standard package/tool distribution endpoints required by GitHub Actions and PyPI:

- github.com / api.github.com / actions.githubusercontent.com — GitHub-hosted Actions and setup-python distribution path
- pypi.org — Python package metadata/index
- files.pythonhosted.org — exact hash-locked wheel downloads

No QROS runtime code performs arbitrary download-and-execute. DuckDB extension auto-install and auto-load are explicitly disabled in the Phase 2 query path.

Yuanta/broker endpoints are absent and unauthorized.
