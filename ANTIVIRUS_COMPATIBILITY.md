# Antivirus Compatibility

Target: Windows 11 x64 with Defender, Norton and other endpoint antivirus.

Avoid: process/DLL injection, self-modifying executables, hidden PowerShell core flow, arbitrary download-and-execute, temp unpack-and-run, packers/obfuscation, undocumented startup persistence, credential embedding and opaque child processes.

Candidate builds progressively require documented process tree/network endpoints, dependency manifest, SBOM, SHA-256 and provenance.

False-positive flow: Detection → artifact hash → reproduce from source/build → vendor submission → re-test → evidence.

Permanent antivirus exclusions are not a deployment solution. Paid trusted code signing remains OPTIONAL_FUTURE_PAID_REQUIREMENT and is not authorized.
