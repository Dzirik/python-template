#!/bin/bash
# Install Git hooks for the repository
# Points core.hooksPath at the tracked scripts/hooks directory instead of copying files into
# .git/hooks, so edits to the tracked hooks take effect immediately with no re-install step.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_PATH="scripts/hooks"

echo "Installing Git hooks..."

# Check if .git directory exists
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "Error: .git directory not found. Are you in a git repository?"
    exit 1
fi

# Ensure the tracked hooks are executable (git on some platforms does not preserve the bit)
chmod +x "$REPO_ROOT/$HOOKS_PATH/pre-commit" "$REPO_ROOT/$HOOKS_PATH/pre-push"

git config core.hooksPath "$HOOKS_PATH"

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "Installed hooks:"
echo "  - pre-commit: Blocks direct commits to main/develop branches"
echo "  - pre-push: Runs security checks on changed files before push"
echo ""
echo "To bypass hooks (not recommended):"
echo "  - Skip pre-commit: git commit --no-verify"
echo "  - Skip pre-push: git push --no-verify"
echo ""
