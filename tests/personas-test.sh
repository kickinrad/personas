#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"
MARKETPLACE="$REPO_ROOT/.claude-plugin/marketplace.json"
PASS=0
FAIL=0

check() {
  local desc="$1" result="$2"
  if [[ "$result" == "pass" ]]; then
    echo "  ✓ $desc"
    ((PASS++)) || true
  else
    echo "  ✗ $desc: $result"
    ((FAIL++)) || true
  fi
}

for plugin_dir in "$PLUGINS_DIR"/*/; do
  name=$(basename "$plugin_dir")
  echo "Testing: $name"

  # plugin.json exists and has version
  pjson="$plugin_dir/.claude-plugin/plugin.json"
  if [[ -f "$pjson" ]]; then
    check "plugin.json exists" "pass"
    version=$(jq -r '.version // empty' "$pjson" 2>/dev/null)
    [[ -n "$version" ]] && check "version present ($version)" "pass" || check "version present" "missing"

    # Version matches marketplace.json
    mp_version=$(jq -r ".plugins[] | select(.name == \"$name\") | .version" "$MARKETPLACE" 2>/dev/null)
    [[ "$version" == "$mp_version" ]] && \
      check "version matches marketplace" "pass" || \
      check "version matches marketplace (plugin=$version, marketplace=$mp_version)" "mismatch"
  else
    check "plugin.json exists" "missing"
  fi

  # Persona plugins must have CLAUDE.md
  if [[ "$name" != "persona-manager" ]]; then
    [[ -f "$plugin_dir/CLAUDE.md" ]] && \
      check "CLAUDE.md exists" "pass" || check "CLAUDE.md exists" "missing"
  fi

  # All SKILL.md files must have YAML frontmatter
  while IFS= read -r -d '' skill; do
    grep -q "^---" "$skill" && \
      check "frontmatter: $(basename "$(dirname "$skill")")/SKILL.md" "pass" || \
      check "frontmatter: $(basename "$(dirname "$skill")")/SKILL.md" "missing"
  done < <(find "$plugin_dir/skills" -name "SKILL.md" -print0 2>/dev/null)

  echo ""
done

echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
