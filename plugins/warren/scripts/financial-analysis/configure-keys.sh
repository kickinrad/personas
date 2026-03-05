#!/usr/bin/env bash
# Warren — Financial Analysis Engine Key Configurator
#
# Run this from your terminal (needs GPG TTY for pass):
#   cd scripts/financial-analysis && ./configure-keys.sh
#
# Reads API keys from pass and writes them to ~/.financial-analysis/api_keys.json
# so the engine can run headlessly (no env var injection needed).

set -e

CONFIG="$HOME/.financial-analysis/api_keys.json"

if [ ! -f "$CONFIG" ]; then
    echo "Config not found. Run: python scripts/api_config.py init"
    exit 1
fi

echo "Warren — configuring API keys from pass..."
echo ""

write_key() {
    local api_id="$1"
    local pass_path="$2"
    local key

    key=$(pass show "$pass_path" 2>/dev/null) || { echo "  ✗ $pass_path (not found in pass — skipping)"; return; }

    if [ -z "$key" ]; then
        echo "  ✗ $pass_path (empty — skipping)"
        return
    fi

    python3 -c "
import json
with open('$CONFIG') as f:
    config = json.load(f)
config.setdefault('apis', {}).setdefault('$api_id', {})['api_key'] = '''$key'''
config['apis']['$api_id']['enabled'] = True
with open('$CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
    echo "  ✓ $pass_path → $api_id"
}

write_key "finnhub"               "apis/finnhub"
write_key "alpha_vantage"         "apis/alpha-vantage"
write_key "mboum"                 "apis/mboum"
write_key "seeking_alpha_rapidapi" "apis/seeking-alpha-rapidapi"
write_key "polygon"               "apis/polygon"
write_key "alpaca"                "apis/alpaca"
write_key "fmp"                   "apis/fmp"

echo ""
echo "Done. Run 'python scripts/api_config.py status' to verify."
