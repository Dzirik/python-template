# Install Git hooks for the repository (Windows PowerShell version)
# Points core.hooksPath at the tracked scripts/hooks directory instead of copying files into
# .git/hooks, so edits to the tracked hooks take effect immediately with no re-install step.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$HooksPath = "scripts/hooks"

Write-Host "Installing Git hooks..." -ForegroundColor Cyan

# Check if .git directory exists
if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    Write-Host "Error: .git directory not found. Are you in a git repository?" -ForegroundColor Red
    exit 1
}

git config core.hooksPath $HooksPath

Write-Host ""
Write-Host "Git hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Installed hooks:"
Write-Host "  - pre-commit: Blocks direct commits to main/develop branches"
Write-Host "  - pre-push: Runs security checks on changed files before push"
Write-Host ""
Write-Host "To bypass hooks (not recommended):"
Write-Host "  - Skip pre-commit: git commit --no-verify"
Write-Host "  - Skip pre-push: git push --no-verify"
Write-Host ""
