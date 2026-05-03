#!/usr/bin/env bash
# =============================================================
# VTT-Node → GitHub Push Script
# Run this after unzipping vtt-node-repo.zip
# =============================================================

set -euo pipefail

REPO_URL="https://github.com/jahitchcock/Vtt-node.git"
COMMIT_MSG="feat: Phase 1 + 2 — core infra, FastAPI backend, code review fixes"

echo ""
echo "VTT-Node → GitHub Push"
echo "────────────────────────────────"
echo "Target: $REPO_URL"
echo ""

cd vtt-node

if [ ! -d ".git" ]; then
    git init
    git branch -M main
    echo "✓ Git initialized"
fi

if git remote get-url origin &>/dev/null 2>&1; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

git add -A
git commit -m "$COMMIT_MSG" || echo "(Nothing new to commit)"

echo "Pushing to GitHub..."
git push -u origin main

echo "✓ Done! View at: $REPO_URL"
