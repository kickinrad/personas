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

  # All SKILL.md files must have YAML frontmatter
  while IFS= read -r -d '' skill; do
    grep -q "^---" "$skill" && \
      check "frontmatter: $(basename "$(dirname "$skill")")/SKILL.md" "pass" || \
      check "frontmatter: $(basename "$(dirname "$skill")")/SKILL.md" "missing"
  done < <(find "$plugin_dir/skills" -name "SKILL.md" -print0 2>/dev/null)

  # Secret detection in committed files. Secret prefixes must be followed by
  # ≥20 base64url chars to rule out bare-prefix docs (e.g. "GOCSPX-" listed as
  # an example pattern in validator agent prose).
  secret_hits=""
  while IFS= read -r -d '' f; do
    basename_f=$(basename "$f")
    [[ "$basename_f" == ".mcp.json" ]] && continue
    if grep -qE '(eyJ[A-Za-z0-9_-]{20,}|GOCSPX-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}|BEGIN PRIVATE KEY)' "$f" 2>/dev/null; then
      secret_hits+=" ${f#"$REPO_ROOT"/}"
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

# Persona directory checks (~/.personas/)
PERSONAS_DIR="$HOME/.personas"
if [[ -d "$PERSONAS_DIR" ]]; then
  echo "Persona directory checks (~/.personas/)"
  for persona_dir in "$PERSONAS_DIR"/*/; do
    [[ -d "$persona_dir" ]] || continue
    pname=$(basename "$persona_dir")
    echo "  Checking: $pname"

    # Must have CLAUDE.md
    [[ -f "$persona_dir/CLAUDE.md" ]] && \
      check "CLAUDE.md exists" "pass" || check "CLAUDE.md exists" "missing"

    # Stub-mode: persona lives elsewhere via .persona-cwd redirect.
    # Skip structural checks (sandbox / user / settings.local / .gitignore) — those live at the redirect target.
    if [[ -f "$persona_dir/.persona-cwd" ]]; then
      pcwd=$(tr -d '[:space:]' < "$persona_dir/.persona-cwd")
      if [[ -d "$pcwd" ]]; then
        check ".persona-cwd resolves ($pcwd)" "pass"
      else
        check ".persona-cwd resolves" "target does not exist: $pcwd"
      fi
    else
      # Standard persona — full structural checks
      # Must have sandbox config
      psettings="$persona_dir/.claude/settings.json"
      if [[ -f "$psettings" ]]; then
        jq -e '.sandbox' "$psettings" >/dev/null 2>&1 && \
          check "sandbox config present" "pass" || check "sandbox config present" "missing sandbox key"
      else
        check "sandbox config present" ".claude/settings.json missing"
      fi

      # Must have user/ directory
      [[ -d "$persona_dir/user" ]] && \
        check "user/ directory exists" "pass" || check "user/ directory exists" "missing"

      # Must have autoMemoryDirectory in settings.local.json (not settings.json — Claude ignores it there)
      plocal="$persona_dir/.claude/settings.local.json"
      if [[ -f "$plocal" ]]; then
        jq -e '.autoMemoryDirectory' "$plocal" >/dev/null 2>&1 && \
          check "autoMemoryDirectory configured" "pass" || check "autoMemoryDirectory configured" "missing in settings.local.json"
      else
        check "autoMemoryDirectory configured" "settings.local.json not found"
      fi

      # Must have .gitignore
      [[ -f "$persona_dir/.gitignore" ]] && \
        check ".gitignore exists" "pass" || check ".gitignore exists" "missing"
    fi

    # Framework version stamp
    fwversion="$persona_dir/.framework-version"
    if [[ -f "$fwversion" ]]; then
      fv=$(cat "$fwversion" | tr -d '[:space:]')
      if [[ "$fv" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        check ".framework-version valid ($fv)" "pass"
      else
        check ".framework-version valid" "invalid format: $fv"
      fi
    else
      echo "    ℹ .framework-version not found (run persona-update to add)"
    fi

    # No secrets in committed files
    psecret_hits=""
    while IFS= read -r -d '' f; do
      basename_f=$(basename "$f")
      [[ "$basename_f" == ".mcp.json" ]] && continue
      if grep -qE '(eyJ[A-Za-z0-9_-]{10,}|GOCSPX-|sk-[A-Za-z0-9]{20,}|BEGIN PRIVATE KEY)' "$f" 2>/dev/null; then
        psecret_hits+=" $f"
      fi
    done < <(find "$persona_dir" \( -name "*.md" -o -name "*.json" \) -print0 2>/dev/null)
    [[ -z "$psecret_hits" ]] && \
      check "no secrets in files" "pass" || check "no secrets in files" "found in:$psecret_hits"

    echo ""
  done
else
  echo "Persona directory checks (~/.personas/): skipped (directory not found)"
  echo ""
fi

echo "Results: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
