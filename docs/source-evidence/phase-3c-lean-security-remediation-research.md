# Phase 3C — LEAN dependency remediation research evidence

## Scope

Research only. This phase does not modify the LEAN gitlink, patch upstream source, introduce a fork, authorize runtime promotion, or change any broker/trading gate.

## Current official upstream state — 2026-09-01

- QuantConnect/Lean `master` was observed at `abeb0a0627ec484b92291c45c3f2553726c26199`.
- At that revision, `Compression/QuantConnect.Compression.csproj` still directly references `DotNetZip 1.16.0`.
- `Common/QuantConnect.csproj` directly references the Compression project.
- `Launcher/QuantConnect.Lean.Launcher.csproj` directly references Compression plus the full engine projects used by the standard Launcher.
- Issue #8795 remains OPEN and was updated 2026-08-31.
- PR #8820 proposed a drop-in DotNetZip replacement and was closed unmerged. A LEAN maintainer stated the intended final direction is migration to runtime compression and removal of the old library dependency.
- PR #9744 was merged 2026-08-24 and migrated some ZIP read/update paths to `System.IO.Compression.ZipArchive`, but current master still pins DotNetZip and still contains `Ionic.Zip` usages. Therefore #9744 is partial remediation, not closure of the security gate.
- A maintainer comment on issue #8795 links completion of the runtime-compression migration to .NET 11 capabilities. QROS remains pinned to .NET 10.0.400; this note does not authorize a toolchain upgrade.

## Candidate decision

1. **Preferred:** adopt a future official LEAN revision only after the blocking advisories are absent and full QROS regression passes.
2. **Second:** an upstream-aligned QROS patch that removes vulnerable dependencies may be researched, but implementation requires a separate architecture amendment and explicit review because it changes the canonical engine source.
3. **Minimal build:** currently UNPROVEN. Standard Launcher/Common references do not provide an existing clean subset that excludes Compression.
4. **Drop-in DotNetZip fork:** REJECTED for QROS at this gate.
5. **NU1903/NU1904 suppression:** REJECTED.

## Next evidence

The Phase 3C CI audit must enumerate the exact pinned Launcher's direct/transitive NuGet graph and show dependency paths for every HIGH/CRITICAL blocker. Until that evidence exists, runtime promotion remains DENY.
