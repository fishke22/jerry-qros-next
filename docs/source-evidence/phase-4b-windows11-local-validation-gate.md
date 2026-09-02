# Phase 4B — Windows 11 local validation gate research

Verified: 2026-09-02

Status: **DESIGN / IMPLEMENTATION CANDIDATE ONLY**

## Decision

The canonical Phase 4 desktop target remains physical Windows 11 x64. GitHub-hosted Windows Server evidence is useful compile/smoke evidence but is not equivalent to the target OS.

The current ChatGPT-connected Remote Desktop Commander path is **not authorized for QROS local validation** because its zero-cost service boundary is not sufficiently proven.

- The official Remote Desktop Commander repository describes the remote connector as a hosted/cloud relay, currently beta, and states that the hosted service implementation is proprietary.
- Desktop Commander Terms define Remote Desktop Commander as a cloud-based service and also define free credits, subscription fees, and optional paid features.
- The separate local DesktopCommanderMCP implementation is open source under MIT, but this ChatGPT conversation does not have a proven direct local-stdio path to the user Windows machine.

Under QROS governance:

```text
UNVERIFIED_ZERO_COST_REMOTE_SERVICE = DENY
UNKNOWN != ALLOW
```

Therefore Phase 4 uses a repository-hosted local PowerShell validation harness that the user can execute directly on the physical Windows 11 target without requiring a paid SaaS, paid API, paid MCP, or cloud compute.

## Official evidence

### Remote Desktop Commander

- https://github.com/desktop-commander/remote-desktop-commander
- https://legal.desktopcommander.app/
- https://github.com/wonderwhy-er/DesktopCommanderMCP

Disposition:

```text
remote hosted connector = DENY_FOR_QROS_UNTIL_ZERO_COST_LIMIT_IS_EXPLICITLY_VERIFIED
local open-source MCP = MIT, but no current direct ChatGPT-local transport is proven
```

### GitHub self-hosted runner alternative

GitHub official billing documentation states that GitHub Actions usage is free for self-hosted runners. This satisfies the direct monetary-cost test for the runner service itself.

However, GitHub official security guidance states that self-hosted runners should almost never be used for public repositories because pull requests or workflow changes can compromise the persistent machine environment. GitHub also explicitly recommends using self-hosted runners with private repositories rather than public repositories.

Canonical QROS is currently a public repository. The physical Windows 11 target is a user workstation and may contain unrelated local data. Registering that workstation as a runner for the public canonical repository would therefore enlarge the attack surface beyond the Phase 4 need.

Official references checked 2026-09-02:

- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/security/secure-use
- https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners

Disposition:

```text
SELF_HOSTED_RUNNER_MONETARY_COST = ZERO
SELF_HOSTED_RUNNER_ON_PUBLIC_CANONICAL_REPO = REJECT
EPHEMERAL_SELF_HOSTED_RUNNER_ON_USER_WORKSTATION = NOT_SELECTED
```

The zero-cost property is not sufficient to override the public-repository security warning. QROS will not attach the user's Windows workstation to the public canonical repository as a self-hosted runner.

### Windows Defender inventory

Microsoft documents `Get-MpComputerStatus` as the Defender cmdlet that gets antimalware status.

- https://learn.microsoft.com/powershell/module/defender/get-mpcomputerstatus

The Phase 4 harness uses only read operations. It does not add exclusions, change preferences, update signatures, or start scans.

### Visual Studio / MSVC inventory

Microsoft `vswhere` is MIT-licensed, is included with Visual Studio Installer since Visual Studio 2017 15.2, and can locate installations/components without downloading another tool.

- https://github.com/microsoft/vswhere
- https://github.com/microsoft/vswhere/wiki/Installing

The harness requires `Microsoft.VisualStudio.Component.VC.Tools.x86.x64`.

### Build dependency endpoints

The inventory-only mode performs no dependency bootstrap.

When the user explicitly runs `-BuildSmoke`, exact-lock dependency restoration may use:

- https://registry.npmjs.org/
- https://index.crates.io/
- https://static.crates.io/crates

The npm registry endpoint is the official default public registry. The crates.io sparse index and crate download CDN are official crates.io infrastructure.

## Safety boundary of the local harness

The harness:

- resolves only the QROS repository root and QUT paths;
- reads Windows OS metadata;
- reads Visual Studio metadata using installed `vswhere.exe`;
- reads WebView2 Evergreen registry metadata;
- reads Defender antimalware status;
- reads sanitized SecurityCenter2 antivirus product name/state;
- does not collect hostname or username;
- does not collect antivirus executable paths;
- does not search arbitrary disks;
- does not read broker credentials or certificates;
- does not modify Defender or Norton settings;
- does not create exclusions;
- does not invoke installer, Tauri bundling, release, signing, updater, or broker actions;
- writes sanitized evidence only under ignored `local-only/`;
- keeps all package/release/Yuanta/live-trading gates false.

The harness intentionally stops at inventory/source-build evidence. It does not claim runtime UI, process-tree, network, Defender detection, or Norton compatibility acceptance.

## PowerShell execution-policy boundary

The local runbook must not use `-ExecutionPolicy Bypass`.

If script execution is blocked by local policy, QROS does not alter machine policy and does not weaken endpoint protection. The result remains a blocker until the user has an already-approved local execution method.

## Acceptance rule

The existence of the harness does not close the Phase 4 physical-target gate.

Promotion requires actual evidence from a physical Windows 11 x64 execution, review of the generated sanitized JSON, and a separate runtime/AV smoke review.

Until then:

```text
WINDOWS_11_PHYSICAL_TARGET = UNKNOWN / DENY
WINDOWS_11_RUNTIME_SMOKE = UNKNOWN / DENY
DEFENDER_LOCAL_VALIDATION = UNKNOWN / DENY
NORTON_LOCAL_VALIDATION = UNKNOWN / DENY
DEPENDENCY_ADOPTION = DENY
MAIN_RUNTIME_PROMOTION = DENY
```
