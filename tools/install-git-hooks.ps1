param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

git -C $RepoRoot config core.hooksPath tools/git-hooks
Write-Host "Configured git core.hooksPath=tools/git-hooks for $RepoRoot"
Write-Host "Current hook check:"
git -C $RepoRoot config core.hooksPath
