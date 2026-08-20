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

HOME="$TEST_HOME" bash "$ROOT/tests/personas-test.sh"
HOME="$TEST_HOME" python3 "$ROOT/tests/framework-contract-test.py"
HOME="$TEST_HOME" python3 "$ROOT/tests/test_fleet_verifier.py"
HOME="$TEST_HOME" python3 "$ROOT/tests/verify-fleet.py" --root "$ROOT/examples"
HOME="$TEST_HOME" python3 "$ROOT/tests/test_runtime_adapters.py"
HOME="$TEST_HOME" python3 "$ROOT/tests/test_documentation.py"
HOME="$TEST_HOME" python3 "$ROOT/tests/test_repository_inventory.py"
HOME="$TEST_HOME" python3 "$ROOT/tests/test_release.py"

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$ROOT" diff --check
  git -C "$ROOT" diff --cached --check
fi
