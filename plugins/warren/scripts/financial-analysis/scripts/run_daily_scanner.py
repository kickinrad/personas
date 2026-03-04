#!/usr/bin/env python3
"""
Daily Opportunity Scanner — Use Case #2.

Scans multiple data sources daily to find new opportunities:
  1. RSS feeds (Seeking Alpha, financial news)
  2. Reddit trending stocks (ApeWisdom)
  3. StockTwits most active
  4. Congress trades (Mboum)
  5. Insider buying clusters

Then runs a quick-score on candidates and promotes the best ones to
a full deep dive with entry/exit targets.

Output: Growth-focused trade candidates with 3 entries + 3 exits.

Usage:
    python scripts/run_daily_scanner.py
    python scripts/run_daily_scanner.py --top 5 --output scan.json
    python scripts/run_daily_scanner.py --skip-rss --skip-reddit
"""
import os, sys, json, argparse, time
from datetime import datetime
from collections import defaultdict

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.api_caller import call_api, call_with_fallback
from scripts.api_config import load_config, is_api_available
from scripts.data_fetchers import (
    apewisdom_reddit_sentiment, stocktwits_sentiment,
    tradingview_consensus, mboum_congress_trades,
    yfinance_fundamentals, yfinance_price_history,
)
from scripts.technical_analysis import compute_technicals
from scripts.scoring import compute_quick_score, compute_composite_score, score_to_rating
from scripts.entry_exit import compute_entry_exit, format_entry_exit
from scripts.usage_tracker import get_tracker


def scan_rss_feeds():
    """Scan RSS feeds for mentioned tickers."""
    try:
        import feedparser
        import requests as _req
        from scripts.rss_feeds import FEEDS, extract_tickers
    except ImportError as e:
        print(f"  [RSS] Missing dependency — skipping RSS scan ({e})")
        return []

    print("  [RSS] Scanning financial news feeds...")
    tickers_mentioned = defaultdict(int)
    feeds_scanned = 0
    feeds_failed = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
    }

    # Use Tier 1 + Tier 2 feeds (FEEDS is a dict of {id: {url, tier, source}})
    for feed_id, feed_info in FEEDS.items():
        if feed_info.get("tier", 3) > 2:
            continue
        try:
            # Fetch with requests (has a timeout), then parse the content
            r = _req.get(feed_info["url"], headers=headers, timeout=8)
            if r.status_code != 200:
                feeds_failed += 1
                continue
            feed = feedparser.parse(r.content)
            if not feed.entries:
                feeds_failed += 1
                continue
            for entry in feed.entries[:10]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                text = f"{title} {summary}"
                found = extract_tickers(text)
                for t in found:
                    if t not in _COMMON_WORDS:
                        tickers_mentioned[t] += 1
            feeds_scanned += 1
            print(f"    ✓ {feed_info.get('source', feed_id)} ({len(feed.entries)} articles)")
        except _req.exceptions.Timeout:
            print(f"    ✗ {feed_info.get('source', feed_id)} (timeout)")
            feeds_failed += 1
        except Exception:
            feeds_failed += 1
            continue

    print(f"  [RSS] Scanned {feeds_scanned} feeds ({feeds_failed} failed), found {len(tickers_mentioned)} potential tickers")
    # Return tickers mentioned 2+ times (noise filter)
    return sorted(
        [(t, c) for t, c in tickers_mentioned.items() if c >= 2],
        key=lambda x: -x[1],
    )[:20]


def scan_reddit():
    """Get Reddit trending stocks from ApeWisdom."""
    print("  [Reddit] Fetching trending stocks...")
    try:
        result = call_api("apewisdom", "reddit_sentiment",
                          lambda: apewisdom_reddit_sentiment())
        if result["success"]:
            top = result["data"].get("top_stocks", [])[:15]
            tickers = [(s.get("ticker", ""), s.get("mentions", 0)) for s in top]
            print(f"  [Reddit] Found {len(tickers)} trending tickers")
            return tickers
    except Exception as e:
        print(f"  [Reddit] Error: {e}")
    return []


def scan_stocktwits():
    """Get active tickers from StockTwits trending or ApeWisdom as fallback."""
    print("  [StockTwits] Getting trending tickers...")
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    # Attempt 1: StockTwits trending endpoint
    try:
        r = requests.get(
            "https://api.stocktwits.com/api/2/trending/symbols.json",
            headers=headers, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            symbols = data.get("symbols", [])
            if symbols:
                tickers = [(s.get("symbol", ""), s.get("watchlist_count", 0)) for s in symbols[:15]]
                print(f"  [StockTwits] Found {len(tickers)} trending tickers")
                return tickers
        # If 403/429, fall through to fallback
        print(f"  [StockTwits] API returned {r.status_code}, trying ApeWisdom fallback...")
    except Exception as e:
        print(f"  [StockTwits] API error: {e}, trying ApeWisdom fallback...")

    # Attempt 2: ApeWisdom top stocks (Reddit-based, but fills the "social trending" slot)
    try:
        r = requests.get(
            "https://apewisdom.io/api/v1.0/filter/all-stocks/page/1",
            headers=headers, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            tickers = [(s.get("ticker", ""), s.get("mentions", 0)) for s in results[:15] if s.get("ticker")]
            if tickers:
                print(f"  [StockTwits→ApeWisdom] Found {len(tickers)} trending tickers (via ApeWisdom fallback)")
                return tickers
    except Exception as e:
        print(f"  [StockTwits→ApeWisdom] Fallback also failed: {e}")

    return []


def scan_congress_trades(config):
    """Get recent Congress trades."""
    if not is_api_available("mboum", config):
        print("  [Congress] Mboum API key not configured — skipping")
        return []

    print("  [Congress] Fetching recent trades...")
    try:
        result = call_api("mboum", "congress_trades",
                          lambda: mboum_congress_trades())
        if result["success"]:
            trades = result["data"].get("congress_trades", [])
            ticker_trades = defaultdict(list)
            for trade in trades[:50]:
                ticker = trade.get("ticker") or trade.get("symbol", "")
                if ticker:
                    ticker_trades[ticker.upper()].append(trade)
            # Return tickers with most Congress activity
            ranked = sorted(ticker_trades.items(), key=lambda x: -len(x[1]))[:10]
            tickers = [(t, len(trades)) for t, trades in ranked]
            print(f"  [Congress] Found {len(tickers)} tickers with recent trades")
            return tickers
    except Exception as e:
        print(f"  [Congress] Error: {e}")
    return []


def merge_candidates(sources):
    """
    Merge ticker lists from all sources, scoring by frequency across sources.
    Filters out crypto, forex, and junk tickers — stocks and ETFs only.

    Uses **normalized scoring** so that high-count sources (StockTwits ~50k
    watchlist counts) don't drown out low-count sources (RSS ~5 mentions,
    Reddit ~100 mentions).  Each source's counts are scaled to 0-100 within
    that source, then summed across sources with a diversity bonus for
    appearing in multiple sources.

    Returns list of (ticker, raw_mentions, source_count, combined_score, source_list)
    sorted by combined_score descending.
    """
    # ── Step 1: Collect raw counts per source, filtering junk ──
    source_tickers = {}          # {source_name: {ticker: raw_count}}
    filtered_count = 0

    for source_name, ticker_list in sources.items():
        source_tickers[source_name] = {}
        for ticker, count in ticker_list:
            if not ticker:
                continue
            ticker = ticker.upper()
            if not _is_valid_stock_ticker(ticker):
                filtered_count += 1
                continue
            source_tickers[source_name][ticker] = count

    if filtered_count:
        print(f"  Filtered out {filtered_count} non-stock tickers (crypto, forex, etc.)")

    # ── Step 2: Normalize counts within each source to 10-100 ──
    # Rank-based normalization: top ticker in any source gets 100,
    # last ticker gets 10.  This makes RSS mention-count-of-5 and
    # StockTwits watchlist-count-of-50k comparable.
    normalized = {}              # {source_name: {ticker: norm_score}}
    for source_name, tickers in source_tickers.items():
        if not tickers:
            continue
        # Sort by count descending so rank 0 = highest
        sorted_tickers = sorted(tickers.items(), key=lambda x: -x[1])
        n = len(sorted_tickers)
        normalized[source_name] = {}
        for rank, (ticker, _count) in enumerate(sorted_tickers):
            # rank 0 → 100, rank n-1 → 10  (linear interpolation)
            if n == 1:
                norm = 100.0
            else:
                norm = 100.0 - 90.0 * rank / (n - 1)
            normalized[source_name][ticker] = round(norm, 1)

    # ── Step 3: Merge across sources ──
    ticker_data = defaultdict(lambda: {
        "raw_mentions": 0, "norm_score": 0.0,
        "sources": set(), "source_scores": {},
    })

    for source_name, tickers in normalized.items():
        for ticker, norm_score in tickers.items():
            raw_count = source_tickers[source_name].get(ticker, 0)
            ticker_data[ticker]["raw_mentions"] += raw_count
            ticker_data[ticker]["norm_score"] += norm_score
            ticker_data[ticker]["sources"].add(source_name)
            ticker_data[ticker]["source_scores"][source_name] = norm_score

    # ── Step 4: Combined score with source-diversity bonus ──
    # Each *additional* source adds 50 pts, so a ticker found in 3 sources
    # gets +100 bonus on top of its ~300 norm_score (100 per source max).
    # This ensures multi-source tickers rank above single-source ones.
    ranked = []
    for ticker, data in ticker_data.items():
        source_count = len(data["sources"])
        diversity_bonus = (source_count - 1) * 50
        combined_score = diversity_bonus + data["norm_score"]
        ranked.append((
            ticker,
            data["raw_mentions"],
            source_count,
            round(combined_score, 1),
            sorted(data["sources"]),
        ))

    ranked.sort(key=lambda x: -x[3])
    return ranked


def quick_screen(ticker, config):
    """Run a quick fundamental + TradingView screen on a single ticker."""
    try:
        # Get fundamentals (yfinance only — no API key needed)
        fund = yfinance_fundamentals(ticker)
    except Exception:
        fund = None

    try:
        price_data = yfinance_price_history(ticker, period="3mo")
        df = price_data.get("data")
        ta = compute_technicals(df, ticker) if df is not None and not df.empty else None
    except Exception:
        ta = None

    try:
        tv = tradingview_consensus(ticker)
    except Exception:
        tv = None

    return compute_quick_score(fundamentals=fund, technicals=ta, tradingview=tv)


def run_scanner(args):
    """Main scanner workflow."""
    config = load_config()
    start_time = time.time()

    print(f"\n{'═' * 70}")
    print(f"  DAILY OPPORTUNITY SCANNER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═' * 70}\n")

    # ─── Phase 1: Source Scanning ────────────────────────────────
    print("PHASE 1: Scanning data sources for candidates...\n")
    sources = {}

    if not args.skip_rss:
        rss_tickers = scan_rss_feeds()
        if rss_tickers:
            sources["rss"] = rss_tickers

    if not args.skip_reddit:
        reddit_tickers = scan_reddit()
        if reddit_tickers:
            sources["reddit"] = reddit_tickers

    if not args.skip_stocktwits:
        st_tickers = scan_stocktwits()
        if st_tickers:
            sources["stocktwits"] = st_tickers

    if not args.skip_congress:
        cong_tickers = scan_congress_trades(config)
        if cong_tickers:
            sources["congress"] = cong_tickers

    if not sources:
        print("\nNo data sources returned results. Check API keys and network.")
        return []

    # ─── Phase 2: Merge & Rank ──────────────────────────────────
    print(f"\nPHASE 2: Merging and ranking candidates...\n")
    candidates = merge_candidates(sources)
    top_n = min(args.top, len(candidates))

    print(f"  Found {len(candidates)} unique tickers across {len(sources)} sources")
    print(f"  Top {top_n} candidates (ranked by normalised cross-source score):\n")
    print(f"  {'Rank':<6} {'Ticker':<8} {'Score':<8} {'Srcs':<6} {'Found In'}")
    print(f"  {'─' * 55}")
    for i, (ticker, mentions, src_count, score, src_list) in enumerate(candidates[:top_n]):
        print(f"  {i+1:<6} {ticker:<8} {score:<8.0f} {src_count:<6} {', '.join(src_list)}")

    # ─── Phase 3: Quick Score ───────────────────────────────────
    print(f"\nPHASE 3: Quick-scoring top {top_n} candidates...\n")
    scored = []
    for ticker, mentions, src_count, _, src_list in candidates[:top_n]:
        print(f"  Screening {ticker}...", end=" ", flush=True)
        qs = quick_screen(ticker, config)

        # Build a concise status showing which data sources returned data
        used = qs.get("sources_used", [])
        missing = qs.get("sources_missing", [])
        source_tag = ""
        if missing:
            missing_labels = {"fundamental": "yFinance-Fund", "technical": "yFinance-TA", "tradingview": "TradingView"}
            failed_names = [missing_labels.get(m, m) for m in missing]
            source_tag = f"  [missing: {', '.join(failed_names)}]"

        print(f"Score: {qs['quick_score']}/10 → {qs['rating']}{source_tag}")

        scored.append({
            "ticker": ticker,
            "mentions": mentions,
            "source_count": src_count,
            "sources": src_list,
            "quick_score": qs["quick_score"],
            "rating": qs["rating"],
            "fundamental": qs.get("fundamental_avg"),
            "technical": qs.get("technical"),
            "tradingview": qs.get("tradingview"),
            "sources_used": used,
            "sources_missing": missing,
        })
        time.sleep(0.5)  # be gentle with yfinance

    # Sort by quick score
    scored.sort(key=lambda x: -x["quick_score"])

    # ─── Phase 4: Deep Dive on Top Picks ────────────────────────
    # Promote candidates scoring 6+ to full deep dive
    promoted = [s for s in scored if s["quick_score"] >= 6.0][:args.deep_dive_count]

    deep_results = []
    if promoted:
        print(f"\nPHASE 4: Deep dive on {len(promoted)} top picks...\n")
        from scripts.run_deep_dive import deep_dive, print_report
        for candidate in promoted:
            result = deep_dive(candidate["ticker"], config, verbose=True,
                               use_cache=not getattr(args, 'no_cache', False))
            if "error" not in result:
                print_report(result)
                deep_results.append(result)
    else:
        print(f"\nPHASE 4: No candidates scored 6.0+ for deep dive.")

    # ─── Summary ────────────────────────────────────────────────
    elapsed = round(time.time() - start_time, 1)

    print(f"\n{'═' * 70}")
    print(f"  SCAN SUMMARY")
    print(f"{'═' * 70}")
    print(f"  Sources scanned:  {len(sources)}")
    print(f"  Candidates found: {len(candidates)}")
    print(f"  Quick-scored:     {len(scored)}")
    print(f"  Promoted to DD:   {len(promoted)}")
    print(f"  Elapsed time:     {elapsed}s")
    print(f"\n  {'Ticker':<8} {'Quick':<8} {'Rating':<12} {'Sources'}")
    print(f"  {'─' * 55}")
    for s in scored:
        marker = " **" if s["quick_score"] >= 6.0 else ""
        print(f"  {s['ticker']:<8} {s['quick_score']:<8.1f} {s['rating']:<12} {', '.join(s['sources'])}{marker}")
    print()

    # Save results
    if args.output:
        output = {
            "scan_date": datetime.now().isoformat(),
            "sources_scanned": list(sources.keys()),
            "candidates": scored,
            "deep_dives": deep_results,
            "elapsed_seconds": elapsed,
        }
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"  Results saved to: {args.output}")

    # Usage report
    tracker = get_tracker()
    tracker.print_daily_report()

    return scored


# Common English words that look like tickers — filter these out
_COMMON_WORDS = {
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
    "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HOW", "ITS", "MAY", "NEW",
    "NOW", "OLD", "SEE", "WAY", "WHO", "DID", "GET", "LET", "SAY", "SHE",
    "TOO", "USE", "CEO", "IPO", "ETF", "GDP", "SEC", "FDA", "FED", "NYSE",
    "AI", "EV", "PE", "US", "UK", "EU", "Q1", "Q2", "Q3", "Q4", "YOY",
    "EST", "PST", "CEO", "CFO", "COO", "CTO", "VP", "SVP", "EVP",
    "AM", "PM", "VS", "AN", "AS", "AT", "BE", "BY", "DO", "GO", "IF",
    "IN", "IS", "IT", "ME", "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP",
    "WE", "BIG", "TOP", "LOW", "KEY", "SET", "RUN", "HIT", "CUT", "BUY",
    "PUT", "USD", "JPY", "EUR", "GBP", "CAD", "AUD", "NZD", "RBI", "IMF",
    "JUST", "THIS", "THAT", "WITH", "HAVE", "FROM", "THEY", "BEEN", "SOME",
    "ALSO", "MORE", "THAN", "MOST", "VERY", "WILL", "WHAT", "WHEN", "EACH",
    "MUCH", "NEED", "YEAR", "OVER", "ONLY", "LAST", "NEXT", "LONG", "HIGH",
    "BEST", "DOWN", "BACK", "LOOK", "MAKE", "TAKE", "COME", "LIKE",
    "GOOD", "WELL", "CALL", "EVEN", "NEAR", "RISE", "DEAL", "FIRM",
    "NEWS", "FUND", "RISK", "GAIN", "LOSS", "SELL", "HOLD", "RATE",
    "CASH", "DEBT", "NOTE", "SAID", "SAYS", "MOVE", "PART", "INTO",
    "STILL", "AFTER", "ABOUT", "COULD", "WOULD", "THEIR", "WHICH",
    "OTHER", "BEING", "THESE", "THOSE", "FIRST", "WHILE",
    "STOCK", "SHARE", "MARKET", "PRICE", "TRADE", "VALUE",
}

# Crypto tickers and patterns to exclude — we only want stocks and ETFs
_CRYPTO_TICKERS = {
    "BTC", "ETH", "XRP", "SOL", "ADA", "DOGE", "DOT", "AVAX", "MATIC",
    "LINK", "UNI", "SHIB", "LTC", "BCH", "ATOM", "XLM", "NEAR", "ALGO",
    "FTM", "HBAR", "VET", "MANA", "SAND", "AXS", "THETA", "FIL", "EOS",
    "AAVE", "GRT", "XTZ", "FLOW", "CHZ", "ENJ", "CRV", "COMP", "YFI",
    "SUSHI", "BAT", "ZEC", "DASH", "XMR", "IOTA", "KLAY", "ONE",
    "CELO", "ANKR", "STORJ", "LRC", "IMX", "APE", "OP", "ARB",
    "SUI", "SEI", "TIA", "JUP", "WIF", "BONK", "PEPE", "FLOKI",
    "PENGU", "TOSHI", "DOG", "LUNC", "JASMY", "GALA", "RENDER",
}


def _is_valid_stock_ticker(ticker):
    """
    Check if a ticker looks like a valid stock/ETF (not crypto or junk).

    Filters out:
    - StockTwits crypto suffix (.X)
    - Known crypto tickers
    - Tickers with dots, dashes, or numbers (forex pairs, crypto, etc.)
    - Single-character tickers
    - Common words
    """
    if not ticker or len(ticker) < 2:
        return False
    t = ticker.upper()
    # StockTwits crypto convention: DOGE.X, BTC.X, etc.
    if ".X" in t or "-" in t:
        return False
    # Strip any trailing dot or suffix for the check
    base = t.split(".")[0]
    if base in _CRYPTO_TICKERS:
        return False
    if base in _COMMON_WORDS:
        return False
    # Tickers with numbers are usually crypto or warrants (skip)
    if any(c.isdigit() for c in base):
        return False
    # Valid US stock tickers are 1-5 uppercase letters only
    if not base.isalpha() or len(base) > 5:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Daily Opportunity Scanner")
    parser.add_argument("--top", type=int, default=10, help="Number of candidates to quick-score (default: 10)")
    parser.add_argument("--deep-dive-count", type=int, default=3, help="Max candidates to deep-dive (default: 3)")
    parser.add_argument("--output", "-o", help="Save results to JSON file")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS feed scanning")
    parser.add_argument("--skip-reddit", action="store_true", help="Skip Reddit scanning")
    parser.add_argument("--skip-stocktwits", action="store_true", help="Skip StockTwits scanning")
    parser.add_argument("--skip-congress", action="store_true", help="Skip Congress trades scanning")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache and force fresh API calls for deep dives")
    args = parser.parse_args()

    run_scanner(args)


if __name__ == "__main__":
    main()
