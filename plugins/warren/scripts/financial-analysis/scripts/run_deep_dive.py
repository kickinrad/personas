#!/usr/bin/env python3
"""
On-Demand Stock Deep Dive — Use Case #3.

Analyzes 1-10 specific tickers through every available data source
and produces a full analyst-grade report with:
  - Composite score (0-10) with Buy/Watch·Hold/Sell rating
  - Fundamental, Technical, and Sentiment sub-scores
  - 3 Entry Levels + 3 Exit Targets
  - TradingView consensus cross-check
  - Data source attribution (which APIs succeeded/failed)

Usage:
    python scripts/run_deep_dive.py AAPL
    python scripts/run_deep_dive.py AAPL MSFT NVDA
    python scripts/run_deep_dive.py AAPL --output report.json
"""
import os, sys, json, argparse, time
from datetime import datetime

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.api_caller import call_api, call_with_fallback
from scripts.api_config import load_config
from scripts.data_fetchers import get_fetchers, tradingview_consensus
from scripts.technical_analysis import compute_technicals
from scripts.scoring import compute_composite_score, score_to_rating, score_to_portfolio_action
from scripts.entry_exit import compute_entry_exit, format_entry_exit
from scripts.usage_tracker import get_tracker
from scripts.data_cache import has_cache, load_cache, save_cache, get_cache_path
from scripts.sector_rotation import get_sector_modifier


# ═══════════════════════════════════════════════════════════════════
#  ANALYST DATA PARSER — normalises raw API output from any source
#  into a clean one-liner for display.
# ═══════════════════════════════════════════════════════════════════

def _format_analyst_line(source_id, raw_data):
    """
    Turn raw analyst data from *any* API source into a readable summary.

    Returns a clean string like:
        "25 Buy, 4 Hold, 0 Sell (86% buy)"           — Finnhub
        "Latest: Morgan Stanley → Overweight (Upgrade) | 28 total recs"  — yfinance
        "SA Authors: 17 Buy, 2 Hold, 2 Sell (81% buy) | Quant: 3.3/5"   — Seeking Alpha

    Falls back to a truncated repr if the structure is unrecognised.
    """
    if not isinstance(raw_data, dict):
        return str(raw_data)[:80]

    # ── Finnhub: {buy, strong_buy, hold, sell, strong_sell} ──
    if source_id == "finnhub":
        buy = raw_data.get("buy", 0) + raw_data.get("strong_buy", 0)
        hold = raw_data.get("hold", 0)
        sell = raw_data.get("sell", 0) + raw_data.get("strong_sell", 0)
        total = buy + hold + sell
        if total > 0:
            return f"{buy} Buy, {hold} Hold, {sell} Sell ({buy/total*100:.0f}% buy)"
        return "No analyst data"

    # ── yfinance: {ticker, firm, grade, action, total_recommendations} ──
    if source_id == "yfinance":
        firm = raw_data.get("firm", "").strip() or "Unknown firm"
        grade = raw_data.get("grade", "").strip() or raw_data.get("To Grade", "")
        action = raw_data.get("action", "").strip()
        total = raw_data.get("total_recommendations", 0)
        parts = [f"Latest: {firm}"]
        if grade:
            parts.append(f"→ {grade}")
        if action:
            parts.append(f"({action})")
        if total:
            parts.append(f"| {total} total recs")
        return " ".join(parts)

    # ── Seeking Alpha: {ticker, ratings: {data: [{attributes: {ratings: {...}}}]}} ──
    if source_id == "seeking_alpha_rapidapi":
        ratings_wrapper = raw_data.get("ratings", {})
        data_list = ratings_wrapper.get("data", []) if isinstance(ratings_wrapper, dict) else []
        if data_list and isinstance(data_list, list):
            latest = data_list[0]
            attrs = latest.get("attributes", {}) if isinstance(latest, dict) else {}
            r = attrs.get("ratings", {}) if isinstance(attrs, dict) else {}
            if r:
                sb = int(r.get("authorsRatingStrongBuyCount", 0) or 0)
                b = int(r.get("authorsRatingBuyCount", 0) or 0)
                h = int(r.get("authorsRatingHoldCount", 0) or 0)
                s = int(r.get("authorsRatingSellCount", 0) or 0)
                ss = int(r.get("authorsRatingStrongSellCount", 0) or 0)
                buy_total = sb + b
                sell_total = s + ss
                grand = buy_total + h + sell_total
                quant = r.get("quantRating")
                wall_st = r.get("sellSideRating")
                line = f"SA Authors: {buy_total} Buy, {h} Hold, {sell_total} Sell"
                if grand > 0:
                    line += f" ({buy_total/grand*100:.0f}% buy)"
                extras = []
                if quant is not None:
                    extras.append(f"Quant: {float(quant):.1f}/5")
                if wall_st is not None:
                    extras.append(f"Wall St: {float(wall_st):.1f}/5")
                if extras:
                    line += f" | {', '.join(extras)}"
                return line
        return "No Seeking Alpha ratings data"

    # ── Fallback for unknown sources ──
    buy = raw_data.get("buy", 0) + raw_data.get("strong_buy", 0)
    hold = raw_data.get("hold", 0)
    sell = raw_data.get("sell", 0) + raw_data.get("strong_sell", 0)
    total = buy + hold + sell
    if total > 0:
        return f"{buy} Buy, {hold} Hold, {sell} Sell ({buy/total*100:.0f}% buy)"
    return str(raw_data)[:80]


def deep_dive(ticker, config=None, verbose=True, use_cache=True):
    """
    Run a full deep dive analysis on a single ticker.

    Args:
        ticker: Stock ticker symbol
        config: API config (auto-loaded if None)
        verbose: Print progress to console
        use_cache: Check for same-day cached data before fetching (default True)

    Returns a comprehensive result dict.
    """
    config = config or load_config()

    def _log(msg):
        if verbose:
            print(f"  [{ticker}] {msg}")

    # ─── Cache Check ──────────────────────────────────────────────
    if use_cache and has_cache(ticker):
        _log("Found today's cached data — loading from disk...")
        cached = load_cache(ticker)
        if cached and cached.get("result"):
            cache_path = get_cache_path(ticker)
            _log(f"Loaded from cache: {os.path.basename(cache_path)}")
            result = cached["result"]
            result["from_cache"] = True
            return result
        else:
            _log("Cache file corrupted or incomplete — re-fetching...")

    fetchers = get_fetchers(ticker)
    results = {}
    api_status = {}    # track which APIs succeeded/failed
    data_sources = {}  # {category: api_id} — tracks which API served each data point
    raw_data = {}      # collect raw API data for cache

    _log("Starting deep dive...")
    start_time = time.time()

    # ─── 1. Price History (required) ─────────────────────────────
    _log("Fetching price history...")
    price_result = call_with_fallback("price_history", fetchers["price_history"], config)
    api_status["price_history"] = {
        "success": price_result["success"],
        "api_used": price_result.get("api_id"),
        "attempts": price_result.get("attempts", []),
    }
    if not price_result["success"]:
        _log("FAILED — no price data available. Cannot proceed.")
        return {
            "ticker": ticker,
            "error": "No price data available",
            "api_status": api_status,
        }
    price_data = price_result["data"]
    current_price = price_data.get("latest_close", 0)
    data_sources["price_history"] = price_result["api_id"]
    _log(f"Price: ${current_price:.2f} (from {price_result['api_id']})")
    raw_data["price_history"] = price_data

    # ─── 2. Fundamentals ────────────────────────────────────────
    _log("Fetching fundamentals...")
    fund_result = call_with_fallback("fundamentals", fetchers["fundamentals"], config)
    api_status["fundamentals"] = {
        "success": fund_result["success"],
        "api_used": fund_result.get("api_id"),
        "attempts": fund_result.get("attempts", []),
    }
    fundamentals = fund_result.get("data") if fund_result["success"] else None
    if fundamentals:
        data_sources["fundamentals"] = fund_result["api_id"]
        _log(f"Fundamentals loaded (from {fund_result['api_id']})")
        raw_data["fundamentals"] = fundamentals
    else:
        _log("Fundamentals: unavailable (will use neutral scores)")

    # ─── 3. Analyst Ratings (try ALL sources independently) ────
    _log("Fetching analyst ratings (all sources)...")
    all_analyst_results = {}
    analyst = None  # first successful result used for scoring
    for source_id in ["finnhub", "yfinance", "seeking_alpha_rapidapi"]:
        if source_id in fetchers["analyst_ratings"]:
            _log(f"  Trying analyst source: {source_id}...")
            res = call_api(source_id, "analyst_ratings", fetchers["analyst_ratings"][source_id])
            all_analyst_results[source_id] = {
                "success": res["success"],
                "data": res.get("data"),
                "error": res.get("error"),
            }
            if res["success"] and analyst is None:
                analyst = res["data"]
                data_sources["analyst_ratings"] = source_id
                _log(f"  {source_id}: ✓ (primary)")
            elif res["success"]:
                _log(f"  {source_id}: ✓ (additional)")
            else:
                _log(f"  {source_id}: ✗ ({res.get('error', 'failed')})")
        else:
            all_analyst_results[source_id] = {
                "success": False, "data": None,
                "error": "API key not configured (paid)",
            }
            _log(f"  {source_id}: — (API key not configured)")

    api_status["analyst_ratings"] = {
        "success": analyst is not None,
        "api_used": data_sources.get("analyst_ratings"),
        "all_sources": all_analyst_results,
    }
    if analyst:
        raw_data["analyst_ratings"] = analyst

    # ─── 4. Technical Analysis (local computation) ──────────────
    _log("Computing technical indicators...")
    try:
        price_df = price_data.get("data")
        technicals = compute_technicals(price_df, ticker)
        data_sources["technicals"] = "local (pandas/ta)"
        _log(f"Tech score: {technicals.get('tech_score', 'N/A')}")
        raw_data["technicals"] = technicals
    except Exception as e:
        _log(f"TA failed: {e}")
        technicals = None

    # ─── 5. TradingView Consensus ───────────────────────────────
    _log("Fetching TradingView consensus...")
    tv_result = call_api("tradingview", "tradingview",
                         lambda: tradingview_consensus(ticker))
    api_status["tradingview"] = {
        "success": tv_result["success"],
        "api_used": tv_result.get("api_id", "tradingview"),
    }
    tradingview = tv_result.get("data") if tv_result["success"] else None
    if tradingview:
        data_sources["tradingview"] = "tradingview-ta"
        _log(f"TradingView: {tradingview.get('recommendation', 'N/A')}")
        raw_data["tradingview"] = tradingview
    else:
        _log(f"TradingView: unavailable — {tv_result.get('error', 'unknown error')}")

    # ─── 6. Insider Trades ──────────────────────────────────────
    _log("Fetching insider trades...")
    insider_result = call_with_fallback("insider_trades", fetchers.get("insider_trades", {}), config)
    api_status["insider_trades"] = {
        "success": insider_result["success"],
        "api_used": insider_result.get("api_id"),
    }
    insider = insider_result.get("data") if insider_result["success"] else None
    if insider:
        data_sources["insider_trades"] = insider_result.get("api_id", "finnhub")
        raw_data["insider_trades"] = insider

    # ─── 7. News Sentiment ──────────────────────────────────────
    _log("Fetching news sentiment...")
    news_result = call_with_fallback("news_sentiment", fetchers.get("news_sentiment", {}), config)
    api_status["news_sentiment"] = {
        "success": news_result["success"],
        "api_used": news_result.get("api_id"),
    }
    news = news_result.get("data") if news_result["success"] else None
    if news:
        data_sources["news_sentiment"] = news_result.get("api_id", "unknown")
        # Inject source attribution so scoring engine can display it
        news["source"] = news_result.get("api_id", "Alpha Vantage")
        raw_data["news_sentiment"] = news

    # ─── 8. Reddit Sentiment ────────────────────────────────────
    _log("Fetching Reddit sentiment...")
    reddit_result = call_with_fallback("reddit_sentiment", fetchers.get("reddit_sentiment", {}), config)
    api_status["reddit_sentiment"] = {
        "success": reddit_result["success"],
        "api_used": reddit_result.get("api_id", "apewisdom"),
    }
    reddit = reddit_result.get("data") if reddit_result["success"] else None
    if reddit:
        data_sources["reddit_sentiment"] = "apewisdom"
        raw_data["reddit_sentiment"] = reddit

    # ─── 9. StockTwits Sentiment ────────────────────────────────
    _log("Fetching StockTwits sentiment...")
    st_result = call_with_fallback("social_sentiment", fetchers.get("social_sentiment", {}), config)
    api_status["social_sentiment"] = {
        "success": st_result["success"],
        "api_used": st_result.get("api_id", "stocktwits"),
    }
    stocktwits = st_result.get("data") if st_result["success"] else None
    if stocktwits:
        data_sources["social_sentiment"] = st_result.get("api_id", "stocktwits")
        raw_data["social_sentiment"] = stocktwits

    # ─── 10. Earnings ───────────────────────────────────────────
    _log("Fetching earnings data...")
    earn_result = call_with_fallback("earnings", fetchers.get("earnings", {}), config)
    api_status["earnings"] = {
        "success": earn_result["success"],
        "api_used": earn_result.get("api_id"),
    }
    earnings = earn_result.get("data") if earn_result["success"] else None
    if earnings:
        data_sources["earnings"] = earn_result.get("api_id", "finnhub")
        raw_data["earnings"] = earnings

    # ─── 11. Congress Trades (optional) ─────────────────────────
    congress = None
    if "congress_trades" in fetchers and fetchers["congress_trades"]:
        _log("Fetching Congress trades...")
        cong_result = call_with_fallback("congress_trades", fetchers["congress_trades"], config)
        api_status["congress_trades"] = {
            "success": cong_result["success"],
            "api_used": cong_result.get("api_id", "mboum"),
        }
        congress = cong_result.get("data") if cong_result["success"] else None
        if congress:
            data_sources["congress_trades"] = "mboum"
            raw_data["congress_trades"] = congress
    else:
        api_status["congress_trades"] = {"success": False, "api_used": "mboum", "note": "Mboum API key not configured"}

    # ─── 12. Dividends ──────────────────────────────────────────
    div_result = call_with_fallback("dividends", fetchers.get("dividends", {}), config)
    dividends = div_result.get("data") if div_result["success"] else None
    if dividends:
        data_sources["dividends"] = "yfinance"
        raw_data["dividends"] = dividends

    # ─── 13. RSS Articles (Seeking Alpha per-ticker + news feeds) ─
    _log("Scanning RSS feeds for articles...")
    rss_articles = []
    try:
        from scripts.rss_feeds import scan_ticker_feeds
        sa_articles = scan_ticker_feeds(ticker, max_age_hours=168)  # 7 days
        rss_articles.extend(sa_articles)
        if sa_articles:
            _log(f"Found {len(sa_articles)} Seeking Alpha articles")
    except Exception as e:
        _log(f"RSS scan failed: {e}")

    # Collect articles from news APIs too
    all_articles = _collect_articles(ticker, news, rss_articles)
    if all_articles:
        _log(f"Total articles collected: {len(all_articles)}")

    # ═══════════════════════════════════════════════════════════════
    #  SECTOR ROTATION MODIFIER
    # ═══════════════════════════════════════════════════════════════
    sector_mod = 0.0
    sector_name = ""
    if fundamentals:
        sector_name = fundamentals.get("sector", "")
    if sector_name:
        try:
            sector_mod = get_sector_modifier(sector_name)
            if abs(sector_mod) > 0.01:
                direction = "tailwind" if sector_mod > 0 else "headwind"
                _log(f"Sector ({sector_name}): {sector_mod:+.2f} {direction}")
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════
    #  COMPOSITE SCORING
    # ═══════════════════════════════════════════════════════════════
    _log("Computing composite score...")
    composite = compute_composite_score(
        fundamentals=fundamentals,
        technicals=technicals,
        analyst=analyst,
        insider=insider,
        congress=congress,
        tradingview=tradingview,
        earnings=earnings,
        reddit=reddit,
        stocktwits=stocktwits,
        news=news,
        sector_modifier=sector_mod,
    )
    _log(f"Composite: {composite['composite_score']}/10 → {composite['rating']}")

    # ═══════════════════════════════════════════════════════════════
    #  ENTRY / EXIT LEVELS
    # ═══════════════════════════════════════════════════════════════
    _log("Computing entry/exit levels...")
    try:
        entry_exit = compute_entry_exit(
            current_price=current_price,
            technicals=technicals,
            score=composite["composite_score"],
        )
    except Exception as e:
        _log(f"Entry/exit failed: {e}")
        entry_exit = None

    elapsed = round(time.time() - start_time, 1)
    _log(f"Done in {elapsed}s")

    # ═══════════════════════════════════════════════════════════════
    #  ASSEMBLE RESULT
    # ═══════════════════════════════════════════════════════════════
    result = {
        "ticker": ticker,
        "analysis_date": datetime.now().isoformat(),
        "current_price": current_price,
        "composite_score": composite["composite_score"],
        "rating": composite["rating"],
        "confidence": composite["confidence"],
        "action": score_to_portfolio_action(composite["composite_score"], current_holding=False),
        "sub_scores": composite["sub_scores"],
        "entry_exit": entry_exit,
        "tradingview": tradingview,
        "fundamentals_summary": _summarize_fundamentals(fundamentals),
        "dividends": {
            "yield": dividends.get("dividend_yield") if dividends else None,
            "payout_ratio": dividends.get("payout_ratio") if dividends else None,
        },
        "key_articles": all_articles[:10],
        "api_status": api_status,
        "data_sources": data_sources,
        "elapsed_seconds": elapsed,
        # Expanded detail fields for the report
        "all_analyst_results": all_analyst_results,
        "fundamentals_detail": fundamentals,
        "earnings_detail": earnings,
        "insider_detail": insider,
        "reddit_detail": reddit,
        "stocktwits_detail": stocktwits,
        "news_detail": news,
    }

    # ═══════════════════════════════════════════════════════════════
    #  SAVE TO DATA CACHE
    # ═══════════════════════════════════════════════════════════════
    try:
        raw_data["articles"] = all_articles
        raw_data["composite_score"] = composite
        raw_data["entry_exit"] = entry_exit
        raw_data["api_status"] = api_status

        # Save both the raw data (.md) and the final result (.json cache)
        cache_data = {**raw_data, "result": result}
        md_path = save_cache(ticker, cache_data)
        _log(f"Data saved to: {os.path.basename(md_path)}")
    except Exception as e:
        _log(f"Cache save failed (non-fatal): {e}")

    return result


def _summarize_fundamentals(f):
    """Create a clean summary of key fundamental metrics."""
    if not f:
        return None
    return {
        "name": f.get("name", ""),
        "sector": f.get("sector", ""),
        "market_cap": f.get("market_cap"),
        "pe_ratio": f.get("pe_ratio"),
        "forward_pe": f.get("forward_pe"),
        "pb_ratio": f.get("pb_ratio"),
        "revenue_growth": f.get("revenue_growth"),
        "earnings_growth": f.get("earnings_growth"),
        "profit_margin": f.get("profit_margin"),
        "roe": f.get("roe"),
        "debt_to_equity": f.get("debt_to_equity"),
        "free_cash_flow": f.get("free_cash_flow"),
        "analyst_target": f.get("target_mean_price"),
    }


def _collect_articles(ticker, news_data, rss_articles):
    """
    Merge articles from all sources into a single list, deduplicated by title,
    sorted by relevance (Seeking Alpha > AI-scored > general news).

    Each article dict: {source, title, summary, link, published, sentiment}
    """
    seen_titles = set()
    articles = []

    # 1. RSS articles (Seeking Alpha per-ticker — highest quality)
    for a in (rss_articles or []):
        title = a.get("title", "").strip()
        if not title or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())
        articles.append({
            "source": a.get("source", "Seeking Alpha"),
            "title": title,
            "summary": (a.get("summary", "") or "")[:300],
            "link": a.get("link", ""),
            "published": a.get("published", ""),
            "sentiment": None,
            "priority": 1,  # highest — Seeking Alpha thesis articles
        })

    # 2. Alpha Vantage articles (AI-scored sentiment)
    if news_data and news_data.get("articles"):
        sentiments = news_data.get("sentiment_scores", [])
        for i, a in enumerate(news_data["articles"][:15]):
            title = a.get("title", "").strip()
            if not title or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())
            # AV articles have per-ticker sentiment
            ticker_sent = None
            for ts in a.get("ticker_sentiment", []):
                if ts.get("ticker", "").upper() == ticker.upper():
                    ticker_sent = float(ts.get("ticker_sentiment_score", 0))
                    break
            articles.append({
                "source": a.get("source", "Alpha Vantage"),
                "title": title,
                "summary": (a.get("summary", "") or "")[:300],
                "link": a.get("url", a.get("link", "")),
                "published": a.get("time_published", ""),
                "sentiment": ticker_sent,
                "priority": 2,
            })

    # 3. Finnhub articles (headlines, no sentiment scoring)
    if news_data and news_data.get("articles") and not news_data.get("sentiment_scores"):
        for a in news_data["articles"][:15]:
            title = (a.get("headline", "") or a.get("title", "")).strip()
            if not title or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())
            articles.append({
                "source": a.get("source", "Finnhub News"),
                "title": title,
                "summary": (a.get("summary", "") or "")[:300],
                "link": a.get("url", ""),
                "published": a.get("datetime", ""),
                "sentiment": None,
                "priority": 3,
            })

    # Sort: priority first, then most recent
    def _sort_key(a):
        pub = a.get("published", "") or ""
        # Handle int timestamps (Finnhub), strings (ISO dates), or empty
        if isinstance(pub, (int, float)):
            return (a["priority"], -pub)
        return (a["priority"], str(pub))
    articles.sort(key=_sort_key)

    # Remove internal priority field; add sentiment flags
    for a in articles:
        a.pop("priority", None)
        sent = a.get("sentiment")

        # If no AI sentiment score, estimate from title keywords
        if sent is None:
            sent = _estimate_title_sentiment(a.get("title", ""))
            if sent is not None:
                a["sentiment"] = sent
                a["sentiment_method"] = "title_keywords"

        if sent is not None:
            if sent > 0.15:
                a["sentiment_flag"] = "🟢"
            elif sent < -0.15:
                a["sentiment_flag"] = "🔴"
            else:
                a["sentiment_flag"] = "🟡"
        else:
            a["sentiment_flag"] = "🟡"  # truly unknown

    return articles


# Keyword lists for title-based sentiment estimation
_BULLISH_KEYWORDS = {
    "upgrade", "upgrades", "upgraded", "outperform", "overweight",
    "strong buy", "beat", "beats", "beating", "surge", "surges", "surging",
    "soar", "soars", "soaring", "rally", "rallies", "rallying", "bullish",
    "record", "high-yield", "high yield", "dividend growth", "raises dividend",
    "dividend hike", "strong", "momentum", "breakout", "buy",
    "opportunity", "undervalued", "upside", "growth", "profit",
    "positive", "impressive", "exceeds", "top pick",
}
_BEARISH_KEYWORDS = {
    "downgrade", "downgrades", "downgraded", "underperform", "underweight",
    "sell", "miss", "misses", "missed", "decline", "declines", "declining",
    "plunge", "plunges", "plunging", "crash", "crashes", "crashing",
    "bearish", "cut", "cuts", "slashes", "warning", "warns", "risk",
    "overvalued", "downside", "loss", "negative", "disappoints",
    "disappointing", "weak", "weakening", "concern", "debt",
    "lawsuit", "fraud", "investigation",
}


def _estimate_title_sentiment(title):
    """
    Estimate sentiment from article title keywords when no AI score is available.

    Returns a float between -0.5 and +0.5, or None if no strong signal.
    """
    if not title:
        return None
    words = set(title.lower().split())
    # Also check for multi-word phrases
    title_lower = title.lower()
    bull_hits = sum(1 for kw in _BULLISH_KEYWORDS if kw in title_lower)
    bear_hits = sum(1 for kw in _BEARISH_KEYWORDS if kw in title_lower)

    if bull_hits == 0 and bear_hits == 0:
        return None  # no signal — stay unknown
    net = bull_hits - bear_hits
    # Scale: each net keyword shifts sentiment by ~0.2, capped at ±0.5
    score = max(-0.5, min(0.5, net * 0.2))
    return round(score, 2)


# ═══════════════════════════════════════════════════════════════════
#  REPORT PRINTER
# ═══════════════════════════════════════════════════════════════════

def print_report(result):
    """
    Print a formatted deep dive report to console with full factor detail,
    source attribution, and sentiment flags — matching the portfolio review format.
    """
    t = result["ticker"]
    fs = result.get("fundamentals_summary") or {}
    name = fs.get("name", "")
    cache_note = " (from cache)" if result.get("from_cache") else ""

    print(f"\n{'═' * 70}")
    print(f"  DEEP DIVE: {t}" + (f" — {name}" if name else ""))
    print(f"  {result['analysis_date'][:19]}{cache_note}")
    print(f"{'═' * 70}")
    print(f"  Price:      ${result['current_price']:.2f}")
    print(f"  Score:      {result['composite_score']}/10")
    print(f"  Rating:     {result['rating']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Action:     {result['action']}")

    # ═══════════════════════════════════════════════════════════
    #  FUNDAMENTAL SCORE with factor breakdown
    # ═══════════════════════════════════════════════════════════
    sub = result.get("sub_scores", {})
    fund_sub = sub.get("fundamental", {})
    if fund_sub:
        print(f"\n  {'─' * 60}")
        print(f"  FUNDAMENTAL SCORE: {fund_sub.get('score', 'N/A')}/10  "
              f"(weight: {fund_sub.get('weight', 0.4)*100:.0f}%)  [{fund_sub.get('confidence', 'N/A')}]")
        print(f"  {'─' * 60}")
        factors = fund_sub.get("factors", {})
        if factors:
            factor_names = {
                "pe_ratio": "PE Ratio", "pb_ratio": "PB Ratio",
                "revenue_growth": "Revenue Growth", "eps_growth": "EPS Growth",
                "profit_margin": "Profit Margin", "debt_to_equity": "Debt/Equity",
                "free_cash_flow": "Free Cash Flow", "roe": "Return on Equity",
                "analyst_consensus": "Analyst Consensus", "earnings_surprises": "Earnings Surprises",
            }
            for key in ["pe_ratio", "pb_ratio", "revenue_growth", "eps_growth",
                        "profit_margin", "debt_to_equity", "free_cash_flow", "roe",
                        "analyst_consensus", "earnings_surprises"]:
                f_data = factors.get(key, {})
                display_name = factor_names.get(key, key)
                value = f_data.get("value", "N/A")
                # Format special cases
                if key == "analyst_consensus" and f_data.get("buy") is not None:
                    value = f"{f_data['buy']}B/{f_data.get('hold',0)}H/{f_data.get('sell',0)}S ({f_data.get('buy_pct',0):.0f}% buy)"
                elif key == "analyst_consensus" and f_data.get("recommendation"):
                    value = f_data["recommendation"]
                elif key == "earnings_surprises" and f_data.get("beat_count") is not None:
                    value = f"{f_data['beat_count']}beat/{f_data['miss_count']}miss (avg {f_data.get('surprise_avg_pct', 0):+.1f}%)"
                elif isinstance(value, float):
                    if key in ("revenue_growth", "eps_growth", "profit_margin", "roe"):
                        value = f"{value:.1f}%"
                elif value is None:
                    value = "—"
                score = f_data.get("score", "—")
                rn = f_data.get("rating_note", "")
                print(f"    {display_name:<22} {str(value):<20} {score}/10  {rn}")

    # ═══════════════════════════════════════════════════════════
    #  TECHNICAL SCORE
    # ═══════════════════════════════════════════════════════════
    tech_sub = sub.get("technical", {})
    if tech_sub:
        print(f"\n  {'─' * 60}")
        print(f"  TECHNICAL SCORE: {tech_sub.get('score', 'N/A')}/10  "
              f"(weight: {tech_sub.get('weight', 0.3)*100:.0f}%)  [{tech_sub.get('confidence', 'N/A')}]")
        print(f"  {'─' * 60}")
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
            print(f"    RSI: {rsi_str}  |  MACD: {macd_str}  |  Above SMA50: {sma50_str}")
            print(f"    Above SMA200: {sma200_str}  |  BB Position: {bb_str}  |  Volume: {vol_str}  |  ADX: {adx_str}")

    # ═══════════════════════════════════════════════════════════
    #  SENTIMENT SCORE with factor breakdown
    # ═══════════════════════════════════════════════════════════
    sent_sub = sub.get("sentiment", {})
    if sent_sub:
        print(f"\n  {'─' * 60}")
        print(f"  SENTIMENT SCORE: {sent_sub.get('score', 'N/A')}/10  "
              f"(weight: {sent_sub.get('weight', 0.3)*100:.0f}%)  [{sent_sub.get('confidence', 'N/A')}]")
        print(f"  {'─' * 60}")
        factors = sent_sub.get("factors", {})
        if factors:
            sent_factor_names = {
                "reddit_sentiment": "Reddit", "stocktwits_sentiment": "StockTwits",
                "news_sentiment": "News Sentiment", "tradingview_consensus": "TradingView",
                "rss_buzz": "RSS Buzz", "insider_activity": "Insider Activity",
                "congress_trades": "Congress Trades",
            }
            for key in ["reddit_sentiment", "stocktwits_sentiment", "news_sentiment",
                        "tradingview_consensus", "rss_buzz", "insider_activity", "congress_trades"]:
                f_data = factors.get(key, {})
                display_name = sent_factor_names.get(key, key)
                score = f_data.get("score", "—")
                source = f_data.get("source", "—")
                rn = f_data.get("rating_note", f_data.get("note", ""))
                print(f"    {display_name:<20} {score}/10  [{source}]  {rn}")

    # ═══════════════════════════════════════════════════════════
    #  ANALYST RATINGS (all sources)
    # ═══════════════════════════════════════════════════════════
    all_analyst = result.get("all_analyst_results")
    if all_analyst:
        print(f"\n  {'─' * 60}")
        print(f"  ANALYST RATINGS (all sources)")
        print(f"  {'─' * 60}")
        source_labels = {"finnhub": "Finnhub", "yfinance": "yfinance", "seeking_alpha_rapidapi": "Seeking Alpha"}
        for src_id in ["finnhub", "yfinance", "seeking_alpha_rapidapi"]:
            src_data = all_analyst.get(src_id, {})
            label = source_labels.get(src_id, src_id)
            if src_data.get("success"):
                d = src_data.get("data", {})
                summary = _format_analyst_line(src_id, d)
                print(f"    {label:<20} ✓  {summary}")
            else:
                error = src_data.get("error", "unavailable")
                if "not configured" in error.lower() or "paid" in error.lower():
                    print(f"    {label:<20} —  Paid key required ($)")
                else:
                    print(f"    {label:<20} ✗  {error[:60]}")

    # ═══════════════════════════════════════════════════════════
    #  EARNINGS
    # ═══════════════════════════════════════════════════════════
    ear = result.get("earnings_detail")
    if ear:
        ear_source = (result.get("data_sources") or {}).get("earnings", "Finnhub")
        print(f"\n  {'─' * 60}")
        print(f"  EARNINGS (source: {ear_source})")
        print(f"  {'─' * 60}")
        quarters = ear.get("quarters", ear.get("earnings", []))
        if isinstance(quarters, list) and quarters:
            for q in quarters[:4]:
                period = q.get("period", q.get("quarter", ""))
                actual = q.get("actual", q.get("actual_eps"))
                estimate = q.get("estimate", q.get("estimated_eps"))
                surprise = q.get("surprise_pct", q.get("surprise_percent"))
                actual_str = f"${float(actual):.2f}" if actual is not None else "N/A"
                est_str = f"${float(estimate):.2f}" if estimate is not None else "N/A"
                surp_str = f"{float(surprise):+.1f}%" if surprise is not None else "—"
                print(f"    {period:<12} Actual: {actual_str}  Est: {est_str}  Surprise: {surp_str}")
        else:
            beat = ear.get("beat_count", 0)
            miss = ear.get("miss_count", 0)
            avg_surp = ear.get("surprise_avg", 0)
            print(f"    Beats: {beat} | Misses: {miss} | Avg Surprise: {avg_surp:+.1f}%")

    # ═══════════════════════════════════════════════════════════
    #  INSIDER TRADES
    # ═══════════════════════════════════════════════════════════
    ins = result.get("insider_detail")
    if ins:
        ins_source = (result.get("data_sources") or {}).get("insider_trades", "Finnhub")
        buys = ins.get("buys_last_50", 0)
        sells = ins.get("sells_last_50", 0)
        signal = ins.get("net_insider_signal", "neutral")
        print(f"\n  {'─' * 60}")
        print(f"  INSIDER TRADES (source: {ins_source})")
        print(f"  {'─' * 60}")
        print(f"    Buys: {buys}  |  Sells: {sells}  |  Signal: {signal}")

    # ═══════════════════════════════════════════════════════════
    #  KEY ARTICLES with sentiment flags
    # ═══════════════════════════════════════════════════════════
    articles = result.get("key_articles", [])
    if articles:
        print(f"\n  {'─' * 60}")
        print(f"  KEY ARTICLES ({len(articles)} found)")
        print(f"  {'─' * 60}")
        for i, a in enumerate(articles[:10]):
            flag = a.get("sentiment_flag", "🟡")
            source = a.get("source", "?")
            title = a.get("title", "Untitled")
            if len(title) > 65:
                title = title[:62] + "..."
            sent = a.get("sentiment")
            sent_str = f"  ({sent:+.2f})" if sent is not None else ""
            print(f"    {i+1}. {flag} [{source}] {title}{sent_str}")
            link = a.get("link", "")
            if link:
                print(f"       {link}")

    # Entry/Exit
    ee = result.get("entry_exit")
    if ee:
        print(f"\n{format_entry_exit(ee, t)}")

    # ═══════════════════════════════════════════════════════════
    #  DATA SOURCES
    # ═══════════════════════════════════════════════════════════
    ds = result.get("data_sources", {})
    print(f"\n  {'─' * 60}")
    print(f"  DATA SOURCES")
    print(f"  {'─' * 60}")
    for category, status in result.get("api_status", {}).items():
        if isinstance(status, dict):
            icon = "✓" if status.get("success") else "✗"
            api = status.get("api_used") or ds.get(category, "none")
            note = status.get("note", "")
            note_str = f"  ({note})" if note else ""
            print(f"    {category:<25} [{icon}]  via {api}{note_str}")
        else:
            print(f"    {category:<25} {status}")

    print(f"\n  Elapsed: {result.get('elapsed_seconds', 0)}s")
    print(f"{'═' * 70}\n")


def _fmt_pct(val):
    if val is None:
        return "N/A"
    pct = val * 100 if abs(val) < 1 else val
    return f"{pct:.1f}%"

def _fmt_dollars(val):
    if val is None:
        return "N/A"
    if abs(val) >= 1e9:
        return f"${val/1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"${val/1e6:.1f}M"
    return f"${val:,.0f}"


# ═══════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Stock Deep Dive Analysis")
    parser.add_argument("tickers", nargs="+", help="1-10 ticker symbols to analyze")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache and force fresh API calls")
    parser.add_argument("--refresh", action="store_true", help="Same as --no-cache")
    args = parser.parse_args()
    use_cache = not (args.no_cache or args.refresh)

    if len(args.tickers) > 10:
        print("Maximum 10 tickers per deep dive. Use the daily scanner for larger scans.")
        sys.exit(1)

    config = load_config()
    all_results = []

    for ticker in args.tickers:
        ticker = ticker.upper().strip()
        print(f"\n{'=' * 70}")
        print(f"  ANALYZING: {ticker}")
        print(f"{'=' * 70}")

        result = deep_dive(ticker, config, verbose=not args.quiet, use_cache=use_cache)
        all_results.append(result)

        if "error" not in result:
            print_report(result)
        else:
            print(f"\n  ERROR: {result['error']}\n")

    # Save to JSON if requested
    if args.output:
        output_path = args.output
        # Make results JSON-serializable (remove DataFrames)
        serializable = json.loads(json.dumps(all_results, default=str))
        with open(output_path, "w") as f:
            json.dump(serializable, f, indent=2, default=str)
        print(f"\nResults saved to: {output_path}")

    # Print usage report
    tracker = get_tracker()
    tracker.print_daily_report()

    return all_results


if __name__ == "__main__":
    main()
