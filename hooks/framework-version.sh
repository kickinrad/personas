#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
plugin_root="${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}"
if [[ -z "$plugin_root" || ! -f "$plugin_root/.claude-plugin/plugin.json" ]]; then
  plugin_root=$(CDPATH='' cd -- "${script_dir}/.." && pwd)
fi
manifest="${plugin_root}/.claude-plugin/plugin.json"

[ -f .framework-version ] || exit 0
[ -f "$manifest" ] || exit 0

framework_version=$(tr -d '[:space:]' < .framework-version)
plugin_version=$(jq -r '.version // empty' "$manifest" 2>/dev/null || true)
[ -n "$framework_version" ] || exit 0
[ -n "$plugin_version" ] || exit 0
[ "$framework_version" = "$plugin_version" ] && exit 0

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Framework update available (%s -> %s). Run persona-update to inspect and reconcile drift."}}\n' \
  "$framework_version" "$plugin_version"
