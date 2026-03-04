# API Setup Guide — Financial Analysis Skill

## Quick Start

Run the config initializer to create your API keys file:
```bash
python scripts/api_config.py init
```
This creates `~/.financial-analysis/api_keys.json` with blank entries for every API.

## API Keys — Step by Step

### Required for Core Functionality (all FREE)

| # | API | Signup URL | What You Get |
|---|-----|-----------|--------------|
| 1 | **Finnhub** | https://finnhub.io/register | Analyst ratings, insider sentiment, earnings, news (60/min free) |
| 2 | **Alpha Vantage** | https://www.alphavantage.co/support/#api-key | 50+ technicals, financials, AI news sentiment (25/day free) |
| 3 | **Mboum Finance** | https://rapidapi.com/sparkhub-sparkhub-default/api/mboum-finance | Congress trades, options flow, IV rank, technicals (600/mo free) |
| 4 | **Seeking Alpha RapidAPI** | https://rapidapi.com/apidojo/api/seeking-alpha | Quant ratings, factor grades, analyst ratings (1K/mo free) |

### No Key Required (FREE)

| API | Notes |
|-----|-------|
| **yfinance** | Python package. `pip install yfinance`. No key needed. |
| **SEC EDGAR** | Set your email in config for User-Agent header. |
| **ApeWisdom** | No authentication required. |
| **StockTwits** | No authentication required. |
| **RSS Feeds** | All free. Uses feedparser. `pip install feedparser`. |

### Optional (FREE but need signup)

| API | Signup URL | What You Get |
|-----|-----------|--------------|
| **Polygon.io** | https://polygon.io/dashboard/signup | EOD data backup, technicals (5/min free) |
| **Alpaca Markets** | https://app.alpaca.markets/signup | Paper trading, news stream, historical bars (200/min free) |
| **Financial Modeling Prep** | https://financialmodelingprep.com/developer/docs/ | Financial statements backup (250/day free) |

### Optional PAID

| API | Signup URL | Cost | What You Get |
|-----|-----------|------|--------------|
| **Quiver Quantitative** | https://www.quiverquant.com/ | $10/mo | Best-in-class Congress trades, lobbying, dark pool, gov contracts |

## Setting Keys

### Option A: Edit the config file directly
```bash
# Open the config file
nano ~/.financial-analysis/api_keys.json
```
Set `"api_key": "your-key-here"` and `"enabled": true` for each API.

### Option B: Use environment variables
```bash
export FINNHUB_API_KEY="your-key"
export ALPHA_VANTAGE_API_KEY="your-key"
export MBOUM_API_KEY="your-key"
export SEEKING_ALPHA_RAPIDAPI_KEY="your-key"
export POLYGON_API_KEY="your-key"
export ALPACA_API_KEY="your-key"
export ALPACA_API_SECRET="your-secret"
export FMP_API_KEY="your-key"
export QUIVER_API_KEY="your-key"
```
Environment variables override empty config file entries.

### Option C: Set SEC EDGAR User-Agent
SEC EDGAR requires a User-Agent header with a valid email:
```json
{
  "apis": {
    "sec_edgar": {
      "user_agent_email": "your-email@example.com",
      "enabled": true
    }
  }
}
```

## Verify Setup
```bash
python scripts/api_config.py status
```
This shows all APIs with their tier (FREE/PAID), key status (READY/NEEDS KEY), and rate limits.

## Python Dependencies
```bash
pip install yfinance feedparser pandas pandas-ta requests --break-system-packages
```

## Rate Limits at a Glance

| API | Free Limit | Self-Imposed Delay | Tightest Constraint |
|-----|-----------|-------------------|-------------------|
| yfinance | Unlimited* | 2s between calls | IP blocking risk |
| Finnhub | 60/min | 1s | Per-minute |
| SEC EDGAR | 10/sec | 0.1s | Per-second |
| Mboum | ~20/day, 600/mo | 2s | Monthly cap |
| Alpha Vantage | 5/min, 25/day | 12s | **Daily cap (tightest)** |
| SA RapidAPI | ~33/day, 1K/mo | 2s | Monthly cap |
| Polygon | 5/min | 12s | Per-minute |
| Alpaca | 200/min | 0.3s | Per-minute |
| FMP | 250/day | 1s | Daily cap |
| ApeWisdom | Undocumented | 2s | Unknown |
| StockTwits | ~30 msgs/pull | 2s | Per-pull depth |

## Error Log & Usage Tracking

All API calls are automatically logged to `~/.financial-analysis/logs/`:

| File | Contents |
|------|----------|
| `api_usage.jsonl` | Every API call with timestamp, API, category, success, response time |
| `error_log.jsonl` | Failed calls with error details and fallback results |
| `daily_summary.json` | Aggregated daily usage with paid tier recommendations |

### View Reports
```bash
python scripts/usage_tracker.py daily     # Today's usage report
python scripts/usage_tracker.py errors    # Recent errors (last 7 days)
python scripts/usage_tracker.py summary   # Save daily summary JSON
```

### Automatic Fallbacks
When a primary API fails (rate limit, error, timeout), the system automatically tries the next API in the fallback chain. The error log records which API failed and which fallback succeeded. See `scripts/api_config.py` → `FALLBACK_CHAINS` for the full chain per data category.
