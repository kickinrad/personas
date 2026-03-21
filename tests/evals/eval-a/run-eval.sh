#!/usr/bin/env bash
# run-eval.sh — Orchestrate persona framework evals
# Usage:
#   ./run-eval.sh --scenario 1          # Run scenario 1
#   ./run-eval.sh --scenario 1,3,5      # Run scenarios 1, 3, and 5
#   ./run-eval.sh --all                 # Run all 7 scenarios
#   ./run-eval.sh --all --runs 3        # Run all scenarios 3 times each
#   ./run-eval.sh --scenario 1 --dry-run # Show what would run without executing

set -euo pipefail

# ── Constants ──────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVALS_JSON="${SCRIPT_DIR}/evals.json"
EXECUTOR_MD="${SCRIPT_DIR}/agents/executor.md"
GRADER_MD="${SCRIPT_DIR}/agents/grader.md"
RUNS_DIR="${SCRIPT_DIR}/runs"
PERSONA_DIR="${HOME}/.personas/test-eval-persona"
FRAMEWORK_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# ── Colors ─────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

# ── Defaults ───────────────────────────────────────────────────────
SCENARIOS=""
RUN_ALL=false
NUM_RUNS=1
DRY_RUN=false
VERBOSE=false

# ── Parse args ─────────────────────────────────────────────────────
usage() {
    cat <<'USAGE'
Usage: run-eval.sh [OPTIONS]

Options:
  --scenario N[,N...]   Run specific scenario(s) by ID (1-7)
  --all                 Run all scenarios
  --runs N              Number of repetitions per scenario (default: 1)
  --dry-run             Show what would run without executing
  --verbose             Show detailed output during execution
  -h, --help            Show this help

Examples:
  ./run-eval.sh --scenario 1
  ./run-eval.sh --scenario 1,3,5 --runs 2
  ./run-eval.sh --all --dry-run
USAGE
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scenario)
            SCENARIOS="$2"
            shift 2
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        --runs)
            NUM_RUNS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${RESET}" >&2
            usage
            ;;
    esac
done

if [[ "$RUN_ALL" == false && -z "$SCENARIOS" ]]; then
    echo -e "${RED}Error: Must specify --scenario N or --all${RESET}" >&2
    usage
fi

# ── Validate prerequisites ────────────────────────────────────────
check_prereqs() {
    local missing=()

    if ! command -v claude &>/dev/null; then
        missing+=("claude")
    fi
    if ! command -v jq &>/dev/null; then
        missing+=("jq")
    fi
    if [[ ! -f "$EVALS_JSON" ]]; then
        missing+=("evals.json (expected at ${EVALS_JSON})")
    fi
    if [[ ! -f "$EXECUTOR_MD" ]]; then
        missing+=("executor.md (expected at ${EXECUTOR_MD})")
    fi
    if [[ ! -f "$GRADER_MD" ]]; then
        missing+=("grader.md (expected at ${GRADER_MD})")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Missing prerequisites:${RESET}"
        for m in "${missing[@]}"; do
            echo -e "  ${RED}- ${m}${RESET}"
        done
        exit 1
    fi
}

# ── Helper functions ──────────────────────────────────────────────

log() {
    echo -e "${DIM}[$(date '+%H:%M:%S')]${RESET} $*"
}

log_step() {
    echo -e "${CYAN}  >>>${RESET} $*"
}

get_scenario_ids() {
    if [[ "$RUN_ALL" == true ]]; then
        jq -r '.evals[].id' "$EVALS_JSON"
    else
        echo "$SCENARIOS" | tr ',' '\n'
    fi
}

get_scenario_field() {
    local id="$1"
    local field="$2"
    jq -r --argjson id "$id" '.evals[] | select(.id == $id) | '"$field" "$EVALS_JSON"
}

get_scenario_json() {
    local id="$1"
    jq --argjson id "$id" '.evals[] | select(.id == $id)' "$EVALS_JSON"
}

expand_tilde() {
    echo "${1/#\~/$HOME}"
}

# ── Take filesystem snapshot ──────────────────────────────────────
take_snapshot() {
    local persona_dir="$1"
    local snapshot_dir="$2"
    local label="$3"

    mkdir -p "${snapshot_dir}"

    if [[ -d "$persona_dir" ]]; then
        find "$persona_dir" -type f -not -path '*/.git/*' 2>/dev/null | sort > "${snapshot_dir}/${label}_files.txt" || true
        find "$persona_dir" -type f -not -path '*/.git/*' -exec md5sum {} \; 2>/dev/null | sort > "${snapshot_dir}/${label}_checksums.txt" || true

        # Copy key files for diff
        local key_dir="${snapshot_dir}/${label}"
        mkdir -p "$key_dir"
        for f in user/profile.md user/memory/MEMORY.md hooks.json .claude-flags .claude/settings.json .gitignore; do
            if [[ -f "${persona_dir}/$f" ]]; then
                mkdir -p "$(dirname "${key_dir}/$f")"
                cp "${persona_dir}/$f" "${key_dir}/$f"
            fi
        done
    else
        touch "${snapshot_dir}/${label}_files.txt"
        touch "${snapshot_dir}/${label}_checksums.txt"
    fi
}

# ── Compute diffs between snapshots ───────────────────────────────
compute_diffs() {
    local snapshot_dir="$1"
    local persona_dir="$2"

    # New files
    comm -13 "${snapshot_dir}/before_files.txt" "${snapshot_dir}/after_files.txt" > "${snapshot_dir}/new_files.txt" 2>/dev/null || true

    # Deleted files
    comm -23 "${snapshot_dir}/before_files.txt" "${snapshot_dir}/after_files.txt" > "${snapshot_dir}/deleted_files.txt" 2>/dev/null || true

    # Modified files
    diff "${snapshot_dir}/before_checksums.txt" "${snapshot_dir}/after_checksums.txt" > "${snapshot_dir}/modified_checksums.diff" 2>/dev/null || true

    # Content diffs for key files
    for f in user/profile.md user/memory/MEMORY.md hooks.json .claude-flags .claude/settings.json .gitignore; do
        local safe_name
        safe_name="$(echo "$f" | tr '/' '_')"
        if [[ -f "${snapshot_dir}/before/$f" && -f "${persona_dir}/$f" ]]; then
            diff -u "${snapshot_dir}/before/$f" "${persona_dir}/$f" > "${snapshot_dir}/diff_${safe_name}.diff" 2>/dev/null || true
        fi
    done
}

# ── Run a single scenario ─────────────────────────────────────────
run_scenario() {
    local scenario_id="$1"
    local run_number="$2"
    local run_dir="$3"
    local scenario_json
    local scenario_name
    local setup_script
    local teardown_script
    local prompt

    scenario_json="$(get_scenario_json "$scenario_id")"
    scenario_name="$(echo "$scenario_json" | jq -r '.name')"
    setup_script="$(echo "$scenario_json" | jq -r '.setup.script // empty')"
    teardown_script="$(echo "$scenario_json" | jq -r '.teardown.script // empty')"
    prompt="$(echo "$scenario_json" | jq -r '.prompt')"

    local scenario_run_dir="${run_dir}/scenario-${scenario_id}"
    local outputs_dir="${scenario_run_dir}/outputs"
    local snapshots_dir="${scenario_run_dir}/snapshots"

    mkdir -p "$outputs_dir" "$snapshots_dir"

    echo -e "${BOLD}${BLUE}=== Scenario ${scenario_id}: ${scenario_name} (run ${run_number}) ===${RESET}"

    # ── Dry run ──
    if [[ "$DRY_RUN" == true ]]; then
        echo -e "${YELLOW}  [DRY RUN] Would execute:${RESET}"
        echo -e "${DIM}    Setup: ${setup_script:-'(none)'}${RESET}"
        echo -e "${DIM}    Prompt: ${prompt}${RESET}"
        echo -e "${DIM}    Teardown: ${teardown_script:-'(none)'}${RESET}"
        echo -e "${DIM}    Run dir: ${scenario_run_dir}${RESET}"
        return 0
    fi

    # ── Setup ──
    if [[ -n "$setup_script" ]]; then
        log_step "Running setup..."
        if eval "$setup_script" > "${outputs_dir}/setup.log" 2>&1; then
            log_step "Setup completed"
        else
            echo -e "${RED}  Setup failed! Check ${outputs_dir}/setup.log${RESET}"
            cp "${outputs_dir}/setup.log" "${outputs_dir}/setup_error.log"
            return 1
        fi
    fi

    # ── Before snapshot ──
    log_step "Taking before snapshot..."
    take_snapshot "$(expand_tilde "$PERSONA_DIR")" "$snapshots_dir" "before"

    # ── Record start time ──
    local executor_start
    executor_start="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local executor_start_epoch
    executor_start_epoch="$(date +%s)"

    # ── Execute session (direct — no nested subagent) ──
    log_step "Running Claude session in persona dir..."

    local expanded_persona_dir
    expanded_persona_dir="$(expand_tilde "$PERSONA_DIR")"

    # Run Claude directly in the persona directory, capturing output
    local session_exit_code=0
    if cd "$expanded_persona_dir" && \
       claude --setting-sources project,local -p "$prompt" --output-format text --verbose \
           > "${outputs_dir}/session_stdout.txt" 2>"${outputs_dir}/session_stderr.txt"; then
        log_step "Session completed (exit 0)"
    else
        session_exit_code=$?
        echo -e "${YELLOW}  Session exited with code ${session_exit_code} (may be expected)${RESET}"
    fi
    cd "$SCRIPT_DIR"  # Return to eval dir

    # Write transcript from captured output
    cat > "${scenario_run_dir}/transcript.md" <<TRANSCRIPT
# Eval Transcript — Scenario ${scenario_id}: ${scenario_name}

## Prompt
\`\`\`
${prompt}
\`\`\`

## Session Output
\`\`\`
$(cat "${outputs_dir}/session_stdout.txt" 2>/dev/null || echo "(no output)")
\`\`\`

## Stderr
\`\`\`
$(cat "${outputs_dir}/session_stderr.txt" 2>/dev/null || echo "(none)")
\`\`\`

## Exit Code
${session_exit_code}
TRANSCRIPT

    # Write basic metrics
    local output_chars
    output_chars=$(wc -c < "${outputs_dir}/session_stdout.txt" 2>/dev/null || echo 0)
    cat > "${outputs_dir}/metrics.json" <<METRICS
{
  "exit_code": ${session_exit_code},
  "output_chars": ${output_chars},
  "transcript_chars": $(wc -c < "${scenario_run_dir}/transcript.md" 2>/dev/null || echo 0)
}
METRICS

    log_step "Executor completed"

    # ── Record end time ──
    local executor_end
    executor_end="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    local executor_end_epoch
    executor_end_epoch="$(date +%s)"
    local executor_duration=$(( executor_end_epoch - executor_start_epoch ))

    # ── After snapshot ──
    log_step "Taking after snapshot..."
    take_snapshot "$(expand_tilde "$PERSONA_DIR")" "$snapshots_dir" "after"

    # ── Compute diffs ──
    log_step "Computing diffs..."
    compute_diffs "$snapshots_dir" "$(expand_tilde "$PERSONA_DIR")"

    # ── Write timing ──
    cat > "${scenario_run_dir}/timing.json" <<TIMING_JSON
{
  "executor_start": "${executor_start}",
  "executor_end": "${executor_end}",
  "executor_duration_seconds": ${executor_duration}
}
TIMING_JSON

    # ── Launch grader ──
    log_step "Launching grader agent..."

    local grader_start_epoch
    grader_start_epoch="$(date +%s)"

    local expectations
    expectations="$(echo "$scenario_json" | jq -r '.expectations[]' 2>/dev/null | sed 's/^/- /')"

    local grader_prompt
    grader_prompt="$(cat <<GRADER_PROMPT
You are the grader agent for persona framework evals.

## Instructions
$(cat "$GRADER_MD")

## Scenario
$(echo "$scenario_json" | jq .)

## Paths
- Transcript: ${scenario_run_dir}/transcript.md
- Outputs dir: ${outputs_dir}
- Snapshots dir: ${snapshots_dir}
- Persona dir: $(expand_tilde "$PERSONA_DIR")
- Run dir: ${scenario_run_dir}

## Expectations
${expectations}

## Task
Grade this scenario execution now. Read the transcript, examine outputs, run code assertions against the actual persona directory, and evaluate LLM assertions.

## CRITICAL OUTPUT INSTRUCTION
You MUST output ONLY a valid JSON object as your final response — no markdown, no explanation, no code fences. The JSON must follow the grading.json schema with these top-level keys: expectations, summary, claims, eval_feedback. The summary must include: total_passed, total_failed, total, pass_rate. Output the raw JSON object and nothing else.
GRADER_PROMPT
)"

    # Capture grader output — extract JSON from stdout
    local grader_output
    grader_output="$(claude -p "$grader_prompt" 2>"${outputs_dir}/grader_agent.log")"

    # Try to extract JSON from grader output (may include non-JSON text before/after)
    if echo "$grader_output" | jq . > /dev/null 2>&1; then
        echo "$grader_output" | jq . > "${scenario_run_dir}/grading.json"
        log_step "Grader completed — grading.json written"
    elif echo "$grader_output" | grep -oP '\{[^{}]*("expectations"|"summary")[^{}]*\}' > /dev/null 2>&1; then
        # Try to find JSON embedded in text
        echo "$grader_output" | python3 -c "
import sys, json, re
text = sys.stdin.read()
# Find the largest JSON object
matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
for m in reversed(sorted(matches, key=len)):
    try:
        obj = json.loads(m)
        if 'summary' in obj or 'expectations' in obj:
            print(json.dumps(obj, indent=2))
            sys.exit(0)
    except: pass
sys.exit(1)
" > "${scenario_run_dir}/grading.json" 2>/dev/null && \
            log_step "Grader completed — grading.json extracted from output" || {
            # Fallback: save raw output as grading log
            echo "$grader_output" > "${outputs_dir}/grader_raw_output.txt"
            echo -e "${YELLOW}  Grader produced output but no parseable JSON — saved to grader_raw_output.txt${RESET}"
        }
    else
        echo "$grader_output" > "${outputs_dir}/grader_raw_output.txt"
        echo -e "${YELLOW}  Grader produced no parseable JSON — saved to grader_raw_output.txt${RESET}"
    fi

    local grader_end_epoch
    grader_end_epoch="$(date +%s)"
    local grader_duration=$(( grader_end_epoch - grader_start_epoch ))
    local total_duration=$(( grader_end_epoch - executor_start_epoch ))

    # ── Update timing with grader info ──
    if [[ -f "${scenario_run_dir}/timing.json" ]]; then
        local grader_start
        grader_start="$(date -u -d "@${grader_start_epoch}" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
        local grader_end
        grader_end="$(date -u -d "@${grader_end_epoch}" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"

        jq --argjson gd "$grader_duration" \
           --argjson td "$total_duration" \
           --arg gs "$grader_start" \
           --arg ge "$grader_end" \
           '. + {grader_start: $gs, grader_end: $ge, grader_duration_seconds: $gd, total_duration_seconds: $td}' \
           "${scenario_run_dir}/timing.json" > "${scenario_run_dir}/timing.json.tmp" \
           && mv "${scenario_run_dir}/timing.json.tmp" "${scenario_run_dir}/timing.json"
    fi

    # ── Teardown ──
    if [[ -n "$teardown_script" ]]; then
        log_step "Running teardown..."
        eval "$teardown_script" > "${outputs_dir}/teardown.log" 2>&1 || true
    fi

    # ── Print scenario result ──
    if [[ -f "${scenario_run_dir}/grading.json" ]]; then
        local pass_rate
        pass_rate="$(jq -r '.summary.pass_rate // 0' "${scenario_run_dir}/grading.json" 2>/dev/null || echo "0")"
        local passed
        passed="$(jq -r '.summary.total_passed // 0' "${scenario_run_dir}/grading.json" 2>/dev/null || echo "0")"
        local total
        total="$(jq -r '.summary.total // 0' "${scenario_run_dir}/grading.json" 2>/dev/null || echo "0")"

        if (( $(echo "$pass_rate >= 0.8" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${GREEN}  RESULT: ${passed}/${total} passed (${pass_rate}) [${total_duration}s]${RESET}"
        elif (( $(echo "$pass_rate >= 0.5" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${YELLOW}  RESULT: ${passed}/${total} passed (${pass_rate}) [${total_duration}s]${RESET}"
        else
            echo -e "${RED}  RESULT: ${passed}/${total} passed (${pass_rate}) [${total_duration}s]${RESET}"
        fi
    else
        echo -e "${RED}  RESULT: No grading.json produced${RESET}"
    fi

    echo ""
}

# ── Aggregate results ─────────────────────────────────────────────
print_summary() {
    local run_dir="$1"

    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║                     EVAL SUMMARY                            ║${RESET}"
    echo -e "${BOLD}${BLUE}╠══════════════════════════════════════════════════════════════╣${RESET}"

    printf "${BOLD}${BLUE}║${RESET} %-4s %-25s %-8s %-8s %-8s ${BOLD}${BLUE}║${RESET}\n" "ID" "Scenario" "Passed" "Total" "Rate"
    echo -e "${BOLD}${BLUE}╠══════════════════════════════════════════════════════════════╣${RESET}"

    local total_passed=0
    local total_assertions=0
    local scenarios_run=0
    local scenarios_passed=0

    for grading_file in "${run_dir}"/scenario-*/grading.json; do
        if [[ ! -f "$grading_file" ]]; then
            continue
        fi

        local scenario_dir
        scenario_dir="$(dirname "$grading_file")"
        local scenario_id
        scenario_id="$(basename "$scenario_dir" | sed 's/scenario-//')"
        local scenario_name
        scenario_name="$(jq -r '.scenario.name // "unknown"' "$grading_file" 2>/dev/null || echo "unknown")"
        local passed
        passed="$(jq -r '.summary.total_passed // 0' "$grading_file" 2>/dev/null || echo "0")"
        local total
        total="$(jq -r '.summary.total // 0' "$grading_file" 2>/dev/null || echo "0")"
        local rate
        rate="$(jq -r '.summary.pass_rate // 0' "$grading_file" 2>/dev/null || echo "0")"

        local color="$RED"
        if (( $(echo "$rate >= 0.8" | bc -l 2>/dev/null || echo 0) )); then
            color="$GREEN"
        elif (( $(echo "$rate >= 0.5" | bc -l 2>/dev/null || echo 0) )); then
            color="$YELLOW"
        fi

        printf "${BOLD}${BLUE}║${RESET} ${color}%-4s %-25s %-8s %-8s %-8s${RESET} ${BOLD}${BLUE}║${RESET}\n" \
            "$scenario_id" "$scenario_name" "$passed" "$total" "$rate"

        total_passed=$(( total_passed + passed ))
        total_assertions=$(( total_assertions + total ))
        scenarios_run=$(( scenarios_run + 1 ))
        if (( $(echo "$rate >= 0.8" | bc -l 2>/dev/null || echo 0) )); then
            scenarios_passed=$(( scenarios_passed + 1 ))
        fi
    done

    echo -e "${BOLD}${BLUE}╠══════════════════════════════════════════════════════════════╣${RESET}"

    local overall_rate="0"
    if [[ "$total_assertions" -gt 0 ]]; then
        overall_rate="$(echo "scale=2; $total_passed / $total_assertions" | bc -l 2>/dev/null || echo "0")"
    fi

    local overall_color="$RED"
    if (( $(echo "$overall_rate >= 0.8" | bc -l 2>/dev/null || echo 0) )); then
        overall_color="$GREEN"
    elif (( $(echo "$overall_rate >= 0.5" | bc -l 2>/dev/null || echo 0) )); then
        overall_color="$YELLOW"
    fi

    printf "${BOLD}${BLUE}║${RESET} ${overall_color}${BOLD}%-4s %-25s %-8s %-8s %-8s${RESET} ${BOLD}${BLUE}║${RESET}\n" \
        "" "TOTAL" "$total_passed" "$total_assertions" "$overall_rate"

    echo -e "${BOLD}${BLUE}╠══════════════════════════════════════════════════════════════╣${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET} Scenarios: ${scenarios_passed}/${scenarios_run} passed (>= 80% threshold)           ${BOLD}${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET} Results:   ${run_dir}  ${BOLD}${BLUE}${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
}

# ── Main ──────────────────────────────────────────────────────────
main() {
    check_prereqs

    echo ""
    echo -e "${BOLD}${CYAN}  Persona Framework Eval System A${RESET}"
    echo -e "${DIM}  $(date)${RESET}"
    echo ""

    # Build list of scenario IDs
    local scenario_ids
    mapfile -t scenario_ids < <(get_scenario_ids)

    if [[ ${#scenario_ids[@]} -eq 0 ]]; then
        echo -e "${RED}No scenarios to run${RESET}"
        exit 1
    fi

    # Validate scenario IDs
    for sid in "${scenario_ids[@]}"; do
        local name
        name="$(get_scenario_field "$sid" '.name' 2>/dev/null)"
        if [[ -z "$name" || "$name" == "null" ]]; then
            echo -e "${RED}Error: Scenario ID ${sid} not found in evals.json${RESET}"
            exit 1
        fi
        log "Found scenario ${sid}: ${name}"
    done

    echo ""

    # Run each scenario × repetitions
    for run_num in $(seq 1 "$NUM_RUNS"); do
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local run_dir="${RUNS_DIR}/${timestamp}"

        if [[ "$NUM_RUNS" -gt 1 ]]; then
            echo -e "${BOLD}── Run ${run_num}/${NUM_RUNS} ──${RESET}"
            run_dir="${RUNS_DIR}/${timestamp}_run${run_num}"
        fi

        mkdir -p "$run_dir"

        # Save run metadata
        cat > "${run_dir}/run_meta.json" <<META_JSON
{
  "timestamp": "${timestamp}",
  "run_number": ${run_num},
  "total_runs": ${NUM_RUNS},
  "scenarios": [$(IFS=,; echo "${scenario_ids[*]}")],
  "dry_run": ${DRY_RUN},
  "framework_dir": "${FRAMEWORK_DIR}",
  "persona_dir": "${PERSONA_DIR}"
}
META_JSON

        for sid in "${scenario_ids[@]}"; do
            run_scenario "$sid" "$run_num" "$run_dir" || {
                echo -e "${RED}Scenario ${sid} failed — continuing to next${RESET}"
                continue
            }
        done

        # Print summary for this run
        if [[ "$DRY_RUN" == false ]]; then
            print_summary "$run_dir"
        fi
    done
}

main "$@"
