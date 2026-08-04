param([switch]$AuditOnly)

$ErrorActionPreference = "Stop"
$vault = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$hub = Join-Path $vault "tools\agent-hub\skills"
$runtimeRoots = @(
    (Join-Path $env:USERPROFILE ".codex\skills"),
    (Join-Path $env:USERPROFILE ".claude\skills"),
    (Join-Path $env:USERPROFILE ".gemini\antigravity\skills")
)
$skills = @("personal-kg-ingest", "personal-kg-lookup", "personal-kg-health")
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

function Get-Target([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.LinkType -and $item.Target) { return [string]$item.Target }
    return $null
}

Write-Host "== Personal KG Agent Hub ($($AuditOnly ? 'audit' : 'repair')) =="
$configDir = Join-Path $env:USERPROFILE ".personal-kg"
$configFile = Join-Path $configDir "root.txt"
$configured = if (Test-Path $configFile) { (Get-Content $configFile -TotalCount 1).Trim() } else { $null }
if ($configured -ieq $vault) {
    Write-Host "[OK] $configFile"
} elseif ($AuditOnly) {
    Write-Host "[DRIFT] $configFile -> $configured"
} else {
    New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    Set-Content -LiteralPath $configFile -Value $vault -Encoding utf8
    Write-Host "[SET] $configFile -> $vault"
}

foreach ($root in $runtimeRoots) {
    foreach ($skill in $skills) {
        $link = Join-Path $root $skill
        $target = Join-Path $hub $skill
        $current = Get-Target $link
        if ($current -eq $target) {
            Write-Host "[OK] $link"
            continue
        }
        if ($AuditOnly) {
            Write-Host "[DRIFT] $link -> $current"
            continue
        }
        New-Item -ItemType Directory -Force -Path $root | Out-Null
        if (Test-Path -LiteralPath $link) {
            Move-Item -LiteralPath $link -Destination "$link.backup-$timestamp"
        }
        New-Item -ItemType Junction -Path $link -Target $target | Out-Null
        Write-Host "[LINKED] $link -> $target"
    }
}
