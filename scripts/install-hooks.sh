#!/bin/bash
# Install Git hooks for the repository
# This script copies pre-push hook to .git/hooks/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
PRE_COMMIT_HOOK="$HOOKS_DIR/pre-commit"
PRE_PUSH_HOOK="$HOOKS_DIR/pre-push"

echo "Installing Git hooks..."

# Check if .git directory exists
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "Error: .git directory not found. Are you in a git repository?"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Copy pre-commit hook
echo "Installing pre-commit hook (blocks commits to main/develop)..."
cp "$SCRIPT_DIR/pre-commit" "$PRE_COMMIT_HOOK"
chmod +x "$PRE_COMMIT_HOOK"

# Copy pre-push hook
echo "Installing pre-push hook (security checks on changed files)..."
cp "$SCRIPT_DIR/pre-push" "$PRE_PUSH_HOOK"
chmod +x "$PRE_PUSH_HOOK"

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

