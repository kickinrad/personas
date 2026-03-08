#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGINS_DIR="$REPO_ROOT/plugins"
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

  # Sandbox config (persona plugins only)
  if [[ "$name" != "persona-manager" ]]; then
    settings="$plugin_dir/.claude/settings.json"
    if [[ -f "$settings" ]]; then
      jq -e '.sandbox' "$settings" >/dev/null 2>&1 && \
        check "sandbox config present" "pass" || check "sandbox config present" "missing sandbox key"
    else
      check "sandbox config present" ".claude/settings.json missing"
    fi
  fi

  # Secret detection in committed files
  secret_hits=""
  while IFS= read -r -d '' f; do
    basename_f=$(basename "$f")
    [[ "$basename_f" == ".mcp.json" ]] && continue
    if grep -qE '(eyJ[A-Za-z0-9_-]{10,}|GOCSPX-|sk-[A-Za-z0-9]{20,}|BEGIN PRIVATE KEY)' "$f" 2>/dev/null; then
      secret_hits+=" $(realpath --relative-to="$REPO_ROOT" "$f")"
    fi
  done < <(find "$plugin_dir" \( -name "*.md" -o -name "*.json" \) -print0 2>/dev/null)
  [[ -z "$secret_hits" ]] && \
    check "no secrets in committed files" "pass" || check "no secrets in committed files" "found in:$secret_hits"

  echo ""
done

# Version sync: marketplace.json vs plugin.json
echo "Version sync checks"
marketplace="$REPO_ROOT/.claude-plugin/marketplace.json"
if [[ -f "$marketplace" ]]; then
  count=$(jq '.plugins | length' "$marketplace")
  for (( i=0; i<count; i++ )); do
    mp_name=$(jq -r ".plugins[$i].name" "$marketplace")
    mp_version=$(jq -r ".plugins[$i].version" "$marketplace")
    pjson="$PLUGINS_DIR/$mp_name/.claude-plugin/plugin.json"
    if [[ -f "$pjson" ]]; then
      pj_version=$(jq -r '.version // empty' "$pjson" 2>/dev/null)
      if [[ "$mp_version" == "$pj_version" ]]; then
        check "$mp_name version in sync ($mp_version)" "pass"
      else
        check "$mp_name version in sync" "marketplace=$mp_version plugin.json=$pj_version"
      fi
    else
      check "$mp_name version in sync" "plugin.json not found"
    fi
  done
else
  check "marketplace.json exists" "missing"
fi
echo ""

echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
