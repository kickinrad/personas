"""
Macro Calendar — Upcoming earnings, economic events, and Fed decisions.

Surfaces timing-critical events that affect portfolio decisions:
  - Earnings dates for held stocks (don't sell right before a catalyst)
  - CPI / jobs reports / GDP releases
  - Fed rate decisions (FOMC)
  - Options expiration dates

Data sources:
  - yfinance: Next earnings date per ticker
  - Finnhub: Economic calendar (free tier)
  - Hardcoded: Known FOMC dates, CPI schedule, options expiry (triple witching)

Usage:
    from scripts.macro_calendar import get_earnings_calendar, get_economic_events
    from scripts.macro_calendar import get_macro_summary, days_until_event

    # Earnings for specific tickers
    earnings = get_earnings_calendar(["AAPL", "MSFT", "NVDA"])

    # Upcoming economic events
    events = get_economic_events(days_ahead=14)

    # Full summary for portfolio review header
    summary = get_macro_summary(tickers=["AAPL", "MSFT"], days_ahead=14)
"""
import os, sys
from datetime import datetime, date, timedelta

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ═══════════════════════════════════════════════════════════════════════
#  HARDCODED CALENDARS (updated periodically — reliable fallback)
# ═══════════════════════════════════════════════════════════════════════

# 2025-2026 FOMC meeting dates (announcement days)
FOMC_DATES = [
    # 2025
    "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
    "2025-07-30", "2025-09-17", "2025-10-29", "2025-12-17",
    # 2026
    "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17",
    "2026-07-29", "2026-09-16", "2026-10-28", "2026-12-16",
]

# 2025-2026 CPI release dates (approximate — BLS publishes ~10th-14th of month)
CPI_DATES = [
    "2025-01-15", "2025-02-12", "2025-03-12", "2025-04-10", "2025-05-13",
    "2025-06-11", "2025-07-11", "2025-08-12", "2025-09-10", "2025-10-14",
    "2025-11-12", "2025-12-10",
    "2026-01-14", "2026-02-11", "2026-03-11", "2026-04-14", "2026-05-12",
    "2026-06-10", "2026-07-14", "2026-08-12", "2026-09-15", "2026-10-13",
    "2026-11-10", "2026-12-10",
]

# Jobs reports (first Friday of each month, usually)
JOBS_DATES = [
    "2025-01-10", "2025-02-07", "2025-03-07", "2025-04-04", "2025-05-02",
    "2025-06-06", "2025-07-03", "2025-08-01", "2025-09-05", "2025-10-03",
    "2025-11-07", "2025-12-05",
    "2026-01-09", "2026-02-06", "2026-03-06", "2026-04-03", "2026-05-01",
    "2026-06-05", "2026-07-02", "2026-08-07", "2026-09-04", "2026-10-02",
    "2026-11-06", "2026-12-04",
]

# Triple witching / quad witching (3rd Friday of March, June, Sept, Dec)
OPEX_DATES = [
    "2025-03-21", "2025-06-20", "2025-09-19", "2025-12-19",
    "2026-03-20", "2026-06-19", "2026-09-18", "2026-12-18",
]


def _parse_date(d):
    """Parse a date string to a date object."""
    if isinstance(d, date):
        return d
    if isinstance(d, datetime):
        return d.date()
    try:
        return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def days_until_event(event_date):
    """Return number of calendar days from today to the event."""
    d = _parse_date(event_date)
    if not d:
        return None
    return (d - date.today()).days


# ═══════════════════════════════════════════════════════════════════════
#  EARNINGS CALENDAR
# ═══════════════════════════════════════════════════════════════════════

def get_earnings_calendar(tickers):
    """
    Get next earnings date for each ticker via yfinance.

    Returns: list of {ticker, earnings_date, days_until, is_upcoming}
    """
    results = []
    try:
        import yfinance as yf
    except ImportError:
        return results

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            cal = stock.calendar
            earn_date = None

            if cal is not None:
                # yfinance returns different formats depending on version
                if isinstance(cal, dict):
                    ed = cal.get("Earnings Date")
                    if ed:
                        if isinstance(ed, list) and len(ed) > 0:
                            earn_date = ed[0]
                        else:
                            earn_date = ed
                elif hasattr(cal, "iloc"):
                    # DataFrame format
                    try:
                        earn_date = cal.iloc[0, 0] if cal.shape[0] > 0 else None
                    except Exception:
                        pass

            # Fallback: try earnings_dates property
            if earn_date is None:
                try:
                    edates = stock.earnings_dates
                    if edates is not None and len(edates) > 0:
                        # Get the nearest future date
                        today = datetime.now()
                        future = [d for d in edates.index if d >= today]
                        if future:
                            earn_date = future[0]
                except Exception:
                    pass

            if earn_date is not None:
                d = _parse_date(earn_date)
                if d:
                    days = (d - date.today()).days
                    results.append({
                        "ticker": ticker,
                        "earnings_date": d.isoformat(),
                        "days_until": days,
                        "is_upcoming": 0 <= days <= 14,
                        "is_imminent": 0 <= days <= 3,
                    })
        except Exception:
            continue

    return sorted(results, key=lambda x: x.get("days_until", 999))


# ═══════════════════════════════════════════════════════════════════════
#  ECONOMIC EVENTS
# ═══════════════════════════════════════════════════════════════════════

def get_economic_events(days_ahead=14):
    """
    Get upcoming economic events within the specified window.

    Returns: list of {event, date, days_until, impact}
    """
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    events = []

    # FOMC
    for d in FOMC_DATES:
        dt = _parse_date(d)
        if dt and today <= dt <= cutoff:
            days = (dt - today).days
            events.append({
                "event": "FOMC Rate Decision",
                "date": dt.isoformat(),
                "days_until": days,
                "impact": "HIGH",
                "description": "Federal Reserve interest rate decision and economic projections",
                "affects": "All sectors — especially REITs, banks, growth stocks",
            })

    # CPI
    for d in CPI_DATES:
        dt = _parse_date(d)
        if dt and today <= dt <= cutoff:
            days = (dt - today).days
            events.append({
                "event": "CPI Report",
                "date": dt.isoformat(),
                "days_until": days,
                "impact": "HIGH",
                "description": "Consumer Price Index — key inflation measure",
                "affects": "Rate-sensitive sectors, growth vs value rotation",
            })

    # Jobs
    for d in JOBS_DATES:
        dt = _parse_date(d)
        if dt and today <= dt <= cutoff:
            days = (dt - today).days
            events.append({
                "event": "Jobs Report (NFP)",
                "date": dt.isoformat(),
                "days_until": days,
                "impact": "HIGH",
                "description": "Non-Farm Payrolls — labor market health",
                "affects": "Consumer discretionary, industrials, broad market sentiment",
            })

    # Options expiration
    for d in OPEX_DATES:
        dt = _parse_date(d)
        if dt and today <= dt <= cutoff:
            days = (dt - today).days
            events.append({
                "event": "Triple Witching (OPEX)",
                "date": dt.isoformat(),
                "days_until": days,
                "impact": "MEDIUM",
                "description": "Index futures, index options, stock options all expire — high volume day",
                "affects": "Elevated volatility, especially last 2 hours of trading",
            })

    # Try Finnhub for additional events
    try:
        fh_events = _fetch_finnhub_calendar(days_ahead)
        events.extend(fh_events)
    except Exception:
        pass

    return sorted(events, key=lambda x: x.get("days_until", 999))


def _fetch_finnhub_calendar(days_ahead=14):
    """Fetch economic calendar from Finnhub (free tier)."""
    events = []
    try:
        from scripts.api_config import load_config
        config = load_config()
        key = config.get("api_keys", {}).get("finnhub")
        if not key:
            return events

        import requests
        today = date.today()
        end = today + timedelta(days=days_ahead)

        r = requests.get(
            "https://finnhub.io/api/v1/calendar/economic",
            params={
                "from": today.isoformat(),
                "to": end.isoformat(),
                "token": key,
            },
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            for item in data.get("economicCalendar", []):
                impact = item.get("impact", 0)
                if impact < 2:  # skip low-impact events
                    continue
                dt = _parse_date(item.get("time", item.get("date", "")))
                if not dt:
                    continue
                events.append({
                    "event": item.get("event", "Economic Event"),
                    "date": dt.isoformat(),
                    "days_until": (dt - today).days,
                    "impact": "HIGH" if impact >= 3 else "MEDIUM",
                    "description": f"Country: {item.get('country', 'US')} | "
                                   f"Previous: {item.get('prev', 'N/A')} | "
                                   f"Estimate: {item.get('estimate', 'N/A')}",
                    "affects": item.get("country", "US"),
                    "source": "finnhub",
                })
    except Exception:
        pass

    return events


# ═══════════════════════════════════════════════════════════════════════
#  MACRO SUMMARY (for portfolio review header)
# ═══════════════════════════════════════════════════════════════════════

def get_macro_summary(tickers=None, days_ahead=14):
    """
    Build a complete macro summary for the portfolio review.

    Returns:
        dict with earnings_calendar, economic_events, risk_flags
    """
    tickers = tickers or []
    earnings = get_earnings_calendar(tickers) if tickers else []
    events = get_economic_events(days_ahead)

    # Generate risk flags
    risk_flags = []

    # Imminent earnings
    imminent = [e for e in earnings if e.get("is_imminent")]
    if imminent:
        tickers_str = ", ".join(e["ticker"] for e in imminent)
        risk_flags.append({
            "flag": "EARNINGS_IMMINENT",
            "severity": "HIGH",
            "message": f"Earnings within 3 days: {tickers_str} — expect volatility, review position sizing",
        })

    upcoming = [e for e in earnings if e.get("is_upcoming") and not e.get("is_imminent")]
    if upcoming:
        tickers_str = ", ".join(f"{e['ticker']} ({e['days_until']}d)" for e in upcoming)
        risk_flags.append({
            "flag": "EARNINGS_UPCOMING",
            "severity": "MEDIUM",
            "message": f"Earnings within 14 days: {tickers_str}",
        })

    # High-impact economic events
    high_events = [e for e in events if e.get("impact") == "HIGH" and e.get("days_until", 99) <= 5]
    if high_events:
        for ev in high_events:
            risk_flags.append({
                "flag": "MACRO_EVENT",
                "severity": "HIGH",
                "message": f"{ev['event']} in {ev['days_until']} day(s) ({ev['date']}) — {ev.get('affects', '')}",
            })

    return {
        "earnings_calendar": earnings,
        "economic_events": events,
        "risk_flags": risk_flags,
        "checked_at": datetime.now().isoformat(),
    }


def format_macro_summary(summary):
    """Format the macro summary for console output."""
    lines = []
    _h = lines.append

    _h(f"  {'─' * 60}")
    _h(f"  MACRO CALENDAR")
    _h(f"  {'─' * 60}")

    # Risk flags first
    flags = summary.get("risk_flags", [])
    if flags:
        for f in flags:
            icon = "🔴" if f["severity"] == "HIGH" else "🟡"
            _h(f"  {icon} {f['message']}")
        _h("")

    # Earnings
    earnings = summary.get("earnings_calendar", [])
    if earnings:
        _h(f"  UPCOMING EARNINGS:")
        for e in earnings:
            days = e["days_until"]
            marker = " *** IMMINENT" if e.get("is_imminent") else ""
            if days < 0:
                _h(f"    {e['ticker']:<8} {e['earnings_date']}  ({abs(days)}d ago){marker}")
            else:
                _h(f"    {e['ticker']:<8} {e['earnings_date']}  (in {days}d){marker}")
        _h("")

    # Economic events
    events = summary.get("economic_events", [])
    if events:
        _h(f"  ECONOMIC EVENTS (next 14 days):")
        for ev in events[:8]:
            impact = ev.get("impact", "?")
            _h(f"    [{impact}] {ev['event']} — {ev['date']} (in {ev['days_until']}d)")
    else:
        _h(f"  No major economic events in the next 14 days.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Macro Calendar")
    parser.add_argument("tickers", nargs="*", help="Tickers to check earnings for")
    parser.add_argument("--days", type=int, default=14, help="Days ahead to scan (default: 14)")
    args = parser.parse_args()

    summary = get_macro_summary(tickers=args.tickers, days_ahead=args.days)
    print(format_macro_summary(summary))


if __name__ == "__main__":
    main()
