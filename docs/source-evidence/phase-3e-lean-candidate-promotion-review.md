# Phase 3E — LEAN candidate promotion review evidence

## Initial state

Review-only. All promotion criteria start PENDING/UNVERIFIED.

### NetMQ license evidence

Official NetMQ tag `4.0.4.3` resolves to commit `ca87d32d5ca5d8a2675fb7a9925e4b3dc8c35010`.

The upstream `COPYING.LESSER` file contains GNU Lesser General Public License version 3 and a project-specific special exception permitting linking with independent modules subject to each module's own terms. Because the exception is project-specific rather than an assumed SPDX exception identifier, QROS records automated SPDX equivalence as UNVERIFIED and requires distribution-compliance review before any future packaging.

No packaging or release is authorized in Phase 3E.

### Upstream regression target

Pinned LEAN contains `Tests/Compression/CompressionTests.cs` in `Tests/QuantConnect.Tests.csproj`, target `net10.0`. The test project itself directly pins NetMQ 4.0.1.6, so the Phase 3E test harness will make the same 4.0.4.3 replacement in that test project only to avoid reintroducing the obsolete Messaging chain into the regression harness. This test-harness edit is not part of the runtime candidate.

### Resource-model hypothesis

The research compatibility bridge currently calls `CopyTo(memory)` followed by `memory.ToArray()` for each ZIP entry. Phase 3E will run a 32 MiB highly compressible entry probe and inspect the bridge's private retained buffer to determine whether the implementation materially retains the full uncompressed entry.

Acceptance evidence is pending CI.
