#!/usr/bin/env bash
# personas-mesh SessionStart hook — pull the current persona's repo from the
# mesh hub before the session starts, so the session sees the latest state.
#
# Wired into each persona's hooks.json by `personas-mesh:setup`. Runs as a
# command hook; reads stdin JSON (hook_event_name, cwd, session_id, ...) and
# emits a hookSpecificOutput JSON blob on stdout ONLY when there's something
# worth surfacing (conflict, network outage). Exit is always 0 — this hook
# must never block a session.

set -euo pipefail

INPUT=$(cat)
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')
[ -z "$CWD" ] && CWD="$PWD"

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
BIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(dirname "$SCRIPT_DIR")}/bin"
SYNC_ONE="$BIN_DIR/sync-persona"

repo="$CWD"
persona=$(basename "$repo")

# Gate: no sync binary, or not a git repo — silently skip.
[ -x "$SYNC_ONE" ] || exit 0
[ -d "$repo/.git" ] || exit 0

rc=0
out=$("$SYNC_ONE" "$repo" 2>&1) || rc=$?

emit_ctx() {
  local msg="$1"
  jq -cn --arg m "$msg" \
    '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $m}}'
}

case "$rc" in
  0) : ;; # clean — no news
  2) emit_ctx "personas-mesh: sync conflict on persona ${persona}. See ~/.personas/.sync-conflicts/${persona}.log and resolve with the personas-mesh:mesh-doctor skill." ;;
  3) emit_ctx "personas-mesh: sync hub unreachable at session start — working from local state for ${persona}." ;;
  *) emit_ctx "personas-mesh: sync failed for ${persona} (exit ${rc}). Output: ${out}" ;;
esac

exit 0
