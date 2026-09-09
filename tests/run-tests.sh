#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TEST_HOME=$(mktemp -d)
cleanup() {
  find "$TEST_HOME" -depth -delete
}
trap cleanup EXIT

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$ROOT" -path "$ROOT/.git" -prune -o -name '*.sh' -type f -print0)

HOME="$TEST_HOME" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$ROOT/tests" -p 'test_*.py' -v
HOME="$TEST_HOME" PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/tests/verify-fleet.py" --root "$ROOT/examples"

if [[ -e "$ROOT/.git" ]]; then
  git -C "$ROOT" diff --check
  git -C "$ROOT" diff --cached --check
fi
