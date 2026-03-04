#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
#  Financial Analysis Skill — Setup
# ═══════════════════════════════════════════════════════════════
#  Creates a Python virtual environment, installs pinned
#  dependencies, and initializes the API config.
#
#  Usage:
#    chmod +x setup.sh
#    ./setup.sh
#
#  After setup, activate the venv before running anything:
#    source .venv/bin/activate
# ═══════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

# ── Check Python version ────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Financial Analysis Skill — Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

PY_VERSION=$($PYTHON --version 2>&1)
echo "Using: $PY_VERSION"

# Require Python 3.9+
PY_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]); then
    echo "ERROR: Python 3.9+ is required (found $PY_VERSION)"
    echo "Install a newer Python or set PYTHON=python3.11 ./setup.sh"
    exit 1
fi

# ── Create venv ─────────────────────────────────────────────────
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    echo "To recreate: rm -rf $VENV_DIR && ./setup.sh"
else
    echo "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    echo "  → $VENV_DIR created"
fi

# ── Activate & upgrade pip ──────────────────────────────────────
source "$VENV_DIR/bin/activate"
echo "Upgrading pip..."
pip install --upgrade pip -q

# ── Install core dependencies ───────────────────────────────────
echo "Installing core dependencies..."
pip install -r requirements.txt -q
echo "  → Core packages installed"

# ── Install pandas-ta (optional, may fail on older Python) ──────
echo ""
echo "Installing pandas-ta (technical analysis)..."
if pip install pandas-ta -q 2>/dev/null; then
    echo "  → pandas-ta installed"
else
    echo "  → pandas-ta could not be installed (Python $PY_MAJOR.$PY_MINOR)"
    echo "    This is optional. Technical indicators will use API fallbacks."
    echo ""
    echo "    To fix: upgrade to Python 3.10+ and re-run setup, or try:"
    echo "      pip install pandas-ta --no-deps"
fi

# ── Initialize API config ──────────────────────────────────────
echo ""
echo "Initializing API configuration..."
python scripts/api_config.py init
echo ""

# ── Verify ──────────────────────────────────────────────────────
echo "Verifying installation..."
python -c "
import yfinance, feedparser, pandas, requests
try:
    import pandas_ta
    ta_ok = pandas_ta.__version__
except Exception:
    ta_ok = None
print(f'  yfinance    {yfinance.__version__}')
print(f'  feedparser  {feedparser.__version__}')
print(f'  pandas      {pandas.__version__}')
print(f'  requests    {requests.__version__}')
if ta_ok:
    print(f'  pandas-ta   {ta_ok}')
else:
    print(f'  pandas-ta   not installed (optional)')
"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Setup complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Activate the venv:  source .venv/bin/activate"
echo "  Run tests:          python tests/test_skill.py"
echo "  Check API status:   python scripts/api_config.py status"
echo "  Add API keys:       nano ~/.financial-analysis/api_keys.json"
echo ""
