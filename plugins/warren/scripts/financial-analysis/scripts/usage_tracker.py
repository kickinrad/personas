"""
API Usage Tracker & Rate Limit Manager for Financial Analysis Skill.

Tracks every API call, enforces rate limits with automatic fallbacks,
logs errors, and generates daily/weekly usage reports with paid tier recommendations.

Usage:
    from scripts.usage_tracker import UsageTracker
    tracker = UsageTracker()
    tracker.record_call("finnhub", "analyst_ratings", success=True)
    tracker.record_error("alpha_vantage", "technical_indicators", "429 Rate Limited")
    tracker.print_daily_report()
"""
import json, os, sys, time, threading
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict

# Ensure project root is in path so 'from scripts.xxx import' works
# whether this file is run directly or imported from the project root
_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

LOGS_DIR = os.path.expanduser("~/.financial-analysis/logs")
USAGE_LOG = os.path.join(LOGS_DIR, "api_usage.jsonl")
ERROR_LOG = os.path.join(LOGS_DIR, "error_log.jsonl")
DAILY_SUMMARY = os.path.join(LOGS_DIR, "daily_summary.json")


class UsageTracker:
    """Thread-safe API usage tracker with rate limit enforcement."""

    def __init__(self):
        os.makedirs(LOGS_DIR, exist_ok=True)
        self._lock = threading.Lock()
        self._call_timestamps = defaultdict(list)  # api_id -> [timestamps]
        self._daily_counts = defaultdict(int)       # (api_id, date_str) -> count
        self._monthly_counts = defaultdict(int)     # (api_id, month_str) -> count
        self._load_today_counts()

    def _load_today_counts(self):
        """Load today's counts from the usage log."""
        today = date.today().isoformat()
        month = date.today().strftime("%Y-%m")
        if not os.path.exists(USAGE_LOG):
            return
        try:
            with open(USAGE_LOG) as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        ts_date = entry.get("date", "")
                        api = entry.get("api_id", "")
                        if ts_date == today:
                            self._daily_counts[(api, today)] += 1
                        if ts_date.startswith(month):
                            self._monthly_counts[(api, month)] += 1
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

    def can_call(self, api_id, registry=None):
        """Check if an API call is within rate limits. Returns (bool, reason)."""
        if registry is None:
            from scripts.api_config import API_REGISTRY
            registry = API_REGISTRY
        meta = registry.get(api_id, {})
        today = date.today().isoformat()
        month = date.today().strftime("%Y-%m")
        now = time.time()

        # Check per-minute limit
        rpm = meta.get("rate_limit_per_minute")
        if rpm:
            with self._lock:
                recent = [t for t in self._call_timestamps[api_id] if now - t < 60]
                self._call_timestamps[api_id] = recent
                if len(recent) >= rpm:
                    return False, f"Rate limited: {len(recent)}/{rpm} calls in last minute"

        # Check per-day limit
        rpd = meta.get("rate_limit_per_day")
        if rpd:
            with self._lock:
                day_count = self._daily_counts.get((api_id, today), 0)
                if day_count >= rpd:
                    return False, f"Daily limit reached: {day_count}/{rpd}"

        # Check per-month limit
        rpm_mo = meta.get("rate_limit_per_month")
        if rpm_mo:
            with self._lock:
                mo_count = self._monthly_counts.get((api_id, month), 0)
                if mo_count >= rpm_mo:
                    return False, f"Monthly limit reached: {mo_count}/{rpm_mo}"

        return True, "OK"

    def record_call(self, api_id, data_category, success=True, response_time_ms=0, details=""):
        """Record a successful or failed API call."""
        now = time.time()
        today = date.today().isoformat()
        month = date.today().strftime("%Y-%m")
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": today,
            "api_id": api_id,
            "data_category": data_category,
            "success": success,
            "response_time_ms": response_time_ms,
            "details": details,
        }
        with self._lock:
            self._call_timestamps[api_id].append(now)
            self._daily_counts[(api_id, today)] += 1
            self._monthly_counts[(api_id, month)] += 1
            with open(USAGE_LOG, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def record_error(self, api_id, data_category, error_msg, fallback_api=None, fallback_success=None):
        """Record an error with optional fallback info."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": date.today().isoformat(),
            "api_id": api_id,
            "data_category": data_category,
            "error": error_msg,
            "fallback_api": fallback_api,
            "fallback_success": fallback_success,
        }
        with self._lock:
            with open(ERROR_LOG, "a") as f:
                f.write(json.dumps(entry) + "\n")

    def get_daily_usage(self, target_date=None):
        """Get usage counts per API for a specific date."""
        target = (target_date or date.today()).isoformat()
        counts = defaultdict(lambda: {"calls": 0, "errors": 0})
        if os.path.exists(USAGE_LOG):
            with open(USAGE_LOG) as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        if e.get("date") == target:
                            api = e["api_id"]
                            counts[api]["calls"] += 1
                            if not e.get("success"):
                                counts[api]["errors"] += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
        return dict(counts)

    def get_monthly_usage(self, target_month=None):
        """Get usage counts per API for a specific month (YYYY-MM)."""
        target = target_month or date.today().strftime("%Y-%m")
        counts = defaultdict(lambda: {"calls": 0, "errors": 0})
        if os.path.exists(USAGE_LOG):
            with open(USAGE_LOG) as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        if e.get("date", "").startswith(target):
                            api = e["api_id"]
                            counts[api]["calls"] += 1
                            if not e.get("success"):
                                counts[api]["errors"] += 1
                    except (json.JSONDecodeError, KeyError):
                        continue
        return dict(counts)

    def get_errors(self, last_n_days=7):
        """Get recent errors grouped by API."""
        cutoff = (date.today() - timedelta(days=last_n_days)).isoformat()
        errors = defaultdict(list)
        if os.path.exists(ERROR_LOG):
            with open(ERROR_LOG) as f:
                for line in f:
                    try:
                        e = json.loads(line.strip())
                        if e.get("date", "") >= cutoff:
                            errors[e["api_id"]].append(e)
                    except (json.JSONDecodeError, KeyError):
                        continue
        return dict(errors)

    def print_daily_report(self, target_date=None):
        """Print formatted daily usage report."""
        from scripts.api_config import API_REGISTRY
        target = target_date or date.today()
        usage = self.get_daily_usage(target)
        print(f"\n{'='*80}")
        print(f"  API USAGE REPORT — {target.isoformat()}")
        print(f"{'='*80}")
        print(f"{'API':<28} {'Calls':<8} {'Errors':<8} {'Limit':<12} {'% Used':<10} {'Status'}")
        print(f"{'─'*80}")
        total_calls = 0
        warnings = []
        for api_id, meta in API_REGISTRY.items():
            u = usage.get(api_id, {"calls": 0, "errors": 0})
            calls = u["calls"]
            errs = u["errors"]
            total_calls += calls
            limit = meta.get("rate_limit_per_day") or meta.get("rate_limit_per_month") or 0
            limit_label = ""
            pct = 0
            if meta.get("rate_limit_per_day"):
                limit_label = f"{meta['rate_limit_per_day']}/day"
                pct = (calls / meta["rate_limit_per_day"]) * 100 if meta["rate_limit_per_day"] else 0
            elif meta.get("rate_limit_per_month"):
                monthly = self.get_monthly_usage()
                mo_calls = monthly.get(api_id, {}).get("calls", 0)
                limit_label = f"{meta['rate_limit_per_month']}/mo"
                pct = (mo_calls / meta["rate_limit_per_month"]) * 100 if meta["rate_limit_per_month"] else 0
            else:
                limit_label = "Unlimited"
            status = "OK"
            if pct >= 90:
                status = "CRITICAL"
                warnings.append((api_id, meta["name"], pct, meta.get("cost", "")))
            elif pct >= 70:
                status = "WARNING"
                warnings.append((api_id, meta["name"], pct, meta.get("cost", "")))
            if calls > 0 or errs > 0:
                print(f"{meta['name']:<28} {calls:<8} {errs:<8} {limit_label:<12} {pct:>5.1f}%    {status}")
        print(f"{'─'*80}")
        print(f"{'TOTAL':<28} {total_calls:<8}")

        if warnings:
            print(f"\n{'⚠ PAID TIER RECOMMENDATIONS':}")
            print(f"{'─'*80}")
            for api_id, name, pct, cost in warnings:
                print(f"  {name}: {pct:.0f}% of free limit used. Current cost: {cost}")
                if pct >= 90:
                    print(f"    → STRONGLY RECOMMEND upgrading to paid tier to avoid service disruption.")
                else:
                    print(f"    → Consider monitoring. Upgrade if usage consistently exceeds 70%.")

    def print_error_report(self, last_n_days=7):
        """Print formatted error report."""
        errors = self.get_errors(last_n_days)
        if not errors:
            print(f"\nNo API errors in the last {last_n_days} days.")
            return
        print(f"\n{'='*80}")
        print(f"  ERROR LOG — Last {last_n_days} days")
        print(f"{'='*80}")
        for api_id, err_list in errors.items():
            print(f"\n  {api_id} ({len(err_list)} errors):")
            for e in err_list[-5:]:  # last 5
                fb = f" → Fallback: {e['fallback_api']} ({'OK' if e.get('fallback_success') else 'FAILED'})" if e.get("fallback_api") else ""
                print(f"    [{e['timestamp'][:19]}] {e['data_category']}: {e['error']}{fb}")

    def save_daily_summary(self, output_path=None):
        """Save aggregated daily summary to JSON. Uses default path if none given."""
        from scripts.api_config import API_REGISTRY
        today = date.today().isoformat()
        usage = self.get_daily_usage()
        monthly = self.get_monthly_usage()
        summary = {
            "date": today,
            "generated_at": datetime.now().isoformat(),
            "apis": {},
            "daily_usage": {},
            "monthly_usage": {},
            "paid_tier_recommendations": [],
        }
        for api_id, meta in API_REGISTRY.items():
            u = usage.get(api_id, {"calls": 0, "errors": 0})
            m = monthly.get(api_id, {"calls": 0, "errors": 0})
            if u["calls"] > 0 or m["calls"] > 0:
                daily_limit = meta.get("rate_limit_per_day")
                monthly_limit = meta.get("rate_limit_per_month")
                daily_pct = (u["calls"] / daily_limit * 100) if daily_limit else 0
                monthly_pct = (m["calls"] / monthly_limit * 100) if monthly_limit else 0
                api_summary = {
                    "name": meta["name"],
                    "daily_calls": u["calls"],
                    "daily_errors": u["errors"],
                    "daily_limit": daily_limit,
                    "daily_pct": round(daily_pct, 1),
                    "monthly_calls": m["calls"],
                    "monthly_limit": monthly_limit,
                    "monthly_pct": round(monthly_pct, 1),
                }
                summary["apis"][api_id] = api_summary
                summary["daily_usage"][api_id] = {
                    "name": meta["name"],
                    "calls": u["calls"],
                    "errors": u["errors"],
                    "daily_limit": daily_limit,
                    "daily_pct": round(daily_pct, 1),
                }
                summary["monthly_usage"][api_id] = {
                    "name": meta["name"],
                    "calls": m["calls"],
                    "errors": m["errors"],
                    "monthly_limit": monthly_limit,
                    "monthly_pct": round(monthly_pct, 1),
                }
                max_pct = max(daily_pct, monthly_pct)
                if max_pct >= 70:
                    summary["paid_tier_recommendations"].append({
                        "api_id": api_id,
                        "name": meta["name"],
                        "usage_pct": round(max_pct, 1),
                        "current_cost": meta["cost"],
                        "severity": "CRITICAL" if max_pct >= 90 else "WARNING",
                        "recommendation": f"Upgrade to paid tier" if max_pct >= 90 else "Monitor usage",
                    })
        dest = output_path or DAILY_SUMMARY
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            json.dump(summary, f, indent=2)
        return summary


# ─── CONVENIENCE FUNCTIONS ────────────────────────────────────

_tracker_instance = None

def get_tracker():
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UsageTracker()
    return _tracker_instance


if __name__ == "__main__":
    tracker = UsageTracker()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "daily":
            tracker.print_daily_report()
        elif cmd == "errors":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            tracker.print_error_report(days)
        elif cmd == "summary":
            s = tracker.save_daily_summary()
            print(json.dumps(s, indent=2))
        else:
            print("Usage: python scripts/usage_tracker.py [daily|errors|summary]")
    else:
        tracker.print_daily_report()
        tracker.print_error_report()
