#!/usr/bin/env bash
# Public Repo Guard — prevents committing personal data to public repos
# Ships with every persona via hooks.json (PreToolUse on Bash)
#
# How it works:
#   1. Fires on git commit/push commands
#   2. Checks if the repo has a public remote (via gh)
#   3. If public, verifies user/ is gitignored and no personal files are staged
#   4. Blocks (exit 2) with a clear message if risks are found
#
# Exit codes: 0 = allow, 2 = block

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check git commit and git push
if ! echo "$COMMAND" | grep -qE '^\s*git\s+(commit|push)'; then
  exit 0
fi

# Check if we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  exit 0
fi

# Determine repo visibility — default to private (safe) if gh unavailable or no remote
VISIBILITY="private"
if command -v gh &>/dev/null && git remote get-url origin &>/dev/null 2>&1; then
  VISIBILITY=$(gh repo view --json visibility -q '.visibility' 2>/dev/null || echo "private")
fi

# Private repos can commit whatever they want
if [[ "${VISIBILITY,,}" == "private" ]]; then
  exit 0
fi

# === PUBLIC REPO CHECKS ===

ISSUES=()

# Check 1: Is user/ properly gitignored?
if ! git check-ignore -q user/ 2>/dev/null; then
  ISSUES+=("user/ directory is NOT gitignored — personal data (profile, memories) will be public")
fi

# Check 2: Are any user/ files staged for commit?
if echo "$COMMAND" | grep -qE '^\s*git\s+commit'; then
  STAGED_USER_FILES=$(git diff --cached --name-only 2>/dev/null | grep -E '^user/' || true)
  if [[ -n "$STAGED_USER_FILES" ]]; then
    ISSUES+=("Personal files staged for commit:")
    while IFS= read -r f; do
      ISSUES+=("  - $f")
    done <<< "$STAGED_USER_FILES"
  fi
fi

# Check 3: Is .mcp.json tracked? (should always be gitignored)
if git ls-files --error-unmatch .mcp.json &>/dev/null 2>&1; then
  ISSUES+=(".mcp.json is tracked — API keys and secrets will be public")
fi

# Check 4: Are any common secret patterns in staged files?
if echo "$COMMAND" | grep -qE '^\s*git\s+commit'; then
  SECRET_FILES=$(git diff --cached --name-only 2>/dev/null | grep -iE '\.(env|secret|key|pem|p12|pfx|credentials)$' || true)
  if [[ -n "$SECRET_FILES" ]]; then
    ISSUES+=("Files matching secret patterns are staged:")
    while IFS= read -r f; do
      ISSUES+=("  - $f")
    done <<< "$SECRET_FILES"
  fi
fi

# Check 5: For push — check all commits being pushed for personal data in history
if echo "$COMMAND" | grep -qE '^\s*git\s+push'; then
  DIFF_BASE=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null || \
    git rev-parse --verify origin/main 2>/dev/null || \
    git rev-parse --verify origin/master 2>/dev/null || echo "")

  if [[ -n "$DIFF_BASE" ]]; then
    HISTORY_USER_FILES=$(git diff --name-only "$DIFF_BASE"...HEAD 2>/dev/null | grep -E '^user/' || true)
    if [[ -n "$HISTORY_USER_FILES" ]]; then
      ISSUES+=("Commits being pushed contain personal data files:")
      while IFS= read -r f; do
        ISSUES+=("  - $f")
      done <<< "$HISTORY_USER_FILES"
    fi

    HISTORY_SECRET_FILES=$(git diff --name-only "$DIFF_BASE"...HEAD 2>/dev/null | grep -iE '\.(env|secret|key|pem|p12|pfx|credentials)$' || true)
    if [[ -n "$HISTORY_SECRET_FILES" ]]; then
      ISSUES+=("Commits being pushed contain secret files:")
      while IFS= read -r f; do
        ISSUES+=("  - $f")
      done <<< "$HISTORY_SECRET_FILES"
    fi
  fi
fi

# If no issues, allow
if [[ ${#ISSUES[@]} -eq 0 ]]; then
  exit 0
fi

# Block with details
{
  echo ""
  echo "PUBLIC REPO GUARD: This repository is PUBLIC. Personal data must not be committed."
  echo ""
  for issue in "${ISSUES[@]}"; do
    echo "  $issue"
  done
  echo ""
  echo "To fix:"
  echo "  1. Uncomment 'user/' in .gitignore (keeps personal data out of public repo)"
  echo "  2. Remove any staged personal files: git reset HEAD user/"
  echo "  3. Verify .mcp.json is in .gitignore"
  echo ""
  echo "If this repo should be private: gh repo edit --visibility private"
} >&2

exit 2
