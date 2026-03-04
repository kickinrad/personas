"""
Sector Rotation Tracker — Tracks 11 sector ETFs vs SPY for relative strength.

Computes which sectors are leading/lagging over multiple timeframes and returns
a sector score modifier that can be applied to the composite scoring model.

Sectors tracked (SPDR Select Sector ETFs):
    XLK  Technology       XLV  Healthcare       XLC  Communications
    XLF  Financials       XLI  Industrials      XLB  Materials
    XLE  Energy           XLY  Cons. Discret.   XLRE Real Estate
    XLP  Cons. Staples    XLU  Utilities

Each sector's relative strength vs SPY is computed over 1-week, 1-month, and
3-month windows. A stock in an outperforming sector gets a tailwind boost;
a stock in an underperforming sector gets a headwind penalty.

Usage:
    from scripts.sector_rotation import get_sector_rotation, get_sector_modifier
    from scripts.sector_rotation import format_sector_rotation

    rotation = get_sector_rotation()  # full sector analysis
    modifier = get_sector_modifier("Technology")  # -0.5 to +0.5 score adjustment
"""
import os, sys
from datetime import datetime, date, timedelta

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ═══════════════════════════════════════════════════════════════════════
#  SECTOR DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════

SECTOR_ETFS = {
    "XLK":  "Technology",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLV":  "Healthcare",
    "XLI":  "Industrials",
    "XLY":  "Consumer Discretionary",
    "XLP":  "Consumer Staples",
    "XLU":  "Utilities",
    "XLRE": "Real Estate",
    "XLC":  "Communication Services",
    "XLB":  "Materials",
}

# Map common yfinance sector names to our ETF-based sectors
SECTOR_NAME_MAP = {
    "technology":              "Technology",
    "information technology":  "Technology",
    "financial services":      "Financials",
    "financials":              "Financials",
    "energy":                  "Energy",
    "healthcare":              "Healthcare",
    "health care":             "Healthcare",
    "industrials":             "Industrials",
    "consumer cyclical":       "Consumer Discretionary",
    "consumer discretionary":  "Consumer Discretionary",
    "consumer defensive":      "Consumer Staples",
    "consumer staples":        "Consumer Staples",
    "utilities":               "Utilities",
    "real estate":             "Real Estate",
    "communication services":  "Communication Services",
    "basic materials":         "Materials",
    "materials":               "Materials",
    # Non-equity categories (ETFs, funds)
    "fixed income":            "Fixed Income",
    "broad market":            "Broad Market",
    "other":                   "Other",
}

# Cache to avoid re-fetching during same session
_sector_cache = {
    "data": None,
    "timestamp": None,
}

CACHE_TTL_MINUTES = 30  # refresh sector data every 30 min


# ═══════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def get_sector_rotation(force_refresh=False):
    """
    Compute sector rotation analysis: relative performance of each sector
    ETF vs SPY over 1-week, 1-month, and 3-month windows.

    Returns:
        dict with:
        - sectors: list of {etf, name, perf_1w, perf_1m, perf_3m,
                             rel_1w, rel_1m, rel_3m, composite_rel, rank, signal}
        - spy: {perf_1w, perf_1m, perf_3m}
        - leaders: top 3 sectors
        - laggards: bottom 3 sectors
        - timestamp: when computed
    """
    # Check in-memory cache
    if not force_refresh and _sector_cache["data"] and _sector_cache["timestamp"]:
        age = (datetime.now() - _sector_cache["timestamp"]).total_seconds() / 60
        if age < CACHE_TTL_MINUTES:
            return _sector_cache["data"]

    try:
        import yfinance as yf
    except ImportError:
        return {"error": "yfinance not installed", "sectors": []}

    # Fetch all ETFs + SPY in one batch
    all_tickers = list(SECTOR_ETFS.keys()) + ["SPY"]
    period = "6mo"  # enough data for 3-month lookback

    try:
        data = yf.download(all_tickers, period=period, group_by="ticker",
                           progress=False, auto_adjust=True)
    except Exception as e:
        return {"error": f"Download failed: {e}", "sectors": []}

    if data is None or data.empty:
        return {"error": "No data returned", "sectors": []}

    # Compute returns for SPY
    spy_returns = _compute_returns(data, "SPY")
    if not spy_returns:
        return {"error": "SPY data unavailable", "sectors": []}

    # Compute returns and relative strength for each sector
    sectors = []
    for etf, name in SECTOR_ETFS.items():
        returns = _compute_returns(data, etf)
        if not returns:
            continue

        # Relative strength = sector return - SPY return
        rel_1w = returns["perf_1w"] - spy_returns["perf_1w"]
        rel_1m = returns["perf_1m"] - spy_returns["perf_1m"]
        rel_3m = returns["perf_3m"] - spy_returns["perf_3m"]

        # Composite relative strength (weighted: recent performance matters more)
        composite = rel_1w * 0.4 + rel_1m * 0.35 + rel_3m * 0.25

        sectors.append({
            "etf": etf,
            "name": name,
            "perf_1w": round(returns["perf_1w"], 2),
            "perf_1m": round(returns["perf_1m"], 2),
            "perf_3m": round(returns["perf_3m"], 2),
            "rel_1w": round(rel_1w, 2),
            "rel_1m": round(rel_1m, 2),
            "rel_3m": round(rel_3m, 2),
            "composite_rel": round(composite, 2),
        })

    # Rank by composite relative strength
    sectors.sort(key=lambda x: -x["composite_rel"])
    for i, s in enumerate(sectors):
        s["rank"] = i + 1
        # Signal based on relative strength
        if s["composite_rel"] > 2.0:
            s["signal"] = "STRONG OUTPERFORM"
        elif s["composite_rel"] > 0.5:
            s["signal"] = "OUTPERFORM"
        elif s["composite_rel"] > -0.5:
            s["signal"] = "IN LINE"
        elif s["composite_rel"] > -2.0:
            s["signal"] = "UNDERPERFORM"
        else:
            s["signal"] = "STRONG UNDERPERFORM"

    result = {
        "sectors": sectors,
        "spy": {
            "perf_1w": round(spy_returns["perf_1w"], 2),
            "perf_1m": round(spy_returns["perf_1m"], 2),
            "perf_3m": round(spy_returns["perf_3m"], 2),
        },
        "leaders": [s["name"] for s in sectors[:3]],
        "laggards": [s["name"] for s in sectors[-3:]],
        "timestamp": datetime.now().isoformat(),
    }

    # Cache it
    _sector_cache["data"] = result
    _sector_cache["timestamp"] = datetime.now()

    return result


def _compute_returns(data, ticker):
    """Compute 1-week, 1-month, 3-month returns for a ticker from the batch download."""
    try:
        if ticker in data.columns.get_level_values(0):
            close = data[ticker]["Close"].dropna()
        else:
            close = data["Close"][ticker].dropna() if "Close" in data.columns.get_level_values(0) else None

        if close is None or len(close) < 10:
            return None

        latest = close.iloc[-1]

        # 1-week (~5 trading days)
        w1_price = close.iloc[-6] if len(close) > 5 else close.iloc[0]
        perf_1w = ((latest / w1_price) - 1) * 100

        # 1-month (~21 trading days)
        m1_idx = min(22, len(close) - 1)
        m1_price = close.iloc[-m1_idx]
        perf_1m = ((latest / m1_price) - 1) * 100

        # 3-month (~63 trading days)
        m3_idx = min(64, len(close) - 1)
        m3_price = close.iloc[-m3_idx]
        perf_3m = ((latest / m3_price) - 1) * 100

        return {"perf_1w": perf_1w, "perf_1m": perf_1m, "perf_3m": perf_3m}
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════
#  SCORE MODIFIER
# ═══════════════════════════════════════════════════════════════════════

def get_sector_modifier(sector_name, rotation_data=None):
    """
    Get a score modifier for a stock based on its sector's relative strength.

    Returns a float from -0.5 to +0.5:
        +0.5  = strong sector tailwind (top 2 sector)
        +0.25 = moderate tailwind
         0.0  = sector in line with market
        -0.25 = moderate headwind
        -0.5  = strong headwind (bottom 2 sector)

    Args:
        sector_name: Sector name from yfinance (e.g., "Technology", "Energy")
        rotation_data: Pre-computed rotation data (optional, avoids re-fetch)
    """
    if not sector_name:
        return 0.0

    rotation = rotation_data or get_sector_rotation()
    if not rotation or not rotation.get("sectors"):
        return 0.0

    # Normalize sector name
    normalized = SECTOR_NAME_MAP.get(sector_name.lower(), sector_name)

    # Find this sector in the rotation data
    sector = None
    for s in rotation["sectors"]:
        if s["name"].lower() == normalized.lower():
            sector = s
            break

    if not sector:
        return 0.0

    # Map composite relative strength to a -0.5 to +0.5 modifier
    rel = sector["composite_rel"]

    if rel > 3.0:
        return 0.5
    elif rel > 1.5:
        return 0.35
    elif rel > 0.5:
        return 0.2
    elif rel > -0.5:
        return 0.0
    elif rel > -1.5:
        return -0.2
    elif rel > -3.0:
        return -0.35
    else:
        return -0.5


def get_portfolio_sector_exposure(holdings_with_sectors, rotation_data=None):
    """
    Analyze sector concentration in a portfolio.

    Args:
        holdings_with_sectors: list of {ticker, sector} dicts
        rotation_data: pre-computed rotation data

    Returns:
        dict with sector_breakdown, concentration_warnings, avg_modifier
    """
    rotation = rotation_data or get_sector_rotation()

    sector_counts = {}
    total = len(holdings_with_sectors)

    for h in holdings_with_sectors:
        sector = h.get("sector", "") or ""
        if sector:
            normalized = SECTOR_NAME_MAP.get(sector.lower(), sector)
        else:
            normalized = "Unclassified"
        sector_counts[normalized] = sector_counts.get(normalized, 0) + 1

    # Compute weights and modifiers
    breakdown = []
    for sector, count in sorted(sector_counts.items(), key=lambda x: -x[1]):
        weight = count / total if total > 0 else 0
        modifier = get_sector_modifier(sector, rotation)
        signal = "N/A"
        for s in rotation.get("sectors", []):
            if s["name"].lower() == sector.lower():
                signal = s.get("signal", "N/A")
                break
        breakdown.append({
            "sector": sector,
            "count": count,
            "weight_pct": round(weight * 100, 1),
            "modifier": modifier,
            "signal": signal,
        })

    # Warnings
    warnings = []
    for item in breakdown:
        if item["weight_pct"] > 40:
            warnings.append(
                f"Heavy concentration in {item['sector']} ({item['weight_pct']}% of portfolio)"
                f" — currently {item['signal']}"
            )
        if item["weight_pct"] > 25 and item["modifier"] < -0.2:
            warnings.append(
                f"{item['sector']} ({item['weight_pct']}% of portfolio) is underperforming the market"
            )

    # Average modifier across portfolio
    modifiers = [get_sector_modifier(h.get("sector", ""), rotation) for h in holdings_with_sectors]
    avg_mod = sum(modifiers) / len(modifiers) if modifiers else 0

    return {
        "sector_breakdown": breakdown,
        "concentration_warnings": warnings,
        "avg_sector_modifier": round(avg_mod, 3),
    }


# ═══════════════════════════════════════════════════════════════════════
#  FORMATTER
# ═══════════════════════════════════════════════════════════════════════

def format_sector_rotation(rotation):
    """Format sector rotation data for console output."""
    lines = []
    _h = lines.append

    _h(f"  {'─' * 60}")
    _h(f"  SECTOR ROTATION")
    _h(f"  {'─' * 60}")

    spy = rotation.get("spy", {})
    _h(f"  S&P 500 (SPY):  1W {spy.get('perf_1w', 0):+.1f}%  |  "
       f"1M {spy.get('perf_1m', 0):+.1f}%  |  3M {spy.get('perf_3m', 0):+.1f}%")
    _h("")

    _h(f"  {'Rank':<5} {'Sector':<28} {'1W':>6} {'1M':>6} {'3M':>6} {'vs SPY':>7}  {'Signal'}")
    _h(f"  {'─' * 75}")

    for s in rotation.get("sectors", []):
        signal = s.get("signal", "N/A")
        arrow = ""
        if "STRONG OUTPERFORM" in signal:
            arrow = "▲▲"
        elif "OUTPERFORM" in signal:
            arrow = "▲"
        elif "STRONG UNDERPERFORM" in signal:
            arrow = "▼▼"
        elif "UNDERPERFORM" in signal:
            arrow = "▼"
        else:
            arrow = "━"

        _h(f"  {s['rank']:<5} {s['name']:<28} "
           f"{s['perf_1w']:>+5.1f}% {s['perf_1m']:>+5.1f}% {s['perf_3m']:>+5.1f}% "
           f"{s['composite_rel']:>+6.1f}%  {arrow} {signal}")

    _h("")
    leaders = rotation.get("leaders", [])
    laggards = rotation.get("laggards", [])
    if leaders:
        _h(f"  Leaders:  {', '.join(leaders)}")
    if laggards:
        _h(f"  Laggards: {', '.join(laggards)}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("Fetching sector rotation data...\n")
    rotation = get_sector_rotation(force_refresh=True)

    if rotation.get("error"):
        print(f"Error: {rotation['error']}")
        return

    print(format_sector_rotation(rotation))


if __name__ == "__main__":
    main()
