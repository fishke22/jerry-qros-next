# ADR-0002 — Public Repository Security Model

- Status: ACCEPTED
- Date: 2026-08-31
- Authority: user-approved amendment to `deep-research-report.md`

Observed repository state: public, default branch `main`, initial main commit `d25692bbc91b8cf6aec3423525fa425ae9b34bcd`.

Decision: all Git history is treated as public and durable. Secrets, certificates, broker identifiers, proprietary SDKs, restricted raw data and paid data remain local/private only.

Public standard GitHub-hosted runner compute may be used under zero-cost policy; larger/GPU/paid runners remain prohibited.
