#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PERSONA_DIR="${HOME}/.personas/test-eval-persona"
CONFIG="${SCRIPT_DIR}/promptfooconfig.yaml"

# --- Usage ---
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Run persona framework end-to-end evals with promptfoo.

Options:
  --scenario N    Run only scenario N (01-07). Can be repeated.
  --view          Open the results viewer after running.
  --no-cache      Disable result caching.
  --help          Show this help message.

Examples:
  $(basename "$0")                    # Run all scenarios
  $(basename "$0") --scenario 01      # Run only scaffolding scenario
  $(basename "$0") --scenario 01 --scenario 03  # Run scenarios 01 and 03
  $(basename "$0") --view             # Run all and open viewer
EOF
}

# --- Parse args ---
SCENARIOS=()
VIEW=false
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario)
      shift
      SCENARIOS+=("$1")
      shift
      ;;
    --view)
      VIEW=true
      shift
      ;;
    --no-cache)
      EXTRA_ARGS+=("--no-cache")
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      # Pass through unknown args to promptfoo
      EXTRA_ARGS+=("$1")
      shift
      ;;
  esac
done

# --- Preflight checks ---
if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found in PATH."
  exit 1
fi

if ! command -v npx &>/dev/null; then
  echo "Error: 'npx' not found in PATH."
  exit 1
fi

echo "=== Persona Framework E2E Eval (promptfoo) ==="
echo "Config: ${CONFIG}"
echo "Persona dir: ${PERSONA_DIR}"
echo ""

# --- Build promptfoo args ---
PROMPTFOO_ARGS=("eval" "-c" "${CONFIG}")

# Filter to specific scenarios if requested
if [[ ${#SCENARIOS[@]} -gt 0 ]]; then
  FILTER_PARTS=()
  for s in "${SCENARIOS[@]}"; do
    # Pad to 2 digits
    padded=$(printf "%02d" "$s")
    FILTER_PARTS+=("${padded}")
  done
  # Join with | for regex OR
  FILTER=$(IFS='|'; echo "${FILTER_PARTS[*]}")
  PROMPTFOO_ARGS+=("--filter-pattern" "${FILTER}")
  echo "Running scenarios: ${FILTER}"
else
  echo "Running all scenarios"
fi

# Append extra args
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  PROMPTFOO_ARGS+=("${EXTRA_ARGS[@]}")
fi

echo ""

# --- Run eval ---
npx promptfoo "${PROMPTFOO_ARGS[@]}"

echo ""
echo "=== Eval complete ==="
echo "View results: npx promptfoo view"

# --- Open viewer ---
if [[ "${VIEW}" == "true" ]]; then
  echo ""
  echo "Opening results viewer..."
  npx promptfoo view
fi
