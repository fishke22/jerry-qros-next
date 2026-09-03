[CmdletBinding()]
param(
    [switch]$BuildSmoke,
    [string]$EvidencePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$QutRoot = Join-Path $RepoRoot "apps\qut"
$CargoManifest = Join-Path $QutRoot "src-tauri\Cargo.toml"
$PackageLock = Join-Path $QutRoot "package-lock.json"
$CargoLock = Join-Path $QutRoot "src-tauri\Cargo.lock"

if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $RepoRoot "local-only\phase4\windows11-validation.json"
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-NativeText {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$WorkingDirectory = $RepoRoot
    )
    Push-Location $WorkingDirectory
    try {
        $output = & $FilePath @ArgumentList 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "$FilePath failed with exit code $exitCode"
        }
        return (($output | ForEach-Object { "$_" }) -join [Environment]::NewLine).Trim()
    }
    finally {
        Pop-Location
    }
}

function Invoke-NativeVisible {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$WorkingDirectory = $RepoRoot
    )
    Push-Location $WorkingDirectory
    try {
        & $FilePath @ArgumentList
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            throw "$FilePath failed with exit code $exitCode"
        }
    }
    finally {
        Pop-Location
    }
}

$gitRoot = Invoke-NativeText -FilePath "git" -ArgumentList @("-C", $RepoRoot, "rev-parse", "--show-toplevel")
if ([IO.Path]::GetFullPath($gitRoot) -ne [IO.Path]::GetFullPath($RepoRoot)) {
    throw "Repository root mismatch"
}

$headSha = Invoke-NativeText -FilePath "git" -ArgumentList @("-C", $RepoRoot, "rev-parse", "HEAD")
$trackedStatus = Invoke-NativeText -FilePath "git" -ArgumentList @("-C", $RepoRoot, "status", "--porcelain", "--untracked-files=no")
$trackedClean = [string]::IsNullOrWhiteSpace($trackedStatus)

$os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
$isWindows11 = $os.Caption -like "*Windows 11*"
$isX64 = ($os.OSArchitecture -like "*64-bit*") -and ($env:PROCESSOR_ARCHITECTURE -eq "AMD64")
if (-not $isWindows11) {
    throw "Physical Windows 11 target required; detected: $($os.Caption)"
}
if (-not $isX64) {
    throw "x64 target required; detected OSArchitecture=$($os.OSArchitecture), PROCESSOR_ARCHITECTURE=$($env:PROCESSOR_ARCHITECTURE)"
}

$nodeVersion = Invoke-NativeText -FilePath "node" -ArgumentList @("--version")
$npmVersion = Invoke-NativeText -FilePath "npm" -ArgumentList @("--version")
$rustcVerbose = Invoke-NativeText -FilePath "rustc" -ArgumentList @("-Vv")
$cargoVersion = Invoke-NativeText -FilePath "cargo" -ArgumentList @("-V")
$rustupActive = Invoke-NativeText -FilePath "rustup" -ArgumentList @("show", "active-toolchain")

$rustcVersionLine = (($rustcVerbose -split "\r?\n")[0]).Trim()
$rustHostLine = @($rustcVerbose -split "\r?\n" | Where-Object { $_ -like "host:*" }) | Select-Object -First 1
if (-not $rustHostLine) {
    throw "Unable to determine Rust host triple"
}
$rustHost = ($rustHostLine -replace "^host:\s*", "").Trim()

if ($nodeVersion -ne "v24.20.0") {
    throw "Unexpected Node version: $nodeVersion"
}
if ($npmVersion -ne "11.19.0") {
    throw "Unexpected npm version: $npmVersion"
}
if (($rustcVersionLine -split " ")[1] -ne "1.98.0") {
    throw "Unexpected Rust version: $rustcVersionLine"
}
if ($rustHost -ne "x86_64-pc-windows-msvc") {
    throw "Unexpected Rust host target: $rustHost"
}
if (-not $rustupActive.StartsWith("1.98.0-x86_64-pc-windows-msvc")) {
    throw "Unexpected active Rust toolchain: $rustupActive"
}

$toolchain = [ordered]@{
    node_version = $nodeVersion
    npm_version = $npmVersion
    rustc_version = $rustcVersionLine
    cargo_version = $cargoVersion
    rust_host = $rustHost
    rustup_active_toolchain = $rustupActive
}

$vswhere = Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path -LiteralPath $vswhere -PathType Leaf)) {
    throw "vswhere.exe missing from the standard Visual Studio Installer location"
}
$vsJson = Invoke-NativeText -FilePath $vswhere -ArgumentList @(
    "-products", "*",
    "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
    "-format", "json"
)
$vsInstances = @($vsJson | ConvertFrom-Json)
if ($vsInstances.Count -eq 0) {
    throw "No Visual Studio installation with VC.Tools.x86.x64 was found"
}

$communityInstances = @(
    $vsInstances |
        Where-Object { $_.productId -eq "Microsoft.VisualStudio.Product.Community" } |
        Sort-Object { [version]$_.installationVersion } -Descending
)
if ($communityInstances.Count -eq 0) {
    $detectedProducts = @($vsInstances | ForEach-Object { "$($_.productId)" }) -join ", "
    throw "No Visual Studio Community instance with VC.Tools.x86.x64 was found. Non-Community product(s) require separate license evidence: $detectedProducts"
}
$vs = $communityInstances[0]

$vcToolsVersionFile = Join-Path $vs.installationPath "VC\Auxiliary\Build\Microsoft.VCToolsVersion.default.txt"
if (-not (Test-Path -LiteralPath $vcToolsVersionFile -PathType Leaf)) {
    throw "Visual C++ toolset version file missing"
}
$vcToolsVersion = (Get-Content -LiteralPath $vcToolsVersionFile -Raw -ErrorAction Stop).Trim()
$clExe = Join-Path $vs.installationPath "VC\Tools\MSVC\$vcToolsVersion\bin\Hostx64\x64\cl.exe"
if (-not (Test-Path -LiteralPath $clExe -PathType Leaf)) {
    throw "x64 MSVC compiler executable missing for toolset $vcToolsVersion"
}
$clProductVersion = (Get-Item -LiteralPath $clExe -ErrorAction Stop).VersionInfo.ProductVersion

$webViewClientId = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
$webViewRegistryPaths = @(
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\$webViewClientId",
    "HKCU:\Software\Microsoft\EdgeUpdate\Clients\$webViewClientId"
)
$webViewVersions = @()
foreach ($path in $webViewRegistryPaths) {
    if (Test-Path -LiteralPath $path) {
        $pv = (Get-ItemProperty -LiteralPath $path -Name pv -ErrorAction Stop).pv
        if ($pv -and $pv -ne "0.0.0.0") {
            $webViewVersions += [ordered]@{
                registry_scope = if ($path.StartsWith("HKLM:")) { "HKLM" } else { "HKCU" }
                version = "$pv"
            }
        }
    }
}
if ($webViewVersions.Count -eq 0) {
    throw "WebView2 Evergreen Runtime registry inventory missing"
}

$defender = [ordered]@{
    command_available = $false
    query_succeeded = $false
    antimalware_enabled = $null
    antivirus_enabled = $null
    real_time_protection_enabled = $null
    am_running_mode = $null
    am_product_version = $null
    am_engine_version = $null
    antivirus_signature_version = $null
    error_type = $null
}
if (Get-Command Get-MpComputerStatus -ErrorAction SilentlyContinue) {
    $defender.command_available = $true
    try {
        $mp = Get-MpComputerStatus -ErrorAction Stop
        $defender.query_succeeded = $true
        $defender.antimalware_enabled = [bool]$mp.AMServiceEnabled
        $defender.antivirus_enabled = [bool]$mp.AntivirusEnabled
        $defender.real_time_protection_enabled = [bool]$mp.RealTimeProtectionEnabled
        $defender.am_running_mode = "$($mp.AMRunningMode)"
        $defender.am_product_version = "$($mp.AMProductVersion)"
        $defender.am_engine_version = "$($mp.AMEngineVersion)"
        $defender.antivirus_signature_version = "$($mp.AntivirusSignatureVersion)"
    }
    catch {
        $defender.error_type = $_.Exception.GetType().FullName
    }
}

$securityCenter = [ordered]@{
    query_succeeded = $false
    products = @()
    norton_or_symantec_detected = $false
    error_type = $null
}
try {
    $products = @(Get-CimInstance -Namespace "root/SecurityCenter2" -ClassName AntiVirusProduct -ErrorAction Stop)
    $sanitizedProducts = @(
        $products | ForEach-Object {
            [ordered]@{
                display_name = "$($_.displayName)"
                product_state = ("0x{0:X6}" -f [int]$_.productState)
            }
        }
    )
    $securityCenter.query_succeeded = $true
    $securityCenter.products = $sanitizedProducts
    $securityCenter.norton_or_symantec_detected = @(
        $sanitizedProducts | Where-Object { $_.display_name -match "(?i)norton|symantec" }
    ).Count -gt 0
}
catch {
    $securityCenter.error_type = $_.Exception.GetType().FullName
}

$build = [ordered]@{
    requested = [bool]$BuildSmoke
    performed = $false
    package_lock_sha256 = Get-Sha256 -Path $PackageLock
    cargo_lock_sha256 = Get-Sha256 -Path $CargoLock
    node_version = $nodeVersion
    npm_version = $npmVersion
    rustc_version = $rustcVersionLine
    development_exe_sha256 = $null
    installer_artifacts_found = @()
}

if ($BuildSmoke) {
    if (-not $trackedClean) {
        throw "Tracked working tree must be clean before BuildSmoke"
    }

    $expectedPackageLockSha = "e8c023a29dbbbc9fbaff86769998e05635ab140594eb53caff5bd082624ee4b8"
    $expectedCargoLockSha = "c9abfa64e57be2dd18efa91d8ae4abf43944bdbae75af94555ff28daa7601adb"
    if ($build.package_lock_sha256 -ne $expectedPackageLockSha) {
        throw "package-lock.json SHA-256 drift"
    }
    if ($build.cargo_lock_sha256 -ne $expectedCargoLockSha) {
        throw "Cargo.lock SHA-256 drift"
    }

    Invoke-NativeVisible -FilePath "npm" -ArgumentList @("ci", "--ignore-scripts", "--no-audit", "--no-fund") -WorkingDirectory $QutRoot
    Invoke-NativeVisible -FilePath "npm" -ArgumentList @("run", "build") -WorkingDirectory $QutRoot
    Invoke-NativeVisible -FilePath "cargo" -ArgumentList @(
        "metadata",
        "--locked",
        "--filter-platform", "x86_64-pc-windows-msvc",
        "--format-version=1",
        "--manifest-path", $CargoManifest
    )
    Invoke-NativeVisible -FilePath "cargo" -ArgumentList @(
        "build",
        "--locked",
        "--manifest-path", $CargoManifest
    )

    $exe = Join-Path $QutRoot "src-tauri\target\debug\qros-qut.exe"
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        throw "Development executable missing after source build"
    }
    $build.development_exe_sha256 = Get-Sha256 -Path $exe

    $forbiddenArtifacts = @(
        Get-ChildItem -LiteralPath $QutRoot -Recurse -File -ErrorAction Stop |
            Where-Object {
                $_.Name -like "*.msi" -or
                $_.Name -like "*.msix" -or
                $_.Name -like "*-setup.exe"
            } |
            ForEach-Object { $_.FullName.Substring($RepoRoot.Length).TrimStart("\") }
    )
    $build.installer_artifacts_found = $forbiddenArtifacts
    if ($forbiddenArtifacts.Count -ne 0) {
        throw "Forbidden installer artifact produced"
    }

    $postBuildTrackedStatus = Invoke-NativeText -FilePath "git" -ArgumentList @(
        "-C", $RepoRoot, "status", "--porcelain", "--untracked-files=no"
    )
    if (-not [string]::IsNullOrWhiteSpace($postBuildTrackedStatus)) {
        throw "Tracked files changed during BuildSmoke"
    }

    $build.performed = $true
}

$evidence = [ordered]@{
    schema_version = 1
    evidence_type = "PHASE4_WINDOWS11_LOCAL_VALIDATION_CANDIDATE"
    generated_at_utc = [DateTime]::UtcNow.ToString("o")
    repository = [ordered]@{
        head_sha = $headSha
        tracked_working_tree_clean = $trackedClean
    }
    target = [ordered]@{
        windows_11 = $isWindows11
        x64 = $isX64
        caption = "$($os.Caption)"
        version = "$($os.Version)"
        build_number = "$($os.BuildNumber)"
        os_architecture = "$($os.OSArchitecture)"
    }
    toolchain = $toolchain
    visual_studio = [ordered]@{
        display_name = "$($vs.displayName)"
        installation_version = "$($vs.installationVersion)"
        product_id = "$($vs.productId)"
        license_basis = "COMMUNITY_INDIVIDUAL_SCOPE_CANDIDATE"
        vc_tools_x86_x64_required_component_resolved = $true
        vc_tools_version = "$vcToolsVersion"
        cl_product_version = "$clProductVersion"
    }
    webview2 = [ordered]@{
        evergreen_runtime_present = $true
        versions = $webViewVersions
    }
    defender = $defender
    security_center = $securityCenter
    build_smoke = $build
    hard_gates = [ordered]@{
        package_authorized = $false
        release_authorized = $false
        yuanta_integration_authorized = $false
        live_trading_authorized = $false
        production_readiness_authorized = $false
    }
    privacy = [ordered]@{
        hostname_collected = $false
        username_collected = $false
        antivirus_executable_paths_collected = $false
        broker_credentials_collected = $false
        broad_filesystem_scan_performed = $false
    }
}

$evidenceDirectory = Split-Path -Parent $EvidencePath
New-Item -ItemType Directory -Path $evidenceDirectory -Force | Out-Null
$evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $EvidencePath -Encoding UTF8

Write-Host "QROS_PHASE4_LOCAL_EVIDENCE=$EvidencePath"
Write-Host "QROS_PHASE4_HEAD_SHA=$headSha"
Write-Host "QROS_PHASE4_WINDOWS11_X64=PASS"
Write-Host "QROS_PHASE4_WEBVIEW2=PASS"
Write-Host "QROS_PHASE4_NORTON_DETECTED=$($securityCenter.norton_or_symantec_detected)"
if ($BuildSmoke) {
    Write-Host "QROS_PHASE4_SOURCE_BUILD=PASS"
    Write-Host "QROS_PHASE4_DEV_EXE_SHA256=$($build.development_exe_sha256)"
}
Write-Host "Phase 4 local evidence collection complete; acceptance still requires review."
