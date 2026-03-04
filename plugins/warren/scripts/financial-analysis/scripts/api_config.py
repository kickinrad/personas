"""
API Configuration Manager for Financial Analysis Skill.
Handles API key storage, validation, free/paid tier tracking, and rate limit definitions.

Usage:
    from scripts.api_config import load_config, get_api_key, get_rate_limit, list_apis
"""
import json, os, sys
from pathlib import Path

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.financial-analysis/api_keys.json")
LOGS_DIR = os.path.expanduser("~/.financial-analysis/logs")

# ─── API REGISTRY ────────────────────────────────────────────
# Every API the skill uses, with tier/cost/limit metadata
API_REGISTRY = {
    "yfinance": {
        "name": "Yahoo Finance (yfinance)",
        "tier": "FREE",
        "cost": "Free (unofficial)",
        "requires_key": False,
        "rate_limit_per_minute": 5,       # self-imposed (avoid IP blocks)
        "rate_limit_per_day": 2000,       # self-imposed
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 2.0,
        "notes": "Unofficial scraper. Use batch requests + delays. No API key needed.",
    },
    "finnhub": {
        "name": "Finnhub",
        "tier": "FREE",
        "cost": "Free (60/min), paid $50/mo",
        "requires_key": True,
        "key_env_var": "FINNHUB_API_KEY",
        "key_url": "https://finnhub.io/register",
        "rate_limit_per_minute": 60,
        "rate_limit_per_day": 86400,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 1.0,
        "notes": "Free signup. 60 calls/min on free tier.",
    },
    "sec_edgar": {
        "name": "SEC EDGAR (Official)",
        "tier": "FREE",
        "cost": "Free (government)",
        "requires_key": False,
        "user_agent_required": True,
        "rate_limit_per_minute": 600,     # 10/sec
        "rate_limit_per_day": 864000,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 0.1,
        "notes": "Requires User-Agent header with email. 10 requests/sec max.",
    },
    "mboum": {
        "name": "Mboum Finance",
        "tier": "FREE",
        "cost": "Free (~600/mo), paid $9.95/mo",
        "requires_key": True,
        "key_env_var": "MBOUM_API_KEY",
        "key_url": "https://rapidapi.com/sparkhub-sparkhub-default/api/mboum-finance",
        "rate_limit_per_minute": None,
        "rate_limit_per_day": 20,
        "rate_limit_per_month": 600,
        "delay_between_calls_sec": 2.0,
        "notes": "Via RapidAPI. ~600 req/mo free. Budget carefully.",
    },
    "alpha_vantage": {
        "name": "Alpha Vantage",
        "tier": "FREE",
        "cost": "Free (25/day), paid $29.99/mo",
        "requires_key": True,
        "key_env_var": "ALPHA_VANTAGE_API_KEY",
        "key_url": "https://www.alphavantage.co/support/#api-key",
        "rate_limit_per_minute": 5,
        "rate_limit_per_day": 25,
        "rate_limit_per_month": 750,
        "delay_between_calls_sec": 12.0,  # 5/min = 12s between calls
        "notes": "25 calls/day free. Tightest constraint. Use sparingly.",
    },
    "seeking_alpha_rss": {
        "name": "Seeking Alpha (RSS)",
        "tier": "FREE",
        "cost": "Free (unlimited RSS)",
        "requires_key": False,
        "rate_limit_per_minute": 30,      # self-imposed
        "rate_limit_per_day": None,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 2.0,
        "notes": "RSS feeds are free and unlimited. Non-commercial use per ToS.",
    },
    "seeking_alpha_rapidapi": {
        "name": "Seeking Alpha (RapidAPI)",
        "tier": "FREE",
        "cost": "Free (~1K/mo), paid tiers available",
        "requires_key": True,
        "key_env_var": "SEEKING_ALPHA_RAPIDAPI_KEY",
        "key_url": "https://rapidapi.com/apidojo/api/seeking-alpha",
        "rate_limit_per_minute": None,
        "rate_limit_per_day": 33,         # ~1000/mo / 30
        "rate_limit_per_month": 1000,
        "delay_between_calls_sec": 2.0,
        "notes": "Unofficial API via APIDojo. Free 1K req/mo. Quant ratings + factor grades.",
    },
    "polygon": {
        "name": "Polygon.io (Massive)",
        "tier": "FREE",
        "cost": "Free (5/min), paid $29/mo",
        "requires_key": True,
        "key_env_var": "POLYGON_API_KEY",
        "key_url": "https://polygon.io/dashboard/signup",
        "rate_limit_per_minute": 5,
        "rate_limit_per_day": 7200,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 12.0,
        "notes": "5 req/min free. Good for EOD data backup.",
    },
    "alpaca": {
        "name": "Alpaca Markets",
        "tier": "FREE",
        "cost": "Free (200/min)",
        "requires_key": True,
        "key_env_var": "ALPACA_API_KEY",
        "key_secret_var": "ALPACA_API_SECRET",
        "key_url": "https://app.alpaca.markets/signup",
        "rate_limit_per_minute": 200,
        "rate_limit_per_day": None,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 0.3,
        "notes": "Free paper trading + news stream. 200/min. 15-min delayed quotes.",
    },
    "fmp": {
        "name": "Financial Modeling Prep",
        "tier": "FREE",
        "cost": "Free (250/day), paid $14/mo",
        "requires_key": True,
        "key_env_var": "FMP_API_KEY",
        "key_url": "https://financialmodelingprep.com/developer/docs/",
        "base_url": "https://financialmodelingprep.com/stable/",
        "rate_limit_per_minute": None,
        "rate_limit_per_day": 250,
        "rate_limit_per_month": 7500,
        "delay_between_calls_sec": 1.0,
        "notes": "250/day free. Use /stable/ endpoints (v3 legacy deprecated Aug 2025). Solid backup for fundamentals.",
    },
    "apewisdom": {
        "name": "ApeWisdom",
        "tier": "FREE",
        "cost": "Free",
        "requires_key": False,
        "rate_limit_per_minute": 30,      # self-imposed
        "rate_limit_per_day": None,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 2.0,
        "notes": "Reddit sentiment from 232+ subreddits. No documented limits.",
    },
    "stocktwits": {
        "name": "StockTwits",
        "tier": "FREE",
        "cost": "Free (30 msgs/pull)",
        "requires_key": False,
        "rate_limit_per_minute": 30,      # self-imposed
        "rate_limit_per_day": None,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 2.0,
        "notes": "30 most recent messages per symbol. Bullish/bearish ratio only.",
    },
    "tradingview": {
        "name": "TradingView (TA)",
        "tier": "FREE",
        "cost": "Free (unofficial scraper)",
        "requires_key": False,
        "rate_limit_per_minute": 10,       # self-imposed
        "rate_limit_per_day": 500,         # self-imposed
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 3.0,
        "notes": "Unofficial tradingview-ta library. 26-indicator consensus (Strong Buy → Strong Sell). No key needed.",
    },
    "quiver": {
        "name": "Quiver Quantitative",
        "tier": "PAID",
        "cost": "$10/mo (Hobbyist), $75/mo (Trader)",
        "requires_key": True,
        "key_env_var": "QUIVER_API_KEY",
        "key_url": "https://www.quiverquant.com/",
        "rate_limit_per_minute": None,
        "rate_limit_per_day": None,
        "rate_limit_per_month": None,
        "delay_between_calls_sec": 1.0,
        "notes": "OPTIONAL PAID. Best for Congress trades, lobbying, dark pool. $10/mo min.",
    },
}

# ─── FALLBACK CHAINS ─────────────────────────────────────────
# For each data category, ordered list of APIs to try
FALLBACK_CHAINS = {
    "price_history":       ["yfinance", "polygon", "alpha_vantage", "fmp"],
    "financial_statements": ["yfinance", "sec_edgar", "finnhub", "fmp", "alpha_vantage"],
    "analyst_ratings":     ["finnhub", "yfinance", "seeking_alpha_rapidapi", "mboum", "fmp"],
    "insider_trades":      ["sec_edgar", "finnhub", "mboum", "yfinance"],
    "congress_trades":     ["mboum", "quiver"],
    "options_data":        ["yfinance", "mboum", "alpaca"],
    "technical_indicators": ["alpha_vantage", "mboum", "polygon", "fmp"],
    "news_sentiment":      ["finnhub", "alpha_vantage", "alpaca"],
    "reddit_sentiment":    ["apewisdom", "stocktwits"],
    "social_sentiment":    ["stocktwits", "apewisdom"],
    "analyst_articles":    ["seeking_alpha_rss", "seeking_alpha_rapidapi"],
    "quant_ratings":       ["seeking_alpha_rapidapi"],
    "earnings_calendar":   ["finnhub", "yfinance", "alpha_vantage", "fmp"],
    "earnings":            ["finnhub", "yfinance", "alpha_vantage", "fmp"],
    "dividends":           ["yfinance", "finnhub", "polygon", "fmp"],
    "dividend_data":       ["yfinance", "finnhub", "polygon", "fmp"],
    "fundamentals":        ["yfinance", "sec_edgar", "finnhub", "fmp"],
    "insider_sentiment":   ["finnhub"],
    "tradingview":         ["tradingview"],
    "rss_feeds":           ["seeking_alpha_rss"],
}


def ensure_dirs():
    os.makedirs(os.path.dirname(DEFAULT_CONFIG_PATH), exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)


def init_config():
    """Create or update config file, preserving any existing API keys."""
    ensure_dirs()
    # Load existing config if present
    existing = {}
    if os.path.exists(DEFAULT_CONFIG_PATH):
        try:
            with open(DEFAULT_CONFIG_PATH) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = {}
    existing_apis = existing.get("apis", {})
    config = {"_comment": "Financial Analysis Skill — API Keys. Fill in keys for APIs you want to use.", "apis": {}}
    for api_id, meta in API_REGISTRY.items():
        if meta.get("requires_key"):
            entry = {
                "api_key": "",
                "tier": meta["tier"],
                "cost": meta["cost"],
                "signup_url": meta.get("key_url", ""),
                "enabled": False,
            }
            if meta.get("key_secret_var"):
                entry["api_secret"] = ""
            if meta.get("user_agent_required"):
                entry["user_agent_email"] = ""
            # Preserve existing keys and settings
            if api_id in existing_apis:
                old = existing_apis[api_id]
                if old.get("api_key"):
                    entry["api_key"] = old["api_key"]
                    entry["enabled"] = old.get("enabled", True)
                if old.get("api_secret"):
                    entry["api_secret"] = old["api_secret"]
                if old.get("user_agent_email"):
                    entry["user_agent_email"] = old["user_agent_email"]
            config["apis"][api_id] = entry
        elif meta.get("user_agent_required"):
            entry = {
                "user_agent_email": "",
                "tier": meta["tier"],
                "cost": meta["cost"],
                "enabled": True,
            }
            if api_id in existing_apis and existing_apis[api_id].get("user_agent_email"):
                entry["user_agent_email"] = existing_apis[api_id]["user_agent_email"]
            config["apis"][api_id] = entry
    with open(DEFAULT_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    return DEFAULT_CONFIG_PATH


def load_config(path=None):
    """Load config, falling back to env vars if keys are empty."""
    path = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(path):
        init_config()
    with open(path) as f:
        config = json.load(f)
    # Overlay env vars for any empty keys
    for api_id, meta in API_REGISTRY.items():
        if meta.get("requires_key"):
            env_var = meta.get("key_env_var", "")
            if env_var and os.environ.get(env_var):
                if api_id not in config.get("apis", {}):
                    config.setdefault("apis", {})[api_id] = {}
                if not config["apis"][api_id].get("api_key"):
                    config["apis"][api_id]["api_key"] = os.environ[env_var]
                    config["apis"][api_id]["enabled"] = True
            secret_var = meta.get("key_secret_var", "")
            if secret_var and os.environ.get(secret_var):
                config["apis"].setdefault(api_id, {})["api_secret"] = os.environ[secret_var]
    return config


def get_api_key(api_id, config=None):
    """Get API key for a given provider. Returns None if not configured."""
    if config is None:
        config = load_config()
    api_conf = config.get("apis", {}).get(api_id, {})
    key = api_conf.get("api_key", "")
    if key:
        return key
    env_var = API_REGISTRY.get(api_id, {}).get("key_env_var", "")
    return os.environ.get(env_var, None)


def is_api_available(api_id, config=None):
    """Check if an API is available (key present or no key required)."""
    meta = API_REGISTRY.get(api_id)
    if not meta:
        return False
    if not meta.get("requires_key"):
        return True
    return bool(get_api_key(api_id, config))


def get_rate_limit(api_id):
    """Get rate limit metadata for an API."""
    return {k: v for k, v in API_REGISTRY.get(api_id, {}).items()
            if k.startswith("rate_limit") or k == "delay_between_calls_sec"}


def get_fallback_chain(category, config=None):
    """Get ordered list of available APIs for a data category."""
    chain = FALLBACK_CHAINS.get(category, [])
    return [api_id for api_id in chain if is_api_available(api_id, config)]


def list_apis():
    """Print all APIs with tier, status, and key info."""
    config = load_config()
    print(f"{'API':<30} {'Tier':<8} {'Key?':<6} {'Status':<12} {'Rate Limit':<20} {'Cost'}")
    print("─" * 110)
    for api_id, meta in API_REGISTRY.items():
        available = is_api_available(api_id, config)
        status = "READY" if available else ("NEEDS KEY" if meta.get("requires_key") else "READY")
        limit = ""
        if meta.get("rate_limit_per_day"):
            limit = f"{meta['rate_limit_per_day']}/day"
        elif meta.get("rate_limit_per_minute"):
            limit = f"{meta['rate_limit_per_minute']}/min"
        elif meta.get("rate_limit_per_month"):
            limit = f"{meta['rate_limit_per_month']}/mo"
        print(f"{meta['name']:<30} {meta['tier']:<8} {'Yes' if meta.get('requires_key') else 'No':<6} {status:<12} {limit:<20} {meta['cost']}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        path = init_config()
        print(f"Config initialized at: {path}")
        print("Edit this file to add your API keys, then run:")
        print("  python scripts/api_config.py status")
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        list_apis()
    else:
        print("Usage:")
        print("  python scripts/api_config.py init    — Create blank config file")
        print("  python scripts/api_config.py status  — Show all API status")
