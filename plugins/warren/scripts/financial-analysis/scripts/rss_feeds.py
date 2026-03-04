"""
RSS Feed Aggregator for Financial Analysis Skill.
Parses 20+ financial RSS feeds, extracts mentioned tickers, and ranks by relevance.

Usage:
    from scripts.rss_feeds import scan_all_feeds, scan_ticker_feeds
    ideas = scan_all_feeds()           # Scan all Tier 1+2 feeds
    articles = scan_ticker_feeds("AAPL")  # Seeking Alpha per-ticker feed
"""
import re
from datetime import datetime, timedelta

# ─── FEED CATALOG ─────────────────────────────────────────────
FEEDS = {
    # TIER 1 — Primary feeds (scan daily)
    "nasdaq_original":      {"url": "https://www.nasdaq.com/feed/nasdaq-original/rss.xml", "tier": 1, "source": "Nasdaq"},
    "nasdaq_stocks":        {"url": "https://www.nasdaq.com/feed/rssoutbound?category=Stocks", "tier": 1, "source": "Nasdaq"},
    "cnbc_top":             {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "tier": 1, "source": "CNBC"},
    "cnbc_finance":         {"url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", "tier": 1, "source": "CNBC"},
    "marketwatch_top":      {"url": "https://feeds.marketwatch.com/marketwatch/topstories/", "tier": 1, "source": "MarketWatch"},
    "marketwatch_pulse":    {"url": "https://feeds.marketwatch.com/marketwatch/marketpulse/", "tier": 1, "source": "MarketWatch"},
    "seeking_alpha_main":   {"url": "https://seekingalpha.com/feed.xml", "tier": 1, "source": "Seeking Alpha"},
    "seeking_alpha_currents": {"url": "https://seekingalpha.com/market_currents.xml", "tier": 1, "source": "Seeking Alpha"},
    "benzinga":             {"url": "https://www.benzinga.com/feed", "tier": 1, "source": "Benzinga"},

    # TIER 2 — Supplementary feeds
    "yahoo_finance":        {"url": "https://finance.yahoo.com/news/rssindex", "tier": 2, "source": "Yahoo Finance"},
    "investing_com":        {"url": "https://www.investing.com/rss/news.rss", "tier": 2, "source": "Investing.com"},
    "motley_fool":          {"url": "https://www.fool.com/feeds/index.aspx?id=foolwatch&format=rss2", "tier": 2, "source": "Motley Fool"},
    "motley_fool_movers":   {"url": "https://www.fool.com/feeds/index.aspx?id=market-movers&format=rss2", "tier": 2, "source": "Motley Fool"},
    "thestreet":            {"url": "https://www.thestreet.com/.rss/full/", "tier": 2, "source": "TheStreet"},
    "zacks":                {"url": "https://scr.zacks.com/distribution/rss-feeds/default.aspx", "tier": 2, "source": "Zacks"},
    "stocktwits_rss":       {"url": "https://stocktwits.com/sitemap/rss_feed.xml", "tier": 2, "source": "StockTwits"},

    # TIER 3 — Specialized
    "barrons":              {"url": "https://www.barrons.com/market-data/rss", "tier": 3, "source": "Barron's"},
    "investinglive":        {"url": "https://investinglive.com/rss/", "tier": 3, "source": "investingLive"},
}

# Common US stock ticker pattern (1-5 uppercase letters)
TICKER_PATTERN = re.compile(r'\b([A-Z]{1,5})\b')

# Words that look like tickers but aren't
TICKER_BLACKLIST = {
    "A", "I", "AM", "PM", "THE", "AND", "FOR", "ARE", "BUT", "NOT",
    "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY",
    "HAD", "HAS", "HIS", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE",
    "WAY", "WHO", "BOY", "DID", "GET", "HIM", "LET", "SAY", "SHE",
    "TOO", "USE", "CEO", "CFO", "CTO", "IPO", "ETF", "GDP", "SEC",
    "FBI", "FED", "NYSE", "NASDAQ", "DJ", "SP", "US", "USA", "UK",
    "EU", "AI", "IT", "CEO", "VS", "EST", "PST", "EDT", "RSS",
    "API", "GDP", "CPI", "PPI", "PMI", "NFP", "FOMC", "FTC", "DOJ",
    "EPS", "PE", "PB", "PS", "ROE", "ROA", "DCF", "FCF", "YOY",
    "QOQ", "MOM", "HOD", "LOD", "ATH", "ATL", "MACD", "RSI",
    "SMA", "EMA", "OTC", "AH", "PM", "NEWS", "TOP", "BIG",
    "UP", "DOWN", "HIGH", "LOW", "BUY", "SELL", "HOLD", "CALL",
    "PUT", "LONG", "SHORT", "BULL", "BEAR", "IPO", "M&A",
}


def parse_feed(feed_id, max_age_hours=24):
    """Parse a single RSS feed and return list of article dicts.

    The caller is responsible for having feedparser installed
    (pip install feedparser).
    """
    import feedparser
    feed_meta = FEEDS.get(feed_id)
    if not feed_meta:
        return []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    feed = feedparser.parse(feed_meta["url"])
    articles = []
    for entry in feed.entries[:50]:  # cap at 50 per feed
        pub_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            pub_date = datetime(*entry.updated_parsed[:6])
        if pub_date and pub_date < cutoff:
            continue
        title = getattr(entry, "title", "")
        summary = getattr(entry, "summary", "")
        link = getattr(entry, "link", "")
        text = f"{title} {summary}"
        tickers = extract_tickers(text)
        articles.append({
            "feed_id": feed_id,
            "source": feed_meta["source"],
            "tier": feed_meta["tier"],
            "title": title,
            "summary": summary[:500],
            "link": link,
            "published": pub_date.isoformat() if pub_date else None,
            "tickers_mentioned": tickers,
        })
    return articles


def extract_tickers(text):
    """Extract likely stock tickers from text, filtering out common words."""
    matches = TICKER_PATTERN.findall(text)
    return list(set(t for t in matches if t not in TICKER_BLACKLIST and len(t) >= 2))


def scan_all_feeds(tiers=None, max_age_hours=24):
    """Scan all feeds (or specific tiers) and return aggregated results.

    Args:
        tiers: List of tiers to scan, e.g. [1, 2]. Default: [1, 2]
        max_age_hours: Only include articles from last N hours

    Returns:
        {
            "articles": [...],
            "ticker_mentions": {ticker: count},
            "top_tickers": [(ticker, count), ...],
            "feeds_scanned": int,
            "articles_found": int,
        }
    """
    tiers = tiers or [1, 2]
    all_articles = []
    ticker_counts = {}

    for feed_id, meta in FEEDS.items():
        if meta["tier"] not in tiers:
            continue
        try:
            articles = parse_feed(feed_id, max_age_hours)
            all_articles.extend(articles)
            for a in articles:
                for t in a.get("tickers_mentioned", []):
                    ticker_counts[t] = ticker_counts.get(t, 0) + 1
        except Exception as e:
            print(f"Warning: Failed to parse {feed_id}: {e}")
            continue

    top = sorted(ticker_counts.items(), key=lambda x: -x[1])
    return {
        "articles": all_articles,
        "ticker_mentions": ticker_counts,
        "top_tickers": top[:30],
        "feeds_scanned": sum(1 for f in FEEDS.values() if f["tier"] in tiers),
        "articles_found": len(all_articles),
    }


def scan_ticker_feeds(ticker, max_age_hours=72):
    """Get Seeking Alpha per-ticker articles via RSS."""
    import feedparser
    url = f"https://seekingalpha.com/api/sa/combined/{ticker}.xml"
    feed = feedparser.parse(url)
    articles = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    for entry in feed.entries[:20]:
        pub_date = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        if pub_date and pub_date < cutoff:
            continue
        articles.append({
            "source": "Seeking Alpha",
            "ticker": ticker,
            "title": getattr(entry, "title", ""),
            "summary": getattr(entry, "summary", "")[:500],
            "link": getattr(entry, "link", ""),
            "published": pub_date.isoformat() if pub_date else None,
        })
    return articles
