#!/usr/bin/env bash
set -euo pipefail

ROOT=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
TEST_HOME=$(mktemp -d)
cleanup() {
  find "$TEST_HOME" -depth -delete
}
trap cleanup EXIT

HOME="$TEST_HOME" bash "$ROOT/tests/personas-test.sh"
HOME="$TEST_HOME" python3 "$ROOT/tests/framework-contract-test.py"
