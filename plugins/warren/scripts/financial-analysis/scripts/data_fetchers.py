"""
Data Fetchers — Actual API implementations for every data source.

Each function returns a standardized dict. All functions are designed to be
passed to call_api() or call_with_fallback() as the fetch_fn argument.

Usage:
    from scripts.api_caller import call_with_fallback
    from scripts.data_fetchers import FETCHERS

    result = call_with_fallback("price_history", {
        api_id: (lambda t=ticker: fn(t)) for api_id, fn in FETCHERS["price_history"].items()
    })
"""
import os, sys, json
from datetime import datetime, timedelta

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.api_config import get_api_key, API_REGISTRY


# ═══════════════════════════════════════════════════════════════════
#  PRICE HISTORY
# ═══════════════════════════════════════════════════════════════════

def yfinance_price_history(ticker, period="1y", interval="1d"):
    """Get OHLCV price history from yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval=interval)
    if hist.empty:
        raise ValueError(f"No price data for {ticker}")
    return {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "data": hist,
        "latest_close": float(hist["Close"].iloc[-1]),
        "latest_volume": int(hist["Volume"].iloc[-1]),
        "records": len(hist),
    }


def polygon_price_history(ticker, days=365):
    """Get OHLCV from Polygon.io."""
    import requests
    key = get_api_key("polygon")
    if not key:
        raise ValueError("Polygon API key not configured")
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    r = requests.get(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}",
        params={"apiKey": key, "adjusted": "true", "sort": "asc", "limit": 5000},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if data.get("resultsCount", 0) == 0:
        raise ValueError(f"No Polygon data for {ticker}")
    bars = data["results"]
    latest_close = float(bars[-1]["c"])  # Polygon uses "c" for close
    return {"ticker": ticker, "results": bars, "records": data["resultsCount"],
            "latest_close": latest_close, "latest_volume": int(bars[-1].get("v", 0))}


def alpha_vantage_price_history(ticker):
    """Get daily prices from Alpha Vantage."""
    import requests
    key = get_api_key("alpha_vantage")
    if not key:
        raise ValueError("Alpha Vantage API key not configured")
    r = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "TIME_SERIES_DAILY", "symbol": ticker, "outputsize": "compact", "apikey": key},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if "Time Series (Daily)" not in data:
        raise ValueError(f"AV error: {data.get('Note', data.get('Error Message', 'Unknown'))}")
    ts = data["Time Series (Daily)"]
    latest_date = sorted(ts.keys())[-1]
    latest_close = float(ts[latest_date]["4. close"])
    return {"ticker": ticker, "time_series": ts,
            "latest_close": latest_close}


def fmp_price_history(ticker):
    """Get daily prices from FMP stable endpoint."""
    import requests
    key = get_api_key("fmp")
    if not key:
        raise ValueError("FMP API key not configured")
    r = requests.get(
        f"https://financialmodelingprep.com/stable/historical-price-eod/full?symbol={ticker}&apikey={key}",
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No FMP price data for {ticker}")
    # FMP returns a list of dicts sorted newest first, each with "close"
    if isinstance(data, list) and len(data) > 0:
        latest_close = float(data[0].get("close", data[0].get("adjClose", 0)))
    elif isinstance(data, dict):
        latest_close = float(data.get("close", data.get("adjClose", 0)))
    else:
        latest_close = 0
    return {"ticker": ticker, "data": data, "latest_close": latest_close}


# ═══════════════════════════════════════════════════════════════════
#  FUNDAMENTALS / FINANCIAL STATEMENTS
# ═══════════════════════════════════════════════════════════════════

# Hardcoded sector map for tickers that yfinance commonly misclassifies
# (CEFs, ADRs, foreign-listed, unusual quoteTypes).  Extend as needed.
_TICKER_SECTOR_OVERRIDE = {
    # Closed-end funds
    "RQI": "Real Estate",
    # Fixed-income ETFs
    "ANGL": "Fixed Income",
    "BLV": "Fixed Income",
    # Index ETFs
    "VOO": "Broad Market",
    "QQQM": "Technology",
    "SPY": "Broad Market",
    "QQQ": "Technology",
    "VTI": "Broad Market",
    "IVV": "Broad Market",
    "SCHD": "Broad Market",
    # Foreign ADRs where yfinance returns no sector
    "IDEXY": "Industrials",   # Industria de Diseño Textil (Inditex)
    "PPERY": "Consumer Cyclical",  # PT Telekomunikasi / Puma
    "CA": "Technology",       # CAE Inc. (flight simulation / defense)
}


def _classify_etf_sector(category):
    """Map yfinance ETF category string to a sector name."""
    c = category.lower()
    # Technology / Growth
    if any(k in c for k in ("technology", "nasdaq", "semiconductor", "software")):
        return "Technology"
    # Financials
    if any(k in c for k in ("financial", "bank", "insurance")):
        return "Financial Services"
    # Energy
    if any(k in c for k in ("energy", "oil", "gas", "petroleum", "mlp")):
        return "Energy"
    # Healthcare
    if any(k in c for k in ("health", "biotech", "pharma")):
        return "Healthcare"
    # Real Estate
    if any(k in c for k in ("real estate", "reit", "realty")):
        return "Real Estate"
    # Utilities
    if any(k in c for k in ("utilities",)):
        return "Utilities"
    # Consumer
    if any(k in c for k in ("consumer defensive", "consumer staples")):
        return "Consumer Defensive"
    if any(k in c for k in ("consumer cyclical", "consumer discretionary", "retail")):
        return "Consumer Cyclical"
    # Industrials
    if any(k in c for k in ("industrial", "aerospace", "defense")):
        return "Industrials"
    # Communication
    if any(k in c for k in ("communication", "media", "telecom")):
        return "Communication Services"
    # Materials
    if any(k in c for k in ("material", "mining", "metals", "chemical")):
        return "Basic Materials"
    # Fixed income
    if any(k in c for k in ("bond", "fixed income", "income", "treasury", "corporate bond",
                              "high yield", "credit", "debt", "aggregate")):
        return "Fixed Income"
    # Broad market / blend
    if any(k in c for k in ("large blend", "large growth", "large value", "mid-cap", "small",
                              "total market", "s&p 500", "blend", "index", "diversified")):
        return "Broad Market"
    # Fallback
    return "Other"


def yfinance_fundamentals(ticker):
    """Get company info, financials, and key metrics from yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    info = t.info
    if not info or not isinstance(info, dict) or len(info) < 5:
        raise ValueError(f"No yfinance info for {ticker}")
    # Accept any info dict that has at least some useful fields
    has_useful = any(info.get(k) for k in ("marketCap", "currentPrice", "previousClose", "totalRevenue"))
    if not has_useful:
        raise ValueError(f"yfinance info for {ticker} has no useful financial data")
    # For ETFs/funds, sector is empty — try multiple fallbacks
    sector = info.get("sector", "")
    if not sector:
        # 1. Check hardcoded override map (CEFs, ADRs, etc.)
        if ticker.upper() in _TICKER_SECTOR_OVERRIDE:
            sector = _TICKER_SECTOR_OVERRIDE[ticker.upper()]
        else:
            # 2. Try yfinance category field
            category = (info.get("category") or "").lower()
            quote_type = (info.get("quoteType") or "").upper()
            if category:
                sector = _classify_etf_sector(category)
            # 3. Try classifying from fund name (e.g. "Vanguard Real Estate ETF")
            elif not sector:
                long_name = (info.get("longName") or info.get("shortName") or "").lower()
                if long_name:
                    sector = _classify_etf_sector(long_name)
                    if sector == "Other" and quote_type in ("ETF", "MUTUALFUND"):
                        sector = "Broad Market"
                elif quote_type in ("ETF", "MUTUALFUND"):
                    sector = "Broad Market"

    return {
        "ticker": ticker,
        "name": info.get("longName", ""),
        "sector": sector,
        "industry": info.get("industry", ""),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "pb_ratio": info.get("priceToBook"),
        "ps_ratio": info.get("priceToSalesTrailing12Months"),
        "dividend_yield": info.get("dividendYield"),
        "beta": info.get("beta"),
        "eps": info.get("trailingEps"),
        "revenue": info.get("totalRevenue"),
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),
        "profit_margin": info.get("profitMargins"),
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins"),
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "debt_to_equity": info.get("debtToEquity"),
        "free_cash_flow": info.get("freeCashflow"),
        "target_mean_price": info.get("targetMeanPrice"),
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
        "recommendation": info.get("recommendationKey"),
        "num_analysts": info.get("numberOfAnalystOpinions"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "50d_avg": info.get("fiftyDayAverage"),
        "200d_avg": info.get("twoHundredDayAverage"),
    }


def sec_edgar_filings(ticker):
    """Get recent SEC filings for a company."""
    import requests
    # First get CIK from ticker
    r = requests.get(
        "https://efts.sec.gov/LATEST/search-index?q=%22" + ticker + "%22&dateRange=custom&startdt=2020-01-01&forms=10-K,10-Q",
        headers={"User-Agent": "FinancialAnalysisSkill contact@example.com"},
        timeout=10,
    )
    # Use the ticker-to-CIK mapping
    r2 = requests.get(
        "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK=" + ticker + "&type=10-K&dateb=&owner=include&count=5&search_text=&action=getcompany",
        headers={"User-Agent": "FinancialAnalysisSkill contact@example.com"},
        timeout=10,
    )
    # Simpler approach: use the company tickers JSON
    tickers_r = requests.get(
        "https://www.sec.gov/files/company_tickers.json",
        headers={"User-Agent": "FinancialAnalysisSkill contact@example.com"},
        timeout=10,
    )
    tickers_r.raise_for_status()
    tickers_data = tickers_r.json()
    cik = None
    for entry in tickers_data.values():
        if entry.get("ticker", "").upper() == ticker.upper():
            cik = str(entry["cik_str"]).zfill(10)
            break
    if not cik:
        raise ValueError(f"CIK not found for {ticker}")
    # Get submissions
    sub_r = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers={"User-Agent": "FinancialAnalysisSkill contact@example.com"},
        timeout=10,
    )
    sub_r.raise_for_status()
    data = sub_r.json()
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    urls = recent.get("primaryDocument", [])
    accessions = recent.get("accessionNumber", [])
    filings = []
    for i in range(min(20, len(forms))):
        filings.append({
            "form": forms[i],
            "date": dates[i],
            "accession": accessions[i] if i < len(accessions) else "",
        })
    return {
        "ticker": ticker,
        "cik": cik,
        "company_name": data.get("name", ""),
        "recent_filings": filings,
    }


def finnhub_financials(ticker):
    """Get basic financials from Finnhub."""
    import requests
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    r = requests.get(
        f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    metrics = data.get("metric", {})
    if not metrics:
        raise ValueError(f"No Finnhub metrics for {ticker}")
    return {"ticker": ticker, "metrics": metrics, "series": data.get("series", {})}


def fmp_fundamentals(ticker):
    """Get company profile from FMP stable endpoint."""
    import requests
    key = get_api_key("fmp")
    if not key:
        raise ValueError("FMP API key not configured")
    r = requests.get(
        f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No FMP data for {ticker}")
    return {"ticker": ticker, "profile": data[0] if isinstance(data, list) else data}


# ═══════════════════════════════════════════════════════════════════
#  ANALYST RATINGS
# ═══════════════════════════════════════════════════════════════════

def finnhub_analyst_ratings(ticker):
    """Get analyst recommendations from Finnhub."""
    import requests
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    r = requests.get(
        f"https://finnhub.io/api/v1/stock/recommendation?symbol={ticker}&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError(f"No recommendations for {ticker}")
    latest = data[0]
    return {
        "ticker": ticker,
        "buy": latest.get("buy", 0),
        "hold": latest.get("hold", 0),
        "sell": latest.get("sell", 0),
        "strong_buy": latest.get("strongBuy", 0),
        "strong_sell": latest.get("strongSell", 0),
        "period": latest.get("period", ""),
        "history": data[:6],
    }


def yfinance_analyst_ratings(ticker):
    """Get analyst recommendations from yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    recs = t.recommendations
    if recs is None or recs.empty:
        raise ValueError(f"No yfinance recommendations for {ticker}")
    latest = recs.iloc[-1]
    return {
        "ticker": ticker,
        "firm": latest.get("Firm", ""),
        "grade": latest.get("To Grade", latest.get("toGrade", "")),
        "action": latest.get("Action", latest.get("action", "")),
        "total_recommendations": len(recs),
    }


def seeking_alpha_ratings(ticker):
    """Get quant ratings from Seeking Alpha RapidAPI."""
    import requests
    key = get_api_key("seeking_alpha_rapidapi")
    if not key:
        raise ValueError("Seeking Alpha RapidAPI key not configured")
    r = requests.get(
        "https://seeking-alpha.p.rapidapi.com/symbols/get-ratings",
        params={"symbol": ticker},
        headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "seeking-alpha.p.rapidapi.com"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return {"ticker": ticker, "ratings": data}


# ═══════════════════════════════════════════════════════════════════
#  INSIDER & CONGRESS TRADES
# ═══════════════════════════════════════════════════════════════════

def sec_insider_trades(ticker):
    """Get insider transactions from SEC EDGAR."""
    import requests
    # Use Finnhub for insider sentiment (easier than parsing EDGAR forms)
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    r = requests.get(
        f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json().get("data", [])
    buys = sum(1 for t in data[:50] if t.get("transactionType", "").lower() in ("p", "purchase", "buy"))
    sells = sum(1 for t in data[:50] if t.get("transactionType", "").lower() in ("s", "sale", "sell"))
    return {
        "ticker": ticker,
        "recent_transactions": data[:20],
        "buys_last_50": buys,
        "sells_last_50": sells,
        "net_insider_signal": "bullish" if buys > sells else ("bearish" if sells > buys else "neutral"),
    }


def finnhub_insider_sentiment(ticker):
    """Get insider sentiment from Finnhub."""
    import requests
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    r = requests.get(
        f"https://finnhub.io/api/v1/stock/insider-sentiment?symbol={ticker}&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json().get("data", [])
    return {"ticker": ticker, "insider_sentiment": data[:12]}


def mboum_congress_trades(ticker=None):
    """Get Congress trading data from Mboum."""
    import requests
    key = get_api_key("mboum")
    if not key:
        raise ValueError("Mboum API key not configured")
    url = "https://mboum-finance.p.rapidapi.com/v1/markets/congress-trading"
    params = {}
    if ticker:
        params["symbol"] = ticker
    r = requests.get(
        url, params=params,
        headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "mboum-finance.p.rapidapi.com"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return {"ticker": ticker, "congress_trades": data}


# ═══════════════════════════════════════════════════════════════════
#  NEWS & SENTIMENT
# ═══════════════════════════════════════════════════════════════════

def finnhub_news_sentiment(ticker):
    """Get company news from Finnhub."""
    import requests
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    r = requests.get(
        f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={week_ago}&to={today}&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    articles = r.json()
    if not articles:
        return {"ticker": ticker, "articles": [], "avg_sentiment": 0, "article_count": 0}
    # Finnhub doesn't provide sentiment scores in free tier, but we get headlines
    return {
        "ticker": ticker,
        "articles": articles[:20],
        "article_count": len(articles),
        "sources": list(set(a.get("source", "") for a in articles)),
    }


def alpha_vantage_news_sentiment(ticker):
    """Get AI-scored news sentiment from Alpha Vantage."""
    import requests
    key = get_api_key("alpha_vantage")
    if not key:
        raise ValueError("Alpha Vantage API key not configured")
    r = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "NEWS_SENTIMENT", "tickers": ticker, "limit": 20, "apikey": key},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if "feed" not in data:
        raise ValueError(f"AV news error: {data.get('Note', data.get('Error Message', 'Unknown'))}")
    feed = data["feed"]
    # Extract per-ticker sentiment from each article
    sentiments = []
    for article in feed:
        for ts in article.get("ticker_sentiment", []):
            if ts.get("ticker", "").upper() == ticker.upper():
                score = float(ts.get("ticker_sentiment_score", 0))
                sentiments.append(score)
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return {
        "ticker": ticker,
        "articles": feed[:10],
        "sentiment_scores": sentiments,
        "avg_sentiment": avg_sentiment,  # -1 to +1
        "article_count": len(feed),
    }


def apewisdom_reddit_sentiment(ticker=None):
    """Get Reddit trending stocks from ApeWisdom."""
    import requests
    r = requests.get("https://apewisdom.io/api/v1.0/filter/all-stocks/page/1", timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if ticker:
        for stock in results:
            if stock.get("ticker", "").upper() == ticker.upper():
                return {
                    "ticker": ticker,
                    "rank": stock.get("rank"),
                    "mentions": stock.get("mentions", 0),
                    "mentions_24h_ago": stock.get("mentions_24h_ago", 0),
                    "upvotes": stock.get("upvotes", 0),
                }
        return {"ticker": ticker, "rank": None, "mentions": 0, "mentions_24h_ago": 0, "upvotes": 0}
    return {"top_stocks": results[:30]}


def stocktwits_sentiment(ticker):
    """Get StockTwits sentiment for a ticker."""
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Accept": "application/json",
    }
    r = requests.get(
        f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json",
        headers=headers,
        timeout=15,
    )
    if r.status_code in (403, 429):
        raise ValueError(f"StockTwits returned {r.status_code} — rate limited or access restricted")
    r.raise_for_status()
    data = r.json()
    messages = data.get("messages", [])
    if not messages:
        raise ValueError(f"StockTwits returned no messages for {ticker}")
    bullish = sum(1 for m in messages if m.get("entities", {}).get("sentiment", {}).get("basic") == "Bullish")
    bearish = sum(1 for m in messages if m.get("entities", {}).get("sentiment", {}).get("basic") == "Bearish")
    total_with_sentiment = bullish + bearish
    bull_pct = (bullish / total_with_sentiment * 100) if total_with_sentiment > 0 else 50
    return {
        "ticker": ticker,
        "messages_count": len(messages),
        "bullish": bullish,
        "bearish": bearish,
        "bull_pct": round(bull_pct, 1),
        "bear_pct": round(100 - bull_pct, 1),
    }


# ═══════════════════════════════════════════════════════════════════
#  EARNINGS & DIVIDENDS
# ═══════════════════════════════════════════════════════════════════

def finnhub_earnings(ticker):
    """Get earnings calendar/surprises from Finnhub."""
    import requests
    key = get_api_key("finnhub")
    if not key:
        raise ValueError("Finnhub API key not configured")
    r = requests.get(
        f"https://finnhub.io/api/v1/stock/earnings?symbol={ticker}&token={key}",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        return {"ticker": ticker, "earnings": [], "surprise_avg": 0}
    surprises = [e.get("surprisePercent", 0) for e in data if e.get("surprisePercent") is not None]
    return {
        "ticker": ticker,
        "earnings": data[:8],
        "surprise_avg": sum(surprises) / len(surprises) if surprises else 0,
        "beat_count": sum(1 for s in surprises if s > 0),
        "miss_count": sum(1 for s in surprises if s < 0),
    }


def yfinance_earnings(ticker):
    """Get earnings data from yfinance (fallback for Finnhub)."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    earnings = t.earnings_history
    if earnings is None or (hasattr(earnings, 'empty') and earnings.empty):
        # Try quarterly earnings instead
        qe = t.quarterly_earnings
        if qe is None or (hasattr(qe, 'empty') and qe.empty):
            raise ValueError(f"No yfinance earnings data for {ticker}")
        # Convert quarterly earnings to standard format
        records = []
        for idx, row in qe.iterrows():
            actual = row.get("Earnings", row.get("Revenue", 0))
            estimate = row.get("Estimate", 0)
            surprise = ((actual - estimate) / abs(estimate) * 100) if estimate else 0
            records.append({"period": str(idx), "actual": actual, "estimate": estimate, "surprisePercent": surprise})
        surprises = [r["surprisePercent"] for r in records if r["surprisePercent"] != 0]
        return {
            "ticker": ticker,
            "earnings": records[:8],
            "surprise_avg": sum(surprises) / len(surprises) if surprises else 0,
            "beat_count": sum(1 for s in surprises if s > 0),
            "miss_count": sum(1 for s in surprises if s < 0),
        }
    # earnings_history is a DataFrame with epsActual, epsEstimate, epsDifference, surprisePercent
    records = []
    for idx, row in earnings.iterrows():
        records.append({
            "period": str(idx),
            "actual": row.get("epsActual"),
            "estimate": row.get("epsEstimate"),
            "surprisePercent": row.get("surprisePercent", 0),
        })
    surprises = [r["surprisePercent"] for r in records if r.get("surprisePercent") is not None and r["surprisePercent"] != 0]
    return {
        "ticker": ticker,
        "earnings": records[:8],
        "surprise_avg": sum(surprises) / len(surprises) if surprises else 0,
        "beat_count": sum(1 for s in surprises if s > 0),
        "miss_count": sum(1 for s in surprises if s < 0),
    }


def yfinance_dividends(ticker):
    """Get dividend info from yfinance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    divs = t.dividends
    info = t.info
    return {
        "ticker": ticker,
        "dividend_yield": info.get("dividendYield"),
        "dividend_rate": info.get("dividendRate"),
        "payout_ratio": info.get("payoutRatio"),
        "ex_dividend_date": info.get("exDividendDate"),
        "recent_dividends": divs.tail(8).to_dict() if divs is not None and not divs.empty else {},
    }


# ═══════════════════════════════════════════════════════════════════
#  TRADINGVIEW CONSENSUS
# ═══════════════════════════════════════════════════════════════════

def _detect_exchange(ticker):
    """Try to detect the exchange for a ticker using yfinance."""
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info or {}
        exch = info.get("exchange", "")
        # Map yfinance exchange names to TradingView names
        exchange_map = {
            "NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ", "NASDAQ": "NASDAQ",
            "NYQ": "NYSE", "NYSE": "NYSE", "NYS": "NYSE",
            "ASE": "AMEX", "AMEX": "AMEX",
            "PCX": "NYSE",  # NYSE Arca
            "BTS": "NYSE",  # BATS → use NYSE
        }
        mapped = exchange_map.get(exch.upper(), "")
        if mapped:
            return mapped
    except Exception:
        pass
    return None


def tradingview_consensus(ticker, exchange=None):
    """
    Get TradingView technical analysis consensus (26 indicators).
    Auto-detects exchange using yfinance, then falls back to trying
    NASDAQ → NYSE → AMEX.
    """
    try:
        from tradingview_ta import TA_Handler, Interval
    except ImportError:
        raise ImportError("tradingview-ta not installed: pip install tradingview-ta")

    # Build exchange list: user-specified > auto-detected > brute-force
    exchanges = []
    if exchange:
        exchanges.append(exchange)
    else:
        detected = _detect_exchange(ticker)
        if detected:
            exchanges.append(detected)
        # Always append the full list as fallback (deduped)
        for exch in ["NASDAQ", "NYSE", "AMEX"]:
            if exch not in exchanges:
                exchanges.append(exch)

    analysis = None
    last_error = None

    for exch in exchanges:
        try:
            handler = TA_Handler(
                symbol=ticker,
                screener="america",
                exchange=exch,
                interval=Interval.INTERVAL_1_DAY,
            )
            analysis = handler.get_analysis()
            # Verify we got actual data (not an empty/broken response)
            if analysis and analysis.summary and analysis.summary.get("RECOMMENDATION"):
                exchange = exch
                break
            else:
                last_error = f"{exch}: got response but no recommendation"
                analysis = None
        except Exception as e:
            last_error = f"{exch}: {type(e).__name__}: {e}"
            analysis = None
            continue

    if analysis is None:
        raise ValueError(f"TradingView: {ticker} not found on {exchanges}. Last error: {last_error}")
    summary = analysis.summary
    indicators = analysis.indicators
    oscillators = analysis.oscillators
    moving_averages = analysis.moving_averages
    return {
        "ticker": ticker,
        "interval": "1d",
        "recommendation": summary.get("RECOMMENDATION", ""),  # STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
        "buy_count": summary.get("BUY", 0),
        "sell_count": summary.get("SELL", 0),
        "neutral_count": summary.get("NEUTRAL", 0),
        "oscillators": {
            "recommendation": oscillators.get("RECOMMENDATION", ""),
            "buy": oscillators.get("BUY", 0),
            "sell": oscillators.get("SELL", 0),
            "neutral": oscillators.get("NEUTRAL", 0),
        },
        "moving_averages": {
            "recommendation": moving_averages.get("RECOMMENDATION", ""),
            "buy": moving_averages.get("BUY", 0),
            "sell": moving_averages.get("SELL", 0),
            "neutral": moving_averages.get("NEUTRAL", 0),
        },
        "rsi": indicators.get("RSI"),
        "macd": indicators.get("MACD.macd"),
        "macd_signal": indicators.get("MACD.signal"),
        "ema_20": indicators.get("EMA20"),
        "sma_50": indicators.get("SMA50"),
        "sma_200": indicators.get("SMA200"),
        "adx": indicators.get("ADX"),
        "atr": indicators.get("ATR"),
        "bbands_upper": indicators.get("BB.upper"),
        "bbands_lower": indicators.get("BB.lower"),
        "volume": indicators.get("volume"),
    }


# ═══════════════════════════════════════════════════════════════════
#  FETCHER REGISTRY — maps data categories to {api_id: fetch_fn}
# ═══════════════════════════════════════════════════════════════════

def get_fetchers(ticker):
    """
    Return a dict mapping each data category to its available fetchers.
    Each fetcher is a zero-arg callable (ticker is pre-bound).

    Usage:
        fetchers = get_fetchers("AAPL")
        result = call_with_fallback("price_history", fetchers["price_history"])
    """
    return {
        "price_history": {
            "yfinance": lambda: yfinance_price_history(ticker),
            "polygon": lambda: polygon_price_history(ticker),
            "alpha_vantage": lambda: alpha_vantage_price_history(ticker),
            "fmp": lambda: fmp_price_history(ticker),
        },
        "fundamentals": {
            "yfinance": lambda: yfinance_fundamentals(ticker),
            "sec_edgar": lambda: sec_edgar_filings(ticker),
            "finnhub": lambda: finnhub_financials(ticker),
            "fmp": lambda: fmp_fundamentals(ticker),
        },
        "analyst_ratings": {
            "finnhub": lambda: finnhub_analyst_ratings(ticker),
            "yfinance": lambda: yfinance_analyst_ratings(ticker),
            "seeking_alpha_rapidapi": lambda: seeking_alpha_ratings(ticker),
        },
        "insider_trades": {
            "finnhub": lambda: sec_insider_trades(ticker),
        },
        "insider_sentiment": {
            "finnhub": lambda: finnhub_insider_sentiment(ticker),
        },
        "congress_trades": {
            "mboum": lambda: mboum_congress_trades(ticker),
        },
        "news_sentiment": {
            "finnhub": lambda: finnhub_news_sentiment(ticker),
            "alpha_vantage": lambda: alpha_vantage_news_sentiment(ticker),
        },
        "reddit_sentiment": {
            "apewisdom": lambda: apewisdom_reddit_sentiment(ticker),
        },
        "social_sentiment": {
            "stocktwits": lambda: stocktwits_sentiment(ticker),
            # Removed apewisdom from social_sentiment to avoid overlap with reddit_sentiment
        },
        "earnings": {
            "finnhub": lambda: finnhub_earnings(ticker),
            "yfinance": lambda: yfinance_earnings(ticker),
        },
        "dividends": {
            "yfinance": lambda: yfinance_dividends(ticker),
        },
        "tradingview": {
            "tradingview": lambda: tradingview_consensus(ticker),
        },
    }
