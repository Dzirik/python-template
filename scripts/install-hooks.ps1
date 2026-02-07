# Install Git hooks for the repository (Windows PowerShell version)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$HooksDir = Join-Path $RepoRoot ".git\hooks"
$PreCommitHook = Join-Path $HooksDir "pre-commit"
$PrePushHook = Join-Path $HooksDir "pre-push"

Write-Host "Installing Git hooks..." -ForegroundColor Cyan

# Check if .git directory exists
if (-not (Test-Path (Join-Path $RepoRoot ".git"))) {
    Write-Host "Error: .git directory not found. Are you in a git repository?" -ForegroundColor Red
    exit 1
}

# Create hooks directory if it doesn't exist
if (-not (Test-Path $HooksDir)) {
    New-Item -ItemType Directory -Path $HooksDir | Out-Null
}

# Copy pre-commit hook
Write-Host "Installing pre-commit hook (blocks commits to main/develop)..." -ForegroundColor Cyan
Copy-Item (Join-Path $ScriptDir "pre-commit") $PreCommitHook -Force

# Copy pre-push hook
Write-Host "Installing pre-push hook (security checks on changed files)..." -ForegroundColor Cyan
Copy-Item (Join-Path $ScriptDir "pre-push") $PrePushHook -Force

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

