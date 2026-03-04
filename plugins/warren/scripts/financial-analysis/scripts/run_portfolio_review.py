#!/usr/bin/env python3
"""
Weekly Portfolio Review — Use Case #1.

Accepts a list of current holdings (from CSV, text file, or command line)
and runs a full analysis on each position to produce:
  - Buy More / Hold / Trim / Sell recommendations (P&L-aware)
  - Updated entry levels (for adding) and exit targets
  - Composite score comparison across the portfolio
  - Macro context: upcoming earnings, economic events, sector rotation
  - Risk concentration warnings

Input formats supported:
  - CSV file with columns: ticker, shares, avg_cost (cost basis required)
  - Command-line arguments: AAPL:100:150.50 MSFT:50:380.00

Usage:
    python scripts/run_portfolio_review.py AAPL:100:150.50 MSFT:50:380
    python scripts/run_portfolio_review.py --file portfolio.csv
    python scripts/run_portfolio_review.py --file portfolio.csv --output review.json
"""
import os, sys, json, csv, argparse, time
from datetime import datetime

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.api_config import load_config
from scripts.scoring import score_to_portfolio_action
from scripts.run_deep_dive import deep_dive, print_report
from scripts.usage_tracker import get_tracker
from scripts.macro_calendar import get_macro_summary, format_macro_summary
from scripts.sector_rotation import (
    get_sector_rotation, get_portfolio_sector_exposure,
    format_sector_rotation, SECTOR_NAME_MAP,
)


def load_holdings_from_file(filepath):
    """
    Load portfolio holdings from CSV or text file.

    Supported formats:
    - CSV with header: ticker,shares,avg_cost
    - CSV without header: ticker,shares,avg_cost
    """
    holdings = []
    ext = os.path.splitext(filepath)[1].lower()

    with open(filepath) as f:
        content = f.read().strip()

    if ext == ".csv" or "," in content.split("\n")[0]:
        # CSV format
        reader = csv.DictReader(content.splitlines())
        fieldnames = reader.fieldnames or []

        # Check if it has a header
        has_header = any(fn.lower() in ("ticker", "symbol", "stock") for fn in fieldnames)
        if not has_header:
            # No header — treat columns as ticker,shares,avg_cost
            for line in content.strip().splitlines():
                parts = line.split(",")
                ticker = parts[0].strip().upper()
                if not ticker or not ticker.isalpha():
                    continue
                shares = float(parts[1]) if len(parts) > 1 and parts[1].strip() else None
                avg_cost = float(parts[2]) if len(parts) > 2 and parts[2].strip() else None
                if shares is None or avg_cost is None:
                    print(f"  WARNING: {ticker} missing shares or avg_cost — skipping")
                    print(f"           CSV format: ticker,shares,avg_cost")
                    continue
                holdings.append({
                    "ticker": ticker,
                    "shares": shares,
                    "avg_cost": avg_cost,
                })
        else:
            for row in reader:
                ticker_key = next((k for k in row if k.lower() in ("ticker", "symbol", "stock")), None)
                if not ticker_key:
                    continue
                ticker = row[ticker_key].strip().upper()
                shares_key = next((k for k in row if k.lower() in ("shares", "quantity", "qty")), None)
                cost_key = next((k for k in row if k.lower() in ("avg_cost", "cost", "price", "avg_price")), None)

                shares = float(row[shares_key]) if shares_key and row.get(shares_key, "").strip() else None
                avg_cost = float(row[cost_key]) if cost_key and row.get(cost_key, "").strip() else None

                if shares is None or avg_cost is None:
                    print(f"  WARNING: {ticker} missing shares or avg_cost — skipping")
                    print(f"           CSV must have: ticker, shares, avg_cost columns")
                    continue

                holdings.append({
                    "ticker": ticker,
                    "shares": shares,
                    "avg_cost": avg_cost,
                })
    else:
        print("ERROR: Portfolio review requires a CSV file with ticker,shares,avg_cost")
        print("       Example CSV:")
        print("         ticker,shares,avg_cost")
        print("         AAPL,100,150.50")
        print("         MSFT,50,380.00")
        return []

    return holdings


def _pnl_adjusted_action(base_action, pnl_pct, score):
    """
    Adjust the action recommendation based on P&L position.

    Logic:
    - Big gain (>100%): Consider taking partial profits regardless of score
    - Good gain (>50%): Suggest trimming if score is weakening
    - Moderate gain (>20%): Hold winners, let them run if score is good
    - Small gain/flat: Standard action based on score
    - Small loss (<-10%): Hold if score supports rebound
    - Moderate loss (-10% to -25%): Flag for review, don't sell at a loss if score is decent
    - Big loss (>-25%): Warn but check if fundamentals support holding for recovery
    """
    if pnl_pct is None:
        return base_action

    # Big winners (100%+) — protect profits
    if pnl_pct >= 100:
        if score >= 7.0:
            return "HOLD (take 25% profit)"
        elif score >= 5.5:
            return "TRIM (take 50% profit)"
        else:
            return "TRIM (take 50-75% profit)"

    # Good winners (50-100%)
    if pnl_pct >= 50:
        if score >= 7.0:
            return "HOLD (strong — let it run)"
        elif score >= 5.5:
            return "HOLD (consider trailing stop)"
        else:
            return "TRIM (take partial profit)"

    # Moderate winners (20-50%)
    if pnl_pct >= 20:
        if score >= 6.5:
            return base_action  # let the score drive it
        elif score < 4.5:
            return "TRIM (lock in gains, score weakening)"
        return base_action

    # Small gain or flat (-5% to 20%)
    if pnl_pct >= -5:
        return base_action  # pure score-based decision

    # Moderate loss (-5% to -15%)
    if pnl_pct >= -15:
        if score >= 6.0:
            return "HOLD (score supports recovery)"
        elif score >= 4.5:
            return "HOLD (monitor closely)"
        else:
            return "REVIEW (cut loss or wait?)"

    # Significant loss (-15% to -30%)
    if pnl_pct >= -30:
        if score >= 6.5:
            return "HOLD (buy the dip?)"
        elif score >= 5.0:
            return "HOLD (wait for rebound)"
        else:
            return "SELL (cut loss)"

    # Deep loss (>-30%)
    if score >= 7.0:
        return "BUY MORE (avg down — strong fundamentals)"
    elif score >= 5.5:
        return "HOLD (recovery possible)"
    else:
        return "SELL (cut loss, redeploy capital)"


def _enrich_action_with_levels(action, entry_exit, current_price):
    """
    Append concrete price levels to action recommendations that mention
    trailing stops, trims, partial profits, buying more, or averaging down.

    Uses the entry_exit data (stop_loss, entries, targets) to add
    specific dollar amounts, e.g.:
        "HOLD (consider trailing stop)"  →
        "HOLD (trailing stop at $58.20, below 50-SMA support)"
    """
    if not entry_exit or not current_price:
        return action

    ee = entry_exit
    stop = ee.get("stop_loss")

    # Parse entries (dict or float)
    entries_raw = ee.get("entries", {})
    if isinstance(entries_raw, dict):
        entry_aggressive = entries_raw.get("aggressive")
        entry_moderate = entries_raw.get("moderate")
        entry_conservative = entries_raw.get("conservative")
    else:
        entry_aggressive = entry_moderate = entry_conservative = None

    # Parse targets (dict or float)
    targets_raw = ee.get("targets", {})
    if isinstance(targets_raw, dict):
        target_1 = targets_raw.get("target_1")
        target_2 = targets_raw.get("target_2")
    else:
        target_1 = target_2 = None

    action_lower = action.lower()

    # Trailing stop → use stop_loss level
    if "trailing stop" in action_lower and stop:
        pct_below = ((current_price - stop) / current_price) * 100
        return f"HOLD (set trailing stop at ${stop:.2f}, {pct_below:.0f}% below current)"

    # Take partial profit / take 25-75% profit → show target sell levels
    if ("profit" in action_lower or "trim" in action_lower) and target_1:
        if stop:
            return f"{action} — sell near ${target_1:.2f}, stop ${stop:.2f}"
        return f"{action} — sell near ${target_1:.2f}"

    # Buy more / avg down → show entry levels
    if ("buy more" in action_lower or "avg down" in action_lower) and entry_moderate:
        return f"{action} — add near ${entry_moderate:.2f}"

    # Buy the dip → show aggressive entry
    if "dip" in action_lower and entry_aggressive:
        return f"{action} — entry near ${entry_aggressive:.2f}, stop ${stop:.2f}" if stop else action

    # Cut loss → use stop as confirmation
    if "cut loss" in action_lower and stop:
        return f"{action} — exit below ${stop:.2f}"

    return action


def run_portfolio_review(holdings, config=None, verbose=True, use_cache=True):
    """
    Run a full portfolio review on all holdings.

    Args:
        holdings: List of {"ticker": str, "shares": float, "avg_cost": float}
        config: API config (auto-loaded if None)
        use_cache: Use same-day cached data when available (default True)

    Returns:
        dict with per-stock analysis, macro context, and portfolio-level summary
    """
    config = config or load_config()
    start_time = time.time()
    results = []
    tickers = [h["ticker"] for h in holdings]

    print(f"\n{'═' * 70}")
    print(f"  WEEKLY PORTFOLIO REVIEW")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Holdings: {len(holdings)} positions")
    print(f"{'═' * 70}")

    # ─── Macro Context (fetch once for all holdings) ──────────────
    print(f"\n  Fetching macro context...")
    macro = get_macro_summary(tickers=tickers, days_ahead=14)
    print(format_macro_summary(macro))

    print(f"\n  Fetching sector rotation data...")
    rotation = get_sector_rotation()
    if rotation.get("sectors"):
        print(format_sector_rotation(rotation))
    else:
        print(f"  Sector rotation: unavailable ({rotation.get('error', 'unknown')})")
    print()

    # Build earnings lookup for quick reference
    earnings_map = {}
    for e in macro.get("earnings_calendar", []):
        earnings_map[e["ticker"]] = e

    # ─── Per-Stock Analysis ───────────────────────────────────────
    for i, holding in enumerate(holdings):
        ticker = holding["ticker"]
        shares = holding["shares"]
        avg_cost = holding["avg_cost"]

        print(f"\n  [{i+1}/{len(holdings)}] Analyzing {ticker} "
              f"({shares} shares @ ${avg_cost:.2f})...")

        # Run full deep dive
        dd_result = deep_dive(ticker, config, verbose=verbose, use_cache=use_cache)

        if "error" in dd_result:
            results.append({
                "ticker": ticker,
                "shares": shares,
                "avg_cost": avg_cost,
                "error": dd_result["error"],
                "action": "REVIEW MANUALLY",
            })
            continue

        # Compute P&L — guard against $0 price (API failure / rate limit)
        current_price = dd_result.get("current_price", 0) or 0
        if current_price <= 0:
            print(f"  ⚠ WARNING: No valid price for {ticker} — P&L will be skipped")
            results.append({
                "ticker": ticker, "shares": shares, "avg_cost": avg_cost,
                "current_price": 0, "position_value": 0,
                "cost_basis_total": round(avg_cost * shares, 2),
                "pnl_per_share": None, "pnl_pct": None, "total_pnl": None,
                "composite_score": dd_result.get("composite_score", 5.0),
                "rating": dd_result.get("rating", "N/A"),
                "action": "REVIEW (no price data)",
                "base_action": "REVIEW",
                "confidence": dd_result.get("confidence"),
                "sector": (dd_result.get("fundamentals_summary") or {}).get("sector", ""),
                "sector_modifier": dd_result.get("sector_modifier", 0),
                "earnings_note": None,
                "entry_exit": dd_result.get("entry_exit"),
                "sub_scores": dd_result.get("sub_scores"),
                "tradingview": dd_result.get("tradingview"),
                "price_error": True,
            })
            continue

        pnl_per_share = current_price - avg_cost
        pnl_pct = (pnl_per_share / avg_cost) * 100 if avg_cost > 0 else 0
        total_pnl = pnl_per_share * shares
        position_value = current_price * shares
        cost_basis_total = avg_cost * shares

        # Get score-based action, then adjust for P&L, then enrich with price levels
        score = dd_result.get("composite_score", 5.0)
        base_action = score_to_portfolio_action(score, current_holding=True)
        action = _pnl_adjusted_action(base_action, pnl_pct, score)
        action = _enrich_action_with_levels(action, dd_result.get("entry_exit"), current_price)

        # Check if earnings are imminent — override action with warning
        earn_info = earnings_map.get(ticker)
        earnings_note = None
        if earn_info and earn_info.get("is_imminent"):
            earnings_note = f"Earnings in {earn_info['days_until']}d ({earn_info['earnings_date']}) — hold through or trim before?"

        # Get sector info for the summary
        sector = ""
        fs = dd_result.get("fundamentals_summary")
        if fs:
            sector = fs.get("sector", "")

        position_result = {
            "ticker": ticker,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_price": current_price,
            "position_value": round(position_value, 2),
            "cost_basis_total": round(cost_basis_total, 2),
            "pnl_per_share": round(pnl_per_share, 2),
            "pnl_pct": round(pnl_pct, 2),
            "total_pnl": round(total_pnl, 2),
            "composite_score": score,
            "rating": dd_result.get("rating"),
            "action": action,
            "base_action": base_action,
            "confidence": dd_result.get("confidence"),
            "sector": sector,
            "sector_modifier": dd_result.get("sector_modifier", 0),
            "earnings_note": earnings_note,
            "entry_exit": dd_result.get("entry_exit"),
            "sub_scores": dd_result.get("sub_scores"),
            "tradingview": dd_result.get("tradingview"),
            # Expanded detail fields (from enhanced deep_dive)
            "all_analyst_results": dd_result.get("all_analyst_results"),
            "data_sources": dd_result.get("data_sources"),
            "fundamentals_summary": dd_result.get("fundamentals_summary"),
            "fundamentals_detail": dd_result.get("fundamentals_detail"),
            "earnings_detail": dd_result.get("earnings_detail"),
            "insider_detail": dd_result.get("insider_detail"),
            "reddit_detail": dd_result.get("reddit_detail"),
            "stocktwits_detail": dd_result.get("stocktwits_detail"),
            "news_detail": dd_result.get("news_detail"),
            "key_articles": dd_result.get("key_articles"),
            "api_status": dd_result.get("api_status"),
            "from_cache": dd_result.get("from_cache", False),
        }
        results.append(position_result)

    elapsed = round(time.time() - start_time, 1)

    # ─── Portfolio Summary ──────────────────────────────────────
    summary = _compute_portfolio_summary(results, holdings, rotation)

    review = {
        "review_date": datetime.now().isoformat(),
        "holdings_count": len(holdings),
        "elapsed_seconds": elapsed,
        "macro": macro,
        "sector_rotation": rotation,
        "positions": results,
        "summary": summary,
    }

    _print_portfolio_summary(review)

    # ─── Auto-save markdown report ────────────────────────────────
    try:
        md_path = _save_markdown_report(review)
        print(f"\n  📄 Full report saved to: {md_path}")
    except Exception as e:
        print(f"\n  ⚠ Failed to save markdown report: {e}")

    return review


def _compute_portfolio_summary(results, holdings, rotation=None):
    """Compute portfolio-level statistics and warnings."""
    valid = [r for r in results if r.get("composite_score")]
    scores = [r["composite_score"] for r in valid]

    avg_score = sum(scores) / len(scores) if scores else 0

    # P&L summary — only include positions with valid price data
    priced = [r for r in valid if not r.get("price_error")]
    no_price = [r for r in valid if r.get("price_error")]

    total_value = sum(r.get("position_value", 0) for r in priced)
    total_cost = sum(r.get("cost_basis_total", 0) for r in priced)
    total_pnl = sum(r.get("total_pnl", 0) for r in priced)
    total_pnl_pct = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0

    # Sector exposure analysis
    sector_exposure = None
    if rotation and rotation.get("sectors"):
        holdings_with_sectors = [{"ticker": r["ticker"], "sector": r.get("sector", "")} for r in valid]
        sector_exposure = get_portfolio_sector_exposure(holdings_with_sectors, rotation)

    # Warnings
    warnings = _generate_warnings(results, sector_exposure)

    return {
        "portfolio_avg_score": round(avg_score, 2),
        "portfolio_rating": _portfolio_health(avg_score),
        "total_value": round(total_value, 2),
        "total_cost_basis": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "strongest": max(valid, key=lambda r: r.get("composite_score", 0)).get("ticker") if valid else None,
        "weakest": min(valid, key=lambda r: r.get("composite_score", 10)).get("ticker") if valid else None,
        "biggest_winner": max(priced, key=lambda r: r.get("pnl_pct") or 0).get("ticker") if priced else None,
        "biggest_loser": min(priced, key=lambda r: r.get("pnl_pct") or 0).get("ticker") if priced else None,
        "sector_exposure": sector_exposure,
        "warnings": warnings,
    }


def _portfolio_health(avg_score):
    """Map average portfolio score to health label."""
    if avg_score >= 7.0:
        return "STRONG"
    elif avg_score >= 5.5:
        return "HEALTHY"
    elif avg_score >= 4.0:
        return "MIXED"
    return "WEAK"


def _generate_warnings(results, sector_exposure=None):
    """Generate portfolio-level risk warnings."""
    warnings = []

    # Price error warnings
    no_price = [r["ticker"] for r in results if r.get("price_error")]
    if no_price:
        warnings.append(f"No price data for: {', '.join(no_price)} — P&L excluded from totals")

    # P&L-based warnings (skip price-error positions)
    priced = [r for r in results if not r.get("price_error")]
    big_losers = [r for r in priced if r.get("pnl_pct") is not None and r["pnl_pct"] < -20]
    if big_losers:
        for r in big_losers:
            warnings.append(
                f"{r['ticker']}: down {abs(r['pnl_pct']):.1f}% "
                f"(${abs(r['total_pnl']):,.0f} loss) — score: {r.get('composite_score', 'N/A')}/10"
            )

    big_winners = [r for r in priced if r.get("pnl_pct") is not None and r["pnl_pct"] > 80]
    if big_winners:
        for r in big_winners:
            warnings.append(
                f"{r['ticker']}: up {r['pnl_pct']:.1f}% "
                f"(${r['total_pnl']:,.0f} gain) — consider taking partial profits"
            )

    # Earnings warnings
    imminent = [r for r in results if r.get("earnings_note")]
    for r in imminent:
        warnings.append(f"{r['ticker']}: {r['earnings_note']}")

    # Low-confidence scores
    low_conf = [r["ticker"] for r in results if r.get("confidence") == "LOW"]
    if low_conf:
        warnings.append(f"Low confidence data for: {', '.join(low_conf)} — limited API data")

    # Sector concentration
    if sector_exposure:
        warnings.extend(sector_exposure.get("concentration_warnings", []))

    return warnings


def _format_position_detail(p):
    """
    Build a detailed report for a single position as a list of markdown lines.
    Used by both console output and markdown report for identical formatting.
    """
    lines = []
    ticker = p["ticker"]
    name = ""
    fs = p.get("fundamentals_summary") or p.get("fundamentals_detail") or {}
    if fs:
        name = fs.get("name", "")

    header = f"### {ticker}"
    if name:
        header += f" — {name}"
    lines.append(header)
    lines.append("")

    # ── Price & P&L line ──
    if p.get("price_error"):
        lines.append(f"Price: ⚠️ No valid price data | Shares: {p['shares']} @ ${p['avg_cost']:.2f}")
    else:
        pnl_str = ""
        if p.get("pnl_pct") is not None:
            icon = "📈" if p["pnl_pct"] >= 0 else "📉"
            pnl_str = f" | P&L: {icon} ${p['total_pnl']:+,.2f} ({p['pnl_pct']:+.1f}%)"
        lines.append(f"Price: ${p.get('current_price', 0):.2f} | "
                      f"Shares: {p['shares']} @ ${p['avg_cost']:.2f}{pnl_str}")

    # ── Score line ──
    cache_note = " (from cache)" if p.get("from_cache") else ""
    lines.append(f"Score: {p.get('composite_score', 'N/A')}/10 ({p.get('rating', 'N/A')}) | "
                  f"Confidence: {p.get('confidence', 'N/A')} | "
                  f"Action: **{p.get('action', 'N/A')}**{cache_note}")
    lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  FUNDAMENTAL SCORE with factor breakdown
    # ═══════════════════════════════════════════════════════════
    sub = p.get("sub_scores") or {}
    fund_sub = sub.get("fundamental", {})
    if fund_sub:
        fund_score = fund_sub.get("score", "N/A")
        fund_weight = fund_sub.get("weight", 0.4)
        fund_conf = fund_sub.get("confidence", "N/A")
        lines.append(f"#### Fundamental Score: {fund_score}/10 (weight: {fund_weight*100:.0f}%) [{fund_conf}]")
        lines.append("")
        factors = fund_sub.get("factors", {})
        if factors:
            lines.append("| Factor | Value | Score | Rating |")
            lines.append("|--------|-------|-------|--------|")
            factor_names = {
                "pe_ratio": "PE Ratio",
                "pb_ratio": "PB Ratio",
                "revenue_growth": "Revenue Growth",
                "eps_growth": "EPS Growth",
                "profit_margin": "Profit Margin",
                "debt_to_equity": "Debt/Equity",
                "free_cash_flow": "Free Cash Flow",
                "roe": "Return on Equity",
                "analyst_consensus": "Analyst Consensus",
                "earnings_surprises": "Earnings Surprises",
            }
            for key in ["pe_ratio", "pb_ratio", "revenue_growth", "eps_growth",
                        "profit_margin", "debt_to_equity", "free_cash_flow", "roe",
                        "analyst_consensus", "earnings_surprises"]:
                f_data = factors.get(key, {})
                display_name = factor_names.get(key, key)
                value = f_data.get("value", "N/A")
                # Format analyst consensus differently
                if key == "analyst_consensus" and f_data.get("buy") is not None:
                    buy_pct = f_data.get("buy_pct", 0)
                    value = f"{f_data['buy']}B/{f_data.get('hold',0)}H/{f_data.get('sell',0)}S ({buy_pct:.0f}% buy)"
                elif key == "analyst_consensus" and f_data.get("recommendation"):
                    value = f_data["recommendation"]
                elif key == "earnings_surprises" and f_data.get("beat_count") is not None:
                    value = f"{f_data['beat_count']} beats / {f_data['miss_count']} misses (avg {f_data.get('surprise_avg_pct', 0):+.1f}%)"
                elif isinstance(value, float):
                    if key in ("revenue_growth", "eps_growth", "profit_margin", "roe"):
                        value = f"{value:.1f}%"
                    else:
                        value = f"{value}"
                elif value is None:
                    value = "—"
                score = f_data.get("score", "—")
                rating = f_data.get("rating_note", f_data.get("note", ""))
                lines.append(f"| {display_name} | {value} | {score}/10 | {rating} |")
            lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  TECHNICAL SCORE
    # ═══════════════════════════════════════════════════════════
    tech_sub = sub.get("technical", {})
    if tech_sub:
        tech_score = tech_sub.get("score", "N/A")
        tech_weight = tech_sub.get("weight", 0.3)
        tech_conf = tech_sub.get("confidence", "N/A")
        lines.append(f"#### Technical Score: {tech_score}/10 (weight: {tech_weight*100:.0f}%) [{tech_conf}]")
        lines.append("")
        tf = tech_sub.get("factors", {})
        if tf:
            rsi = tf.get("rsi")
            rsi_str = f"{rsi:.1f}" if rsi is not None else "N/A"
            macd_str = "Bullish" if tf.get("macd_bullish") else ("Bearish" if tf.get("macd_bullish") is False else "N/A")
            sma50_str = "Yes" if tf.get("above_sma50") else ("No" if tf.get("above_sma50") is False else "N/A")
            sma200_str = "Yes" if tf.get("above_sma200") else ("No" if tf.get("above_sma200") is False else "N/A")
            bb = tf.get("bb_position")
            bb_str = f"{bb:.2f}" if bb is not None else "N/A"
            vol = tf.get("volume_ratio")
            vol_str = f"{vol:.2f}x" if vol is not None else "N/A"
            adx = tf.get("adx")
            adx_str = f"{adx:.1f}" if adx is not None else "N/A"
            lines.append(f"RSI: {rsi_str} | MACD: {macd_str} | Above SMA50: {sma50_str} | "
                          f"Above SMA200: {sma200_str} | BB Position: {bb_str} | "
                          f"Volume Ratio: {vol_str} | ADX: {adx_str}")
            lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  SENTIMENT SCORE with factor breakdown
    # ═══════════════════════════════════════════════════════════
    sent_sub = sub.get("sentiment", {})
    if sent_sub:
        sent_score = sent_sub.get("score", "N/A")
        sent_weight = sent_sub.get("weight", 0.3)
        sent_conf = sent_sub.get("confidence", "N/A")
        lines.append(f"#### Sentiment Score: {sent_score}/10 (weight: {sent_weight*100:.0f}%) [{sent_conf}]")
        lines.append("")
        factors = sent_sub.get("factors", {})
        if factors:
            lines.append("| Factor | Value | Score | Source | Rating |")
            lines.append("|--------|-------|-------|--------|--------|")
            sent_factor_names = {
                "reddit_sentiment": "Reddit",
                "stocktwits_sentiment": "StockTwits",
                "news_sentiment": "News Sentiment",
                "tradingview_consensus": "TradingView",
                "rss_buzz": "RSS Buzz",
                "insider_activity": "Insider Activity",
                "congress_trades": "Congress Trades",
            }
            for key in ["reddit_sentiment", "stocktwits_sentiment", "news_sentiment",
                        "tradingview_consensus", "rss_buzz", "insider_activity", "congress_trades"]:
                f_data = factors.get(key, {})
                display_name = sent_factor_names.get(key, key)
                # Build value string based on factor type
                if key == "reddit_sentiment":
                    mentions = f_data.get("mentions", 0)
                    trend = f_data.get("trend", 0)
                    rank = f_data.get("rank")
                    rank_str = f" (#{rank})" if rank else ""
                    value = f"{mentions} mentions{rank_str}, trend: {trend:.2f}x" if mentions else "—"
                elif key == "stocktwits_sentiment":
                    bull = f_data.get("bull_pct", 0)
                    msgs = f_data.get("messages", 0)
                    value = f"{bull:.0f}% bull ({msgs} msgs)" if msgs else "—"
                elif key == "news_sentiment":
                    avg_s = f_data.get("avg_sentiment")
                    arts = f_data.get("articles", 0)
                    value = f"{avg_s:+.3f} ({arts} articles)" if avg_s is not None else f"{arts} articles"
                elif key == "tradingview_consensus":
                    rec = f_data.get("recommendation", "")
                    bc = f_data.get("buy_count", 0)
                    nc = f_data.get("neutral_count", 0)
                    sc = f_data.get("sell_count", 0)
                    value = f"{rec} ({bc}B/{nc}N/{sc}S)" if rec else "—"
                elif key == "rss_buzz":
                    mc = f_data.get("mention_count", 0)
                    value = f"{mc} mentions" if mc else "—"
                elif key == "insider_activity":
                    buys = f_data.get("buys", 0)
                    sells = f_data.get("sells", 0)
                    signal = f_data.get("signal", "")
                    value = f"{buys} buys / {sells} sells" if buys + sells > 0 else "—"
                    if signal:
                        value += f" ({signal})"
                elif key == "congress_trades":
                    buys = f_data.get("buys", 0)
                    sells = f_data.get("sells", 0)
                    value = f"{buys} buys / {sells} sells" if buys + sells > 0 else "—"
                else:
                    value = str(f_data.get("value", "—"))
                score = f_data.get("score", "—")
                source = f_data.get("source", "—")
                rating = f_data.get("rating_note", f_data.get("note", ""))
                lines.append(f"| {display_name} | {value} | {score}/10 | {source} | {rating} |")
            lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  ANALYST RATINGS (all sources)
    # ═══════════════════════════════════════════════════════════
    all_analyst = p.get("all_analyst_results")
    if all_analyst:
        lines.append("#### Analyst Ratings (all sources)")
        lines.append("")
        lines.append("| Source | Data | Status |")
        lines.append("|--------|------|--------|")
        source_labels = {
            "finnhub": "Finnhub",
            "yfinance": "yfinance",
            "seeking_alpha_rapidapi": "Seeking Alpha",
        }
        from scripts.run_deep_dive import _format_analyst_line
        for src_id in ["finnhub", "yfinance", "seeking_alpha_rapidapi"]:
            src_data = all_analyst.get(src_id, {})
            label = source_labels.get(src_id, src_id)
            if src_data.get("success"):
                d = src_data.get("data", {})
                data_str = _format_analyst_line(src_id, d)
                lines.append(f"| {label} | {data_str} | ✓ |")
            else:
                error = src_data.get("error", "unavailable")
                if "not configured" in error.lower() or "paid" in error.lower():
                    lines.append(f"| {label} | — | Paid key required ($) |")
                else:
                    err_short = error[:60] if len(error) > 60 else error
                    lines.append(f"| {label} | — | ✗ {err_short} |")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  EARNINGS
    # ═══════════════════════════════════════════════════════════
    ear = p.get("earnings_detail")
    if ear:
        ear_source = (p.get("data_sources") or {}).get("earnings", "Finnhub")
        lines.append(f"#### Earnings (source: {ear_source})")
        lines.append("")
        quarters = ear.get("quarters", ear.get("earnings", []))
        if isinstance(quarters, list) and quarters:
            lines.append("| Quarter | Actual | Estimate | Surprise |")
            lines.append("|---------|--------|----------|----------|")
            for q in quarters[:6]:
                period = q.get("period", q.get("quarter", ""))
                actual = q.get("actual", q.get("actual_eps", "N/A"))
                estimate = q.get("estimate", q.get("estimated_eps", "N/A"))
                surprise_pct = q.get("surprise_pct", q.get("surprise_percent"))
                if actual is not None and actual != "N/A":
                    actual_str = f"${float(actual):.2f}"
                else:
                    actual_str = "N/A"
                if estimate is not None and estimate != "N/A":
                    est_str = f"${float(estimate):.2f}"
                else:
                    est_str = "N/A"
                if surprise_pct is not None:
                    surp_str = f"{float(surprise_pct):+.1f}%"
                else:
                    surp_str = "—"
                lines.append(f"| {period} | {actual_str} | {est_str} | {surp_str} |")
        else:
            # Summary format
            beat_count = ear.get("beat_count", 0)
            miss_count = ear.get("miss_count", 0)
            surprise_avg = ear.get("surprise_avg", 0)
            lines.append(f"Beats: {beat_count} | Misses: {miss_count} | Avg Surprise: {surprise_avg:+.1f}%")
        lines.append("")

    # Earnings note (imminent earnings)
    if p.get("earnings_note"):
        lines.append(f"⚠️ **{p['earnings_note']}**")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  INSIDER TRADES
    # ═══════════════════════════════════════════════════════════
    ins = p.get("insider_detail")
    if ins:
        ins_source = (p.get("data_sources") or {}).get("insider_trades", "Finnhub")
        buys = ins.get("buys_last_50", 0)
        sells = ins.get("sells_last_50", 0)
        signal = ins.get("net_insider_signal", "neutral")
        lines.append(f"#### Insider Trades (source: {ins_source})")
        lines.append("")
        lines.append(f"Buys: {buys} | Sells: {sells} | Signal: {signal}")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  SECTOR
    # ═══════════════════════════════════════════════════════════
    if p.get("sector"):
        mod = p.get("sector_modifier", 0)
        mod_str = f" ({mod:+.2f} modifier)" if abs(mod) > 0.01 else ""
        lines.append(f"**Sector**: {p['sector']}{mod_str}")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  ENTRY / EXIT LEVELS
    # ═══════════════════════════════════════════════════════════
    ee = p.get("entry_exit")
    if ee:
        lines.append("#### Entry/Exit Levels")
        lines.append("")
        entries = ee.get("entries", {})
        exits = ee.get("exits", ee.get("targets", {}))
        stop = ee.get("stop_loss")

        lines.append("| Level | Price | Method |")
        lines.append("|-------|-------|--------|")

        # entries may be a dict {aggressive/moderate/conservative: price}
        # or a list [{price, method}, ...]
        if isinstance(entries, dict):
            entry_labels = {"aggressive": "Aggressive", "moderate": "Moderate", "conservative": "Conservative"}
            for key in ["aggressive", "moderate", "conservative"]:
                price = entries.get(key)
                if price is not None:
                    lines.append(f"| Entry ({entry_labels.get(key, key)}) | ${float(price):.2f} | {key.title()} zone |")
        elif isinstance(entries, list):
            for i, e in enumerate(entries[:3]):
                price = e.get("price", e.get("level", 0))
                method = e.get("method", e.get("label", ""))
                lines.append(f"| Entry {i+1} | ${float(price):.2f} | {method} |")

        # exits/targets may be a dict {target_1/target_2/target_3: price}
        # or a list [{price, method}, ...]
        if isinstance(exits, dict):
            target_labels = {"target_1": "Short-term", "target_2": "Medium-term", "target_3": "Stretch goal"}
            for key in ["target_1", "target_2", "target_3"]:
                price = exits.get(key)
                if price is not None:
                    lines.append(f"| Target ({target_labels.get(key, key)}) | ${float(price):.2f} | {target_labels.get(key, key)} |")
        elif isinstance(exits, list):
            for i, e in enumerate(exits[:3]):
                price = e.get("price", e.get("level", 0))
                method = e.get("method", e.get("label", ""))
                lines.append(f"| Target {i+1} | ${float(price):.2f} | {method} |")

        if stop is not None:
            stop_price = stop.get("price", stop) if isinstance(stop, dict) else stop
            lines.append(f"| Stop Loss | ${float(stop_price):.2f} | Risk management |")
        rr = ee.get("risk_reward")
        if rr:
            lines.append(f"")
            if isinstance(rr, dict):
                # rr is {combo_name: {rr_ratio, favorable, ...}} — show best favorable combo
                best = sorted(rr.values(), key=lambda x: -x.get("rr_ratio", 0) if isinstance(x, dict) else 0)
                fav = [v for v in best if isinstance(v, dict) and v.get("favorable")]
                if fav:
                    b = fav[0]
                    lines.append(f"Best R:R: {b['rr_ratio']:.1f}x (entry ${b.get('entry', 0):.2f} → target ${b.get('target', 0):.2f})")
                elif best and isinstance(best[0], dict):
                    b = best[0]
                    lines.append(f"Best R:R: {b.get('rr_ratio', 0):.1f}x")
            else:
                lines.append(f"Risk/Reward: {float(rr):.2f}x")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  KEY ARTICLES
    # ═══════════════════════════════════════════════════════════
    articles = p.get("key_articles", [])
    if articles:
        lines.append(f"#### Key Articles ({len(articles)})")
        lines.append("")
        for i, a in enumerate(articles[:10]):
            flag = a.get("sentiment_flag", "🟡")
            source = a.get("source", "?")
            title = a.get("title", "Untitled")
            if len(title) > 80:
                title = title[:77] + "..."
            sent = a.get("sentiment")
            sent_str = ""
            if sent is not None:
                sent_str = f" ({sent:+.2f})"
            link = a.get("link", "")
            link_str = f" — {link}" if link else ""
            lines.append(f"{i+1}. {flag} [{source}] {title}{sent_str}{link_str}")
        lines.append("")

    # ═══════════════════════════════════════════════════════════
    #  DATA SOURCES
    # ═══════════════════════════════════════════════════════════
    ds = p.get("data_sources")
    api_stat = p.get("api_status")
    if ds or api_stat:
        lines.append("#### Data Sources")
        lines.append("")
        lines.append("| Category | API | Status |")
        lines.append("|----------|-----|--------|")
        if api_stat:
            for category, status in api_stat.items():
                if isinstance(status, dict):
                    icon = "✓" if status.get("success") else "✗"
                    api = status.get("api_used") or ds.get(category, "none")
                    note = status.get("note", "")
                    status_str = icon
                    if note:
                        status_str += f" ({note})"
                    lines.append(f"| {category} | {api} | {status_str} |")
        elif ds:
            for category, api in ds.items():
                lines.append(f"| {category} | {api} | ✓ |")
        lines.append("")

    lines.append("---")
    lines.append("")
    return lines


def _print_portfolio_summary(review):
    """Print formatted portfolio summary and per-position detail to console."""
    s = review["summary"]
    positions = review["positions"]

    # Build the full report as lines — same content goes to console AND markdown
    output = []
    output.append(f"\n{'═' * 70}")
    output.append(f"  PORTFOLIO SUMMARY")
    output.append(f"{'═' * 70}")
    output.append(f"  Average Score:  {s['portfolio_avg_score']}/10")
    output.append(f"  Health:         {s['portfolio_rating']}")
    output.append(f"  Total Value:    ${s['total_value']:,.2f}")
    output.append(f"  Total Cost:     ${s['total_cost_basis']:,.2f}")

    pnl = s['total_pnl']
    pnl_pct = s['total_pnl_pct']
    pnl_icon = "+" if pnl >= 0 else ""
    output.append(f"  Total P&L:      {pnl_icon}${pnl:,.2f} ({pnl_icon}{pnl_pct:.1f}%)")

    output.append(f"\n  Strongest:      {s.get('strongest', 'N/A')}")
    output.append(f"  Weakest:        {s.get('weakest', 'N/A')}")
    output.append(f"  Biggest Winner: {s.get('biggest_winner', 'N/A')}")
    output.append(f"  Biggest Loser:  {s.get('biggest_loser', 'N/A')}")

    # Position summary table
    output.append(f"\n  {'Ticker':<8} {'Score':<7} {'Rating':<13} {'P&L %':>7} {'Total P&L':>11}  {'Action'}")
    output.append(f"  {'─' * 75}")
    for p in sorted(positions, key=lambda x: -x.get("composite_score", 0)):
        score_str = f"{p['composite_score']:.1f}" if p.get("composite_score") else "ERR"
        pnl_str = f"{p['pnl_pct']:+.1f}%" if p.get("pnl_pct") is not None else "N/A"
        total_str = f"${p['total_pnl']:+,.0f}" if p.get("total_pnl") is not None else "N/A"
        action = p.get("action", "N/A")
        if len(action) > 30:
            action = action[:27] + "..."
        output.append(f"  {p['ticker']:<8} {score_str:<7} {p.get('rating', 'N/A'):<13} {pnl_str:>7} {total_str:>11}  {action}")

    # Sector exposure
    se = s.get("sector_exposure")
    if se and se.get("sector_breakdown"):
        output.append(f"\n  {'─' * 60}")
        output.append(f"  SECTOR EXPOSURE")
        output.append(f"  {'─' * 60}")
        for item in se["sector_breakdown"]:
            mod_str = f" ({item['modifier']:+.2f})" if abs(item["modifier"]) > 0.01 else ""
            output.append(f"    {item['sector']:<28} {item['weight_pct']:>5.1f}%  {item['signal']}{mod_str}")

    # Per-position detail (using shared formatter)
    output.append(f"\n{'═' * 70}")
    output.append(f"  POSITION DETAILS")
    output.append(f"{'═' * 70}")
    for p in sorted(positions, key=lambda x: -x.get("composite_score", 0)):
        detail_lines = _format_position_detail(p)
        for line in detail_lines:
            output.append(f"  {line}")

    # Warnings
    if s["warnings"]:
        output.append(f"\n  {'─' * 60}")
        output.append(f"  WARNINGS")
        output.append(f"  {'─' * 60}")
        for w in s["warnings"]:
            output.append(f"    ⚠ {w}")

    output.append(f"\n  Elapsed: {review['elapsed_seconds']}s")
    output.append(f"{'═' * 70}\n")

    # Print everything to console
    for line in output:
        print(line)


# ═══════════════════════════════════════════════════════════════════════
#  MARKDOWN REPORT
# ═══════════════════════════════════════════════════════════════════════

def _save_markdown_report(review):
    """Save the full portfolio review as a human-readable markdown file."""
    today = datetime.now().strftime("%Y-%m-%d")
    data_dir = os.path.join(_project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    md_path = os.path.join(data_dir, f"portfolio_review_{today}.md")

    s = review["summary"]
    positions = review["positions"]
    macro = review.get("macro", {})

    lines = []
    lines.append(f"# Portfolio Review — {today}")
    lines.append(f"")
    lines.append(f"Generated: {review['review_date']}")
    lines.append(f"Holdings: {review['holdings_count']} positions | Elapsed: {review['elapsed_seconds']}s")
    lines.append(f"")

    # ── Portfolio Summary ──
    lines.append(f"## Portfolio Summary")
    lines.append(f"")
    pnl = s['total_pnl']
    pnl_pct = s['total_pnl_pct']
    pnl_icon = "+" if pnl >= 0 else ""
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Average Score | {s['portfolio_avg_score']}/10 |")
    lines.append(f"| Health | **{s['portfolio_rating']}** |")
    lines.append(f"| Total Value | ${s['total_value']:,.2f} |")
    lines.append(f"| Total Cost Basis | ${s['total_cost_basis']:,.2f} |")
    lines.append(f"| Total P&L | {pnl_icon}${pnl:,.2f} ({pnl_icon}{pnl_pct:.1f}%) |")
    lines.append(f"| Strongest | {s.get('strongest', 'N/A')} |")
    lines.append(f"| Weakest | {s.get('weakest', 'N/A')} |")
    lines.append(f"| Biggest Winner | {s.get('biggest_winner', 'N/A')} |")
    lines.append(f"| Biggest Loser | {s.get('biggest_loser', 'N/A')} |")
    lines.append(f"")

    # ── Macro Context ──
    if macro:
        lines.append(f"## Macro Context")
        lines.append(f"")
        for flag in macro.get("risk_flags", []):
            severity_icon = "🔴" if flag["severity"] == "HIGH" else "🟡"
            lines.append(f"- {severity_icon} **{flag['flag']}**: {flag['message']}")
        earnings = macro.get("earnings_calendar", [])
        if earnings:
            lines.append(f"")
            lines.append(f"### Upcoming Earnings")
            lines.append(f"")
            lines.append(f"| Ticker | Date | Days Until | Imminent? |")
            lines.append(f"|--------|------|-----------|-----------|")
            for e in earnings:
                imm = "⚠️ YES" if e.get("is_imminent") else ""
                lines.append(f"| {e['ticker']} | {e['earnings_date']} | {e['days_until']}d | {imm} |")
        events = macro.get("economic_events", [])
        if events:
            lines.append(f"")
            lines.append(f"### Economic Events")
            lines.append(f"")
            lines.append(f"| Event | Date | Days Until | Impact |")
            lines.append(f"|-------|------|-----------|--------|")
            for e in events:
                lines.append(f"| {e['event']} | {e['date']} | {e['days_until']}d | {e['impact']} |")
        lines.append(f"")

    # ── Sector Exposure ──
    se = s.get("sector_exposure")
    if se and se.get("sector_breakdown"):
        lines.append(f"## Sector Exposure")
        lines.append(f"")
        lines.append(f"| Sector | Weight | Signal | Modifier |")
        lines.append(f"|--------|--------|--------|----------|")
        for item in se["sector_breakdown"]:
            mod_str = f"{item['modifier']:+.2f}" if abs(item["modifier"]) > 0.01 else "—"
            lines.append(f"| {item['sector']} | {item['weight_pct']:.1f}% | {item['signal']} | {mod_str} |")
        lines.append(f"")

    # ── Position Summary Table ──
    lines.append(f"## All Positions")
    lines.append(f"")
    lines.append(f"| Ticker | Score | Rating | P&L % | Total P&L | Action |")
    lines.append(f"|--------|-------|--------|------:|----------:|--------|")
    for p in sorted(positions, key=lambda x: -x.get("composite_score", 0)):
        score_str = f"{p['composite_score']:.1f}" if p.get("composite_score") else "ERR"
        if p.get("price_error"):
            pnl_str = "NO DATA"
            total_str = "—"
        elif p.get("pnl_pct") is not None:
            pnl_str = f"{p['pnl_pct']:+.1f}%"
            total_str = f"${p['total_pnl']:+,.0f}"
        else:
            pnl_str = "N/A"
            total_str = "N/A"
        action = p.get("action", "N/A")
        lines.append(f"| {p['ticker']} | {score_str} | {p.get('rating', 'N/A')} | {pnl_str} | {total_str} | {action} |")
    lines.append(f"")

    # ── Per-Stock Details (using shared formatter) ──
    lines.append(f"## Position Details")
    lines.append(f"")
    for p in sorted(positions, key=lambda x: -x.get("composite_score", 0)):
        detail_lines = _format_position_detail(p)
        lines.extend(detail_lines)

    # ── Warnings ──
    if s.get("warnings"):
        lines.append(f"## Warnings")
        lines.append(f"")
        for w in s["warnings"]:
            lines.append(f"- ⚠️ {w}")
        lines.append(f"")

    # Write file
    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    return md_path


# ═══════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Weekly Portfolio Review",
        epilog="Examples:\n"
               "  python scripts/run_portfolio_review.py AAPL:100:150.50 MSFT:50:380\n"
               "  python scripts/run_portfolio_review.py --file portfolio.csv\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tickers", nargs="*",
                        help="Holdings as TICKER:SHARES:AVG_COST (e.g. AAPL:100:150.50)")
    parser.add_argument("--file", "-f", help="Path to CSV file with holdings")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress per-stock progress")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, force fresh API calls")
    args = parser.parse_args()

    # Load holdings
    if args.file:
        if not os.path.exists(args.file):
            print(f"File not found: {args.file}")
            sys.exit(1)
        holdings = load_holdings_from_file(args.file)
        print(f"Loaded {len(holdings)} holdings from {args.file}")
    elif args.tickers:
        holdings = []
        for t in args.tickers:
            parts = t.split(":")
            ticker = parts[0].upper()
            if len(parts) < 3:
                print(f"  ERROR: {t} — format must be TICKER:SHARES:AVG_COST")
                print(f"         Example: AAPL:100:150.50")
                sys.exit(1)
            try:
                shares = float(parts[1])
                avg_cost = float(parts[2])
            except ValueError:
                print(f"  ERROR: {t} — shares and avg_cost must be numbers")
                sys.exit(1)
            holdings.append({"ticker": ticker, "shares": shares, "avg_cost": avg_cost})
    else:
        print("Portfolio review requires holdings with cost basis.")
        print()
        print("Option 1 — Command line:")
        print("  python scripts/run_portfolio_review.py AAPL:100:150.50 MSFT:50:380")
        print()
        print("Option 2 — CSV file:")
        print("  python scripts/run_portfolio_review.py --file portfolio.csv")
        print()
        print("CSV format:")
        print("  ticker,shares,avg_cost")
        print("  AAPL,100,150.50")
        print("  MSFT,50,380.00")
        sys.exit(1)

    if not holdings:
        print("No valid holdings found.")
        sys.exit(1)

    config = load_config()
    review = run_portfolio_review(holdings, config, verbose=not args.quiet,
                                  use_cache=not args.no_cache)

    # Save to JSON if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(review, f, indent=2, default=str)
        print(f"Review saved to: {args.output}")

    # Usage report
    tracker = get_tracker()
    tracker.print_daily_report()


if __name__ == "__main__":
    main()
