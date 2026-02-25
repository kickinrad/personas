#!/usr/bin/env bash
set -euo pipefail

# Required: consume stdin
INPUT=$(cat)

PLUGIN_CACHE="${HOME}/.claude/plugins/cache/personas"
PERSONAS_HOME="${HOME}/.personas"

# No-op if no personas installed yet
[[ -d "$PLUGIN_CACHE" ]] || exit 0

for persona_dir in "$PLUGIN_CACHE"/*/; do
  [[ -d "$persona_dir" ]] || continue

  # Find latest installed version
  latest=$(ls -d "${persona_dir}"*/ 2>/dev/null | sort -V | tail -1) || continue
  [[ -n "$latest" ]] || continue

  # Only process persona plugins (have a CLAUDE.md — skips persona-manager itself)
  [[ -f "${latest}CLAUDE.md" ]] || continue

  name=$(basename "$persona_dir")
  target="$PERSONAS_HOME/$name"

  mkdir -p "$target/.claude"

  # Always update symlink → handles version bumps automatically
  ln -sf "${latest}CLAUDE.md" "$target/CLAUDE.md"

  # Always update settings.json → keeps plugin source path current
  cat > "$target/.claude/settings.json" << EOF
{
  "plugins": {
    "${name}": {
      "source": "${latest%/}"
    }
  }
}
EOF

  # Create .mcp.json template once only — never overwrite (user fills in creds)
  if [[ ! -f "$target/.mcp.json" ]]; then
    cat > "$target/.mcp.json" << 'MCPEOF'
{
  "mcpServers": {
  }
}
MCPEOF
    echo "[persona-manager] Bootstrapped ~/.personas/${name}/ — fill in .mcp.json with credentials" >&2
  fi
done
