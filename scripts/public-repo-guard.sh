#!/usr/bin/env bash
# Persona publishing guard. Run this at a Git/CI/release seam, not as a shell
# command parser. It blocks private state and credentials for every repository.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: public-repo-guard.sh --check-staged|--check-repository|--check-tree <treeish>|--check-cloud-binding|--cloud-preflight [owner/repo]

--check-staged     inspect the staged Git index before commit or release
--check-repository inspect every file in the committed HEAD tree (fails closed without HEAD)
--check-tree REF   inspect one committed tree (suitable for CI/release)
--check-cloud-binding  verify the committed Cloud marker matches this checkout
--cloud-preflight  require authenticated GitHub evidence of exactly PRIVATE
EOF
}

die() { echo "PERSONA PUBLISHING GUARD: $*" >&2; exit 2; }

private_path() {
  case "$1" in
    user|user/*|.mcp.json|.mcp.json.*|.claude/settings.local.json|.claude/settings.local.json.*|.claude/settings.*.local.json|.env|.env.*|*.env|*.key|*.pem|*.p12|*.pfx|*.secret|*credentials*|secrets|secrets/*)
      return 0 ;;
    *) return 1 ;;
  esac
}

secret_content() {
  # Conservative markers cover the credential forms that must never enter Git.
  grep -Eqi '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|(^|[^[:alnum:]_])(api[_-]?key|access[_-]?token|auth[_-]?token|secret|password)[[:space:]]*[:=]|gh[pousr]_[A-Za-z0-9_]{12,}|sk-[A-Za-z0-9_-]{12,}|Bearer[[:space:]]+[A-Za-z0-9._-]{12,})'
}

check_stream() {
  local source_prefix="$1" path content issues=0
  while IFS= read -r -d '' path; do
    if private_path "$path"; then
      echo "blocked private path: $path" >&2
      issues=1
      continue
    fi
    if ! content="$(git show "${source_prefix}${path}" 2>/dev/null)"; then
      echo "unable to inspect tracked content: $path" >&2
      issues=1
      continue
    fi
    if [[ -n "$content" ]] && printf '%s' "$content" | secret_content; then
      echo "blocked credential-like content: $path" >&2
      issues=1
    fi
  done
  return "$issues"
}

check_staged() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a Git worktree"
  if ! git diff --cached --name-only -z --diff-filter=ACMR | check_stream ':'; then
    die "staged content is not publishable; remove it from the index"
  fi
}

check_repository() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a Git worktree"
  git rev-parse --verify 'HEAD^{tree}' >/dev/null 2>&1 || die "committed HEAD tree is unavailable for inspection"
  if ! git ls-tree -rz --name-only HEAD | check_stream 'HEAD:'; then
    die "committed HEAD content is not publishable"
  fi
}

check_tree() {
  local ref="$1"
  git rev-parse --verify "${ref}^{tree}" >/dev/null 2>&1 || die "cannot inspect tree: $ref"
  if ! git ls-tree -rz --name-only "$ref" | check_stream "${ref}:"; then
    die "tree $ref is not publishable"
  fi
}

check_cloud_binding() {
  local repo="${1:-}" marker committed
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Cloud binding check requires a Git worktree"
  if [[ -z "$repo" ]]; then
    repo="$(git config --get remote.origin.url 2>/dev/null || true)"
  fi
  [[ -n "$repo" ]] || die "GitHub repository identity is unavailable"
  case "$repo" in
    git@github.com:*) repo="${repo#git@github.com:}" ;;
    https://github.com/*) repo="${repo#https://github.com/}" ;;
  esac
  repo="${repo%.git}"
  [[ "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "GitHub repository identity is ambiguous"
  marker=".persona-cloud-repository"
  [[ -f "$marker" ]] || die "Cloud repository binding marker is missing"
  git ls-files --error-unmatch -- "$marker" >/dev/null 2>&1 ||
    die "Cloud repository binding marker must be tracked"
  git cat-file -e "HEAD:$marker" 2>/dev/null ||
    die "Cloud repository binding marker is missing from committed HEAD"
  committed="$(git show "HEAD:$marker" 2>/dev/null)" ||
    die "Cloud repository binding marker cannot be read from committed HEAD"
  [[ "$(<"$marker")" == "$committed" ]] ||
    die "Cloud repository binding marker differs from committed HEAD"
  [[ "$(<"$marker")" == "$repo" ]] || die "Cloud repository binding marker does not match origin"
  CLOUD_REPOSITORY="$repo"
}

cloud_preflight() {
  local gh_bin="${PERSONA_GITHUB_CLI:-gh}" visibility
  check_cloud_binding "${1:-}"
  command -v "$gh_bin" >/dev/null 2>&1 || die "authenticated GitHub inspection is unavailable"
  visibility="$($gh_bin repo view "$CLOUD_REPOSITORY" --json visibility --jq .visibility 2>/dev/null || true)"
  [[ "$visibility" == "PRIVATE" ]] || die "GitHub visibility is not proven PRIVATE (reported: ${visibility:-unknown})"
}

case "${1:-}" in
  --check-staged) [[ $# -eq 1 ]] || { usage; exit 64; }; check_staged ;;
  --check-repository) [[ $# -eq 1 ]] || { usage; exit 64; }; check_repository ;;
  --check-tree) [[ $# -eq 2 ]] || { usage; exit 64; }; check_tree "$2" ;;
  --check-cloud-binding) [[ $# -eq 1 ]] || { usage; exit 64; }; check_cloud_binding ;;
  --cloud-preflight) [[ $# -le 2 ]] || { usage; exit 64; }; cloud_preflight "${2:-}" ;;
  *) usage; exit 64 ;;
esac
