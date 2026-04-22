#!/usr/bin/env bash
# personas-mesh Stop hook — commit and push the persona's session changes to
# the mesh hub. Uses sync-persona's amend-if-recent logic to keep the log
# readable. Never blocks the stop — exit is always 0.

set -euo pipefail

INPUT=$(cat)
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')
[ -z "$CWD" ] && CWD="$PWD"

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
BIN_DIR="${CLAUDE_PLUGIN_ROOT:-$(dirname "$SCRIPT_DIR")}/bin"
SYNC_ONE="$BIN_DIR/sync-persona"

repo="$CWD"
persona=$(basename "$repo")

[ -x "$SYNC_ONE" ] || exit 0
[ -d "$repo/.git" ] || exit 0

rc=0
out=$("$SYNC_ONE" "$repo" 2>&1) || rc=$?

# Stop hooks don't inject context back into the session (session is over),
# so just log failures to stderr. Watchdog timer will retry transient errors.
case "$rc" in
  0|3) : ;;
  2)
    printf 'personas-mesh: post-session conflict on %s — see ~/.personas/.sync-conflicts/%s.log\n' \
      "$persona" "$persona" >&2
    ;;
  *)
    printf 'personas-mesh: post-session sync failed for %s (exit %d): %s\n' \
      "$persona" "$rc" "$out" >&2
    ;;
esac

exit 0
