#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
pass=0
fail=0

check() {
  local description="$1" result="$2"
  if [[ "$result" == pass ]]; then
    echo "  ✓ $description"
    ((pass++)) || true
  else
    echo "  ✗ $description: $result"
    ((fail++)) || true
  fi
}

echo "Testing: personas 5.0.0"

for manifest in .claude-plugin/plugin.json .codex-plugin/plugin.json; do
  version=$(jq -r '.version // empty' "$ROOT/$manifest")
  [[ "$version" == 5.0.0 ]] && check "$manifest version" pass || check "$manifest version" "expected 5.0.0, got ${version:-missing}"
done

while IFS= read -r -d '' skill; do
  grep -q '^---$' "$skill" && check "frontmatter: ${skill#"$ROOT"/}" pass || check "frontmatter: ${skill#"$ROOT"/}" missing
done < <(find "$ROOT/skills" -name SKILL.md -type f -print0)

for relative in CLAUDE.md AGENTS.md .claude/settings.json .codex/config.toml skills/atlas-review/SKILL.md; do
  [[ -f "$ROOT/examples/atlas-sanitized/$relative" ]] && check "example: $relative" pass || check "example: $relative" missing
done

[[ ! -e "$ROOT/examples/atlas-sanitized/PERSONA.md" ]] && check "example has no legacy portable definition" pass || check "example has no legacy portable definition" present

secret_hits=""
while IFS= read -r -d '' file; do
  if grep -qE '(eyJ[A-Za-z0-9_-]{20,}|GOCSPX-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|BEGIN[ ]PRIVATE[ ]KEY)' "$file" 2>/dev/null; then
    secret_hits+=" ${file#"$ROOT"/}"
  fi
done < <(find "$ROOT" -path "$ROOT/.git" -prune -o -path "$ROOT/.claude" -prune -o \( -name '*.md' -o -name '*.json' -o -name '*.toml' \) -type f -print0)
[[ -z "$secret_hits" ]] && check "no credential-like source values" pass || check "no credential-like source values" "found in:$secret_hits"

echo "Results: $pass passed, $fail failed"
[[ $fail -eq 0 ]]
