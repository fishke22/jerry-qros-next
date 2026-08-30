# Build Policy

- Formal desktop target: Windows 11 x64 only.
- Linux standard GitHub runners may run non-product CI; this does not imply Linux product support.
- Windows standard runners are only for Windows-specific compile/smoke work.
- No larger, GPU, paid runner or paid cloud build.
- Preserve source revision, lockfiles, build environment and SHA-256 provenance.
- Avoid hidden PowerShell core flow, arbitrary download-and-execute, packers/obfuscation, self-modification and undocumented persistence.
- Production packaging commands are forbidden while `package_authorized=false`.
