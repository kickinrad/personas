"""
Data Cache — Saves raw API data per ticker per day as human-readable .md files.

Every API call's raw data is formatted into a searchable markdown document stored
in the `data/` folder. The same file doubles as a cache: if today's data already
exists for a ticker, the deep dive skips redundant API calls and loads from disk.

File format: data/{TICKER}_{YYYY-MM-DD}.md
Cache format: data/.cache/{TICKER}_{YYYY-MM-DD}.json  (machine-readable sidecar)

Usage:
    from scripts.data_cache import has_cache, load_cache, save_cache

    # Check before fetching
    if has_cache("AAPL"):
        cached = load_cache("AAPL")  # returns dict of all sections
    else:
        ... fetch from APIs ...
        save_cache("AAPL", raw_data_dict)
"""
import os, sys, json
from datetime import datetime, date

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ─── Paths ────────────────────────────────────────────────────────────

DATA_DIR = os.path.join(_project_root, "data")
CACHE_DIR = os.path.join(DATA_DIR, ".cache")


def _ensure_dirs():
    """Create data/ and data/.cache/ if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def _today_str():
    return date.today().strftime("%Y-%m-%d")


def _md_path(ticker, day=None):
    day = day or _today_str()
    return os.path.join(DATA_DIR, f"{ticker.upper()}_{day}.md")


def _cache_path(ticker, day=None):
    day = day or _today_str()
    return os.path.join(CACHE_DIR, f"{ticker.upper()}_{day}.json")


# ═══════════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════════

def has_cache(ticker, day=None):
    """Check if today's data already exists for this ticker."""
    return os.path.exists(_cache_path(ticker, day))


def load_cache(ticker, day=None):
    """
    Load cached data for a ticker. Returns dict with section keys
    (price_history, fundamentals, technicals, etc.) or None if no cache.
    """
    path = _cache_path(ticker, day)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(ticker, data, config_status=None):
    """
    Save all raw API data for a ticker as both .md (human-readable)
    and .json (machine-readable cache).

    Args:
        ticker: Stock ticker symbol
        data: Dict of {section_name: raw_api_response_data}
              Expected keys: price_history, fundamentals, technicals,
              tradingview, analyst_ratings, insider_trades, news_sentiment,
              reddit_sentiment, social_sentiment, earnings, congress_trades,
              dividends, articles, composite_score, entry_exit, api_status
        config_status: Optional API status dict for the report header
    """
    _ensure_dirs()
    today = _today_str()

    # Save human-readable markdown FIRST (uses in-memory data, not serialized)
    md_path = _md_path(ticker, today)
    md_content = _format_markdown(ticker, today, data, config_status)
    with open(md_path, "w") as f:
        f.write(md_content)

    # Save machine-readable cache (JSON) — write to temp, then rename (atomic)
    cache_path = _cache_path(ticker, today)
    tmp_path = cache_path + ".tmp"
    try:
        serializable = _make_serializable(data)
        json_str = json.dumps(serializable, indent=2, default=str)
        with open(tmp_path, "w") as f:
            f.write(json_str)
        os.replace(tmp_path, cache_path)  # atomic rename
    except Exception as e:
        # If JSON serialization fails, still keep the .md file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"  ⚠ Cache JSON save failed for {ticker}: {e}")

    return md_path


def get_cache_path(ticker, day=None):
    """Return the .md file path for a given ticker and day."""
    return _md_path(ticker, day)


def list_cached_tickers(day=None):
    """List all tickers that have cached data for a given day."""
    day = day or _today_str()
    _ensure_dirs()
    tickers = []
    suffix = f"_{day}.json"
    for fname in os.listdir(CACHE_DIR):
        if fname.endswith(suffix):
            tickers.append(fname.replace(suffix, ""))
    return sorted(tickers)


# ═══════════════════════════════════════════════════════════════════════
#  MARKDOWN FORMATTER
# ═══════════════════════════════════════════════════════════════════════

def _format_markdown(ticker, day, data, config_status=None):
    """Build a detailed, searchable markdown file from all raw API data."""
    lines = []
    _h = lines.append

    _h(f"# {ticker} — Deep Dive Data — {day}")
    _h(f"")
    _h(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _h(f"")

    # ─── API Status Summary ───────────────────────────────────────
    api_status = data.get("api_status", {})
    if api_status:
        _h(f"## Data Source Status")
        _h(f"")
        _h(f"| Source | Status | API Used |")
        _h(f"|--------|--------|----------|")
        for src, status in api_status.items():
            icon = "✓" if status.get("success") else "✗"
            api_used = status.get("api_used", "—")
            _h(f"| {src} | {icon} | {api_used} |")
        _h(f"")

    # ─── Price History ────────────────────────────────────────────
    price = data.get("price_history")
    if price:
        _h(f"## Price History")
        _h(f"")
        _h(f"- **Latest Close:** ${_safe_num(price.get('latest_close'), '$')}")
        _h(f"- **Previous Close:** ${_safe_num(price.get('previous_close'), '$')}")
        _h(f"- **52-Week High:** ${_safe_num(price.get('week_52_high'), '$')}")
        _h(f"- **52-Week Low:** ${_safe_num(price.get('week_52_low'), '$')}")
        _h(f"- **Volume:** {_safe_num(price.get('volume'), 'int')}")
        _h(f"- **Avg Volume:** {_safe_num(price.get('avg_volume'), 'int')}")

        change = price.get("daily_change_pct")
        if change is not None:
            _h(f"- **Daily Change:** {change:.2f}%")

        # Price data table (last 20 days if available)
        df_data = price.get("data")
        if df_data is not None and hasattr(df_data, "tail"):
            _h(f"")
            _h(f"### Recent Price Data (Last 20 Trading Days)")
            _h(f"")
            recent = df_data.tail(20)
            _h(f"| Date | Open | High | Low | Close | Volume |")
            _h(f"|------|------|------|-----|-------|--------|")
            for idx, row in recent.iterrows():
                dt = str(idx)[:10] if hasattr(idx, 'strftime') else str(idx)[:10]
                _h(f"| {dt} | {row.get('Open', 'N/A'):.2f} | {row.get('High', 'N/A'):.2f} | {row.get('Low', 'N/A'):.2f} | {row.get('Close', 'N/A'):.2f} | {int(row.get('Volume', 0)):,} |")
        _h(f"")

    # ─── Fundamentals ─────────────────────────────────────────────
    fund = data.get("fundamentals")
    if fund:
        _h(f"## Fundamentals")
        _h(f"")
        _h(f"- **Company:** {fund.get('name', 'N/A')}")
        _h(f"- **Sector:** {fund.get('sector', 'N/A')}")
        _h(f"- **Industry:** {fund.get('industry', 'N/A')}")
        _h(f"- **Market Cap:** {_fmt_large_num(fund.get('market_cap'))}")
        _h(f"")
        _h(f"### Valuation")
        _h(f"- PE Ratio (TTM): {_safe_num(fund.get('pe_ratio'))}")
        _h(f"- Forward PE: {_safe_num(fund.get('forward_pe'))}")
        _h(f"- PB Ratio: {_safe_num(fund.get('pb_ratio'))}")
        _h(f"- PS Ratio: {_safe_num(fund.get('ps_ratio'))}")
        _h(f"- EV/EBITDA: {_safe_num(fund.get('ev_to_ebitda'))}")
        _h(f"- PEG Ratio: {_safe_num(fund.get('peg_ratio'))}")
        _h(f"")
        _h(f"### Growth")
        _h(f"- Revenue Growth: {_fmt_pct(fund.get('revenue_growth'))}")
        _h(f"- Earnings Growth: {_fmt_pct(fund.get('earnings_growth'))}")
        _h(f"- EPS (TTM): {_safe_num(fund.get('eps_ttm'))}")
        _h(f"- EPS Forward: {_safe_num(fund.get('eps_forward'))}")
        _h(f"")
        _h(f"### Profitability")
        _h(f"- Profit Margin: {_fmt_pct(fund.get('profit_margin'))}")
        _h(f"- Operating Margin: {_fmt_pct(fund.get('operating_margin'))}")
        _h(f"- ROE: {_fmt_pct(fund.get('roe'))}")
        _h(f"- ROA: {_fmt_pct(fund.get('roa'))}")
        _h(f"")
        _h(f"### Financial Health")
        _h(f"- Debt-to-Equity: {_safe_num(fund.get('debt_to_equity'))}")
        _h(f"- Current Ratio: {_safe_num(fund.get('current_ratio'))}")
        _h(f"- Free Cash Flow: {_fmt_large_num(fund.get('free_cash_flow'))}")
        _h(f"- Total Cash: {_fmt_large_num(fund.get('total_cash'))}")
        _h(f"- Total Debt: {_fmt_large_num(fund.get('total_debt'))}")
        _h(f"")
        _h(f"### Analyst Estimates")
        _h(f"- Target Mean Price: {_safe_num(fund.get('target_mean_price'), '$')}")
        _h(f"- Target High: {_safe_num(fund.get('target_high_price'), '$')}")
        _h(f"- Target Low: {_safe_num(fund.get('target_low_price'), '$')}")
        _h(f"- Recommendation: {fund.get('recommendation_key', 'N/A')}")
        _h(f"")

        # Dump any extra keys not explicitly formatted
        _h(f"### All Fundamental Data")
        _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(fund), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── Technical Analysis ───────────────────────────────────────
    tech = data.get("technicals")
    if tech:
        _h(f"## Technical Analysis")
        _h(f"")
        _h(f"- **Tech Score:** {_safe_num(tech.get('tech_score'))}/10")
        _h(f"")
        _h(f"### Trend")
        _h(f"- SMA 20: {_safe_num(tech.get('sma_20'), '$')}")
        _h(f"- SMA 50: {_safe_num(tech.get('sma_50'), '$')}")
        _h(f"- SMA 200: {_safe_num(tech.get('sma_200'), '$')}")
        _h(f"- Price vs SMA50: {'Above' if tech.get('above_sma50') else 'Below'}")
        _h(f"- Price vs SMA200: {'Above' if tech.get('above_sma200') else 'Below'}")
        _h(f"- Golden Cross: {'Yes' if tech.get('golden_cross') else 'No'}")
        _h(f"- Death Cross: {'Yes' if tech.get('death_cross') else 'No'}")
        _h(f"")
        _h(f"### Momentum")
        _h(f"- RSI (14): {_safe_num(tech.get('rsi'))}")
        _h(f"- MACD: {_safe_num(tech.get('macd'))}")
        _h(f"- MACD Signal: {_safe_num(tech.get('macd_signal'))}")
        _h(f"- MACD Histogram: {_safe_num(tech.get('macd_hist'))}")
        _h(f"- Stochastic %K: {_safe_num(tech.get('stoch_k'))}")
        _h(f"- Stochastic %D: {_safe_num(tech.get('stoch_d'))}")
        _h(f"- ADX: {_safe_num(tech.get('adx'))}")
        _h(f"")
        _h(f"### Volatility")
        _h(f"- ATR (14): {_safe_num(tech.get('atr'), '$')}")
        _h(f"- Bollinger Upper: {_safe_num(tech.get('bb_upper'), '$')}")
        _h(f"- Bollinger Middle: {_safe_num(tech.get('bb_middle'), '$')}")
        _h(f"- Bollinger Lower: {_safe_num(tech.get('bb_lower'), '$')}")
        _h(f"- BB Width: {_safe_num(tech.get('bb_width'))}")
        _h(f"- BB %B: {_safe_num(tech.get('bb_pctb'))}")
        _h(f"")
        _h(f"### Support & Resistance")
        supports = tech.get("support_levels", [])
        resistances = tech.get("resistance_levels", [])
        if supports:
            _h(f"- Supports: {', '.join([f'${s:.2f}' for s in supports[:5]])}")
        if resistances:
            _h(f"- Resistances: {', '.join([f'${r:.2f}' for r in resistances[:5]])}")

        fibs = tech.get("fibonacci_levels", {})
        if fibs:
            _h(f"")
            _h(f"### Fibonacci Levels")
            for level, price in fibs.items():
                _h(f"- {level}: ${price:.2f}" if isinstance(price, (int, float)) else f"- {level}: {price}")
        _h(f"")

        _h(f"### Volume Analysis")
        _h(f"- Volume Ratio (vs avg): {_safe_num(tech.get('volume_ratio'))}")
        _h(f"- Volume Trend: {tech.get('volume_trend', 'N/A')}")
        _h(f"")

    # ─── TradingView Consensus ────────────────────────────────────
    tv = data.get("tradingview")
    if tv:
        _h(f"## TradingView Consensus")
        _h(f"")
        _h(f"- **Recommendation:** {tv.get('recommendation', 'N/A')}")
        _h(f"- Buy Signals: {tv.get('buy_count', 'N/A')}")
        _h(f"- Neutral Signals: {tv.get('neutral_count', 'N/A')}")
        _h(f"- Sell Signals: {tv.get('sell_count', 'N/A')}")
        if tv.get("oscillators"):
            _h(f"")
            _h(f"### Oscillators")
            _h(f"- Recommendation: {tv['oscillators'].get('RECOMMENDATION', 'N/A')}")
            for k, v in tv.get("oscillators_detail", {}).items():
                _h(f"- {k}: {v}")
        if tv.get("moving_averages"):
            _h(f"")
            _h(f"### Moving Averages")
            _h(f"- Recommendation: {tv['moving_averages'].get('RECOMMENDATION', 'N/A')}")
        _h(f"")

    # ─── Analyst Ratings ──────────────────────────────────────────
    analyst = data.get("analyst_ratings")
    if analyst:
        _h(f"## Analyst Ratings")
        _h(f"")
        if isinstance(analyst, dict):
            _h(f"- **Consensus:** {analyst.get('consensus', 'N/A')}")
            _h(f"- **Target Price:** {_safe_num(analyst.get('target_price'), '$')}")
            _h(f"- Strong Buy: {analyst.get('strong_buy', 'N/A')}")
            _h(f"- Buy: {analyst.get('buy', 'N/A')}")
            _h(f"- Hold: {analyst.get('hold', 'N/A')}")
            _h(f"- Sell: {analyst.get('sell', 'N/A')}")
            _h(f"- Strong Sell: {analyst.get('strong_sell', 'N/A')}")
            _h(f"")
            _h(f"```json")
            _h(json.dumps(_make_serializable(analyst), indent=2, default=str))
            _h(f"```")
        else:
            _h(f"```json")
            _h(json.dumps(_make_serializable(analyst), indent=2, default=str))
            _h(f"```")
        _h(f"")

    # ─── Earnings ─────────────────────────────────────────────────
    earnings = data.get("earnings")
    if earnings:
        _h(f"## Earnings")
        _h(f"")
        if isinstance(earnings, dict):
            recent = earnings.get("recent_quarters", earnings.get("earnings_history", []))
            if recent and isinstance(recent, list):
                _h(f"### Recent Quarters")
                _h(f"")
                _h(f"| Quarter | EPS Actual | EPS Estimate | Surprise |")
                _h(f"|---------|-----------|-------------|----------|")
                for q in recent[:8]:
                    quarter = q.get("quarter", q.get("period", "N/A"))
                    actual = _safe_num(q.get("actual", q.get("epsActual")))
                    estimate = _safe_num(q.get("estimate", q.get("epsEstimate")))
                    surprise = _safe_num(q.get("surprise", q.get("surprisePercent")))
                    _h(f"| {quarter} | {actual} | {estimate} | {surprise} |")
                _h(f"")
            _h(f"```json")
            _h(json.dumps(_make_serializable(earnings), indent=2, default=str))
            _h(f"```")
        else:
            _h(f"```json")
            _h(json.dumps(_make_serializable(earnings), indent=2, default=str))
            _h(f"```")
        _h(f"")

    # ─── Insider Trades ───────────────────────────────────────────
    insider = data.get("insider_trades")
    if insider:
        _h(f"## Insider Trades")
        _h(f"")
        if isinstance(insider, dict):
            _h(f"- Net Activity (3m): {insider.get('net_activity', 'N/A')}")
            _h(f"- Buys: {insider.get('buy_count', 'N/A')}")
            _h(f"- Sells: {insider.get('sell_count', 'N/A')}")
            _h(f"- Net Shares: {insider.get('net_shares', 'N/A')}")
            trades = insider.get("recent_trades", [])
            if trades:
                _h(f"")
                _h(f"### Recent Trades")
                _h(f"")
                _h(f"| Date | Name | Type | Shares | Price |")
                _h(f"|------|------|------|--------|-------|")
                for t in trades[:15]:
                    _h(f"| {t.get('date', 'N/A')} | {t.get('name', 'N/A')} | {t.get('transaction_type', 'N/A')} | {_safe_num(t.get('shares'), 'int')} | {_safe_num(t.get('price'), '$')} |")
            _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(insider), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── News Sentiment ───────────────────────────────────────────
    news = data.get("news_sentiment")
    if news:
        _h(f"## News Sentiment")
        _h(f"")
        if isinstance(news, dict):
            _h(f"- Overall Sentiment: {news.get('overall_sentiment', 'N/A')}")
            _h(f"- Sentiment Score: {_safe_num(news.get('sentiment_score'))}")
            _h(f"- Articles Analyzed: {news.get('article_count', 'N/A')}")
            articles_list = news.get("articles", [])
            if articles_list:
                _h(f"")
                _h(f"### Headlines")
                _h(f"")
                for i, a in enumerate(articles_list[:20]):
                    title = a.get("title", a.get("headline", "Untitled"))
                    source = a.get("source", "Unknown")
                    url = a.get("url", a.get("link", ""))
                    sent = a.get("overall_sentiment_score", "")
                    sent_str = f" (sentiment: {sent})" if sent else ""
                    _h(f"{i+1}. **[{source}]** {title}{sent_str}")
                    if url:
                        _h(f"   {url}")
            _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(news), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── Reddit Sentiment ─────────────────────────────────────────
    reddit = data.get("reddit_sentiment")
    if reddit:
        _h(f"## Reddit Sentiment (ApeWisdom)")
        _h(f"")
        if isinstance(reddit, dict):
            _h(f"- Mentions (24h): {reddit.get('mentions', 'N/A')}")
            _h(f"- Rank: #{reddit.get('rank', 'N/A')}")
            _h(f"- Upvotes: {reddit.get('upvotes', 'N/A')}")
            _h(f"- Mentions Change: {reddit.get('mentions_change', 'N/A')}")
        _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(reddit), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── StockTwits / Social Sentiment ────────────────────────────
    social = data.get("social_sentiment")
    if social:
        _h(f"## Social Sentiment (StockTwits)")
        _h(f"")
        if isinstance(social, dict):
            _h(f"- Bullish: {social.get('bullish', social.get('bull_count', 'N/A'))}")
            _h(f"- Bearish: {social.get('bearish', social.get('bear_count', 'N/A'))}")
            _h(f"- Bull/Bear Ratio: {_safe_num(social.get('bull_bear_ratio'))}")
            _h(f"- Message Volume: {social.get('message_volume', 'N/A')}")
            _h(f"- Trending: {social.get('trending', 'N/A')}")
        _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(social), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── Congress Trades ──────────────────────────────────────────
    congress = data.get("congress_trades")
    if congress:
        _h(f"## Congress Trades")
        _h(f"")
        if isinstance(congress, list):
            _h(f"| Date | Member | Type | Amount |")
            _h(f"|------|--------|------|--------|")
            for t in congress[:20]:
                _h(f"| {t.get('date', 'N/A')} | {t.get('member', 'N/A')} | {t.get('type', 'N/A')} | {t.get('amount', 'N/A')} |")
        elif isinstance(congress, dict):
            _h(f"- Recent Trades: {congress.get('trade_count', 'N/A')}")
            trades = congress.get("trades", [])
            if trades:
                _h(f"")
                _h(f"| Date | Member | Type | Amount |")
                _h(f"|------|--------|------|--------|")
                for t in trades[:20]:
                    _h(f"| {t.get('date', 'N/A')} | {t.get('member', 'N/A')} | {t.get('type', 'N/A')} | {t.get('amount', 'N/A')} |")
        _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(congress), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── Dividends ────────────────────────────────────────────────
    divs = data.get("dividends")
    if divs:
        _h(f"## Dividends")
        _h(f"")
        if isinstance(divs, dict):
            _h(f"- Dividend Yield: {_fmt_pct(divs.get('dividend_yield'))}")
            _h(f"- Payout Ratio: {_fmt_pct(divs.get('payout_ratio'))}")
            _h(f"- Annual Dividend: {_safe_num(divs.get('annual_dividend'), '$')}")
            _h(f"- Ex-Dividend Date: {divs.get('ex_dividend_date', 'N/A')}")
        _h(f"")
        _h(f"```json")
        _h(json.dumps(_make_serializable(divs), indent=2, default=str))
        _h(f"```")
        _h(f"")

    # ─── Articles ─────────────────────────────────────────────────
    articles = data.get("articles", [])
    if articles:
        _h(f"## Key Articles ({len(articles)} found)")
        _h(f"")
        for i, a in enumerate(articles[:20]):
            source = a.get("source", "Unknown")
            title = a.get("title", "Untitled")
            link = a.get("link", "")
            summary = a.get("summary", "")
            published = a.get("published", "")
            sentiment = a.get("sentiment")

            sent_str = ""
            if sentiment is not None:
                if sentiment > 0.15:
                    sent_str = f" — **BULLISH** ({sentiment:+.2f})"
                elif sentiment < -0.15:
                    sent_str = f" — **BEARISH** ({sentiment:+.2f})"
                else:
                    sent_str = f" — neutral ({sentiment:+.2f})"

            _h(f"### {i+1}. [{source}] {title}{sent_str}")
            if published:
                _h(f"*Published: {published}*")
            if summary:
                clean = summary.replace("\n", " ").replace("<p>", "").replace("</p>", "").strip()
                if clean:
                    _h(f"")
                    _h(f"> {clean[:500]}")
            if link:
                _h(f"")
                _h(f"[Read article]({link})")
            _h(f"")

    # ─── Composite Score & Entry/Exit ─────────────────────────────
    score_data = data.get("composite_score")
    if score_data:
        _h(f"## Composite Score")
        _h(f"")
        if isinstance(score_data, dict):
            _h(f"- **Score:** {score_data.get('composite_score', 'N/A')}/10")
            _h(f"- **Rating:** {score_data.get('rating', 'N/A')}")
            _h(f"- **Confidence:** {score_data.get('confidence', 'N/A')}")
            subs = score_data.get("sub_scores", {})
            if subs:
                _h(f"")
                _h(f"### Sub-Scores")
                for name, sub in subs.items():
                    _h(f"- {name.capitalize()}: {sub.get('score', 'N/A')}/10 (weight: {sub.get('weight', 0)*100:.0f}%) [{sub.get('confidence', 'N/A')}]")
        _h(f"")

    ee = data.get("entry_exit")
    if ee:
        _h(f"## Entry / Exit Levels")
        _h(f"")
        if isinstance(ee, dict):
            entries = ee.get("entries", {})
            if entries:
                _h(f"### Entry Levels")
                for level, info in entries.items():
                    if isinstance(info, dict):
                        _h(f"- **{level.replace('_', ' ').title()}:** ${info.get('price', 0):.2f} ({info.get('note', '')})")
                    else:
                        _h(f"- **{level}:** ${info:.2f}" if isinstance(info, (int, float)) else f"- **{level}:** {info}")

            targets = ee.get("targets", {})
            if targets:
                _h(f"")
                _h(f"### Exit Targets")
                for level, info in targets.items():
                    if isinstance(info, dict):
                        rr = info.get("risk_reward", {})
                        rr_str = ""
                        if rr:
                            for entry_name, ratio_info in rr.items():
                                if isinstance(ratio_info, dict):
                                    rr_str += f" | {entry_name} R:R = {ratio_info.get('ratio', 'N/A')}x"
                        _h(f"- **{level.replace('_', ' ').title()}:** ${info.get('price', 0):.2f}{rr_str}")
                    else:
                        _h(f"- **{level}:** ${info:.2f}" if isinstance(info, (int, float)) else f"- **{level}:** {info}")

            stop = ee.get("stop_loss")
            if stop:
                if isinstance(stop, dict):
                    _h(f"")
                    _h(f"### Stop Loss")
                    _h(f"- **Price:** ${stop.get('price', 0):.2f}")
                    _h(f"- **Risk:** {stop.get('pct_from_current', 0):.1f}% from current")
                else:
                    _h(f"- **Stop Loss:** ${stop:.2f}")

            sizing = ee.get("position_sizes")
            if sizing:
                _h(f"")
                _h(f"### Position Sizing")
                for acct, info in sizing.items():
                    if isinstance(info, dict):
                        _h(f"- {acct}: {info.get('shares', 'N/A')} shares (${info.get('cost', 0):,.0f})")
                    else:
                        _h(f"- {acct}: {info}")
        _h(f"")

    # ─── Footer ───────────────────────────────────────────────────
    _h(f"---")
    _h(f"*Data cached at {datetime.now().strftime('%H:%M:%S')} on {day}. "
       f"Same-day queries will use this cached data.*")
    _h(f"")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _make_serializable(obj):
    """Convert an object tree into JSON-serializable form.

    DataFrames are compressed to last-20-row summaries to keep cache files
    small and prevent truncation.  The full DataFrame is only used by the
    .md formatter (which reads from memory, not from the JSON cache).
    """
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_make_serializable(v) for v in obj]
    # Handle pandas DataFrames — compress to summary instead of full dump
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            return _compress_dataframe(obj)
        if isinstance(obj, pd.Series):
            return {str(k): _make_serializable(v) for k, v in obj.to_dict().items()}
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
    except ImportError:
        pass
    # Handle objects with to_dict (non-pandas)
    if hasattr(obj, "to_dict") and not hasattr(obj, "iloc"):
        try:
            return obj.to_dict()
        except Exception:
            return str(obj)
    # Handle numpy types
    if hasattr(obj, "item"):
        try:
            return obj.item()
        except Exception:
            return str(obj)
    # Handle numpy int64/float64 without .item()
    type_name = type(obj).__name__
    if "int" in type_name or "float" in type_name:
        try:
            return float(obj)
        except (ValueError, TypeError):
            pass
    # Fallback
    return str(obj)


def _compress_dataframe(df):
    """Compress a DataFrame to a small JSON-friendly summary.

    Instead of serializing every row (252 rows for 1yr of daily data),
    store only: column names, row count, last 5 rows, and basic stats.
    """
    try:
        tail = df.tail(5)
        summary = {
            "_type": "DataFrame_summary",
            "rows": len(df),
            "columns": list(df.columns),
            "last_5": {},
        }
        for col in tail.columns:
            summary["last_5"][str(col)] = [
                _make_serializable(v) for v in tail[col].tolist()
            ]
        # Add basic stats for numeric columns
        numeric = df.select_dtypes(include=["number"])
        if not numeric.empty:
            summary["latest"] = {
                str(col): _make_serializable(numeric[col].iloc[-1])
                for col in numeric.columns
            }
        return summary
    except Exception:
        return {"_type": "DataFrame_summary", "rows": len(df), "error": "compression failed"}


def _safe_num(val, fmt=None):
    """Format a number safely, handling None and various types."""
    if val is None:
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)
    if fmt == '$':
        return f"{val:,.2f}"
    elif fmt == 'int':
        return f"{int(val):,}"
    elif abs(val) >= 1e6:
        return _fmt_large_num(val)
    return f"{val:.2f}" if abs(val) < 100 else f"{val:,.2f}"


def _fmt_pct(val):
    """Format a percentage value."""
    if val is None:
        return "N/A"
    try:
        pct = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(pct) < 1:
        pct *= 100
    return f"{pct:.2f}%"


def _fmt_large_num(val):
    """Format large numbers (market cap, revenue, etc.)."""
    if val is None:
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)
    if abs(val) >= 1e12:
        return f"${val/1e12:.2f}T"
    elif abs(val) >= 1e9:
        return f"${val/1e9:.2f}B"
    elif abs(val) >= 1e6:
        return f"${val/1e6:.1f}M"
    elif abs(val) >= 1e3:
        return f"${val/1e3:.1f}K"
    return f"${val:,.2f}"


# ═══════════════════════════════════════════════════════════════════════
#  CLI — List/view cached data
# ═══════════════════════════════════════════════════════════════════════

def main():
    """CLI for inspecting cached data."""
    import argparse
    parser = argparse.ArgumentParser(description="Data Cache Manager")
    parser.add_argument("command", choices=["list", "view", "path"],
                        help="list: show today's cached tickers; view: print .md; path: show file path")
    parser.add_argument("ticker", nargs="?", help="Ticker symbol (for view/path)")
    parser.add_argument("--day", help="Date to check (YYYY-MM-DD, default: today)")
    args = parser.parse_args()

    if args.command == "list":
        tickers = list_cached_tickers(args.day)
        if tickers:
            print(f"Cached tickers for {args.day or _today_str()}: {', '.join(tickers)}")
        else:
            print(f"No cached data for {args.day or _today_str()}")

    elif args.command == "view":
        if not args.ticker:
            print("Usage: python scripts/data_cache.py view AAPL")
            return
        path = _md_path(args.ticker, args.day)
        if os.path.exists(path):
            with open(path) as f:
                print(f.read())
        else:
            print(f"No cached data for {args.ticker.upper()} on {args.day or _today_str()}")

    elif args.command == "path":
        if not args.ticker:
            print("Usage: python scripts/data_cache.py path AAPL")
            return
        print(_md_path(args.ticker, args.day))


if __name__ == "__main__":
    main()
