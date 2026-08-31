# Local Source Promotion Policy

Purpose: allow desktop sessions to pre-process useful local material so later mobile/cloud work does not depend on local connectivity, without violating public-repository boundaries.

## D:\QROS

Treat as a legacy donor, not a canonical source tree.

Promotion flow:

Local whitelist → path exclusion → secret pattern scan → rights/license review → semantic review → independent rewrite or explicitly approved copy → tests → PR.

Never upload its complete Git history, local data lake, caches, logs, credentials, proprietary SDKs or broker-connected code.

## D:\YUANTA_AUTOPILOT

Current state: DENY.

No inventory, read, upload or migration until the user explicitly authorizes Yuanta SPARK integration.

## Mobile/cloud continuity

Cloud-accessible continuity should come from:

- canonical QROS Next source/contracts/docs;
- sanitized evidence summaries and hashes;
- synthetic fixtures;
- explicitly promoted, independently reviewed assets.

It should not come from mirroring a mixed-trust Windows workspace into a public Git repository.
