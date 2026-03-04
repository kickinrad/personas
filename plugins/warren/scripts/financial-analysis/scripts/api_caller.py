"""
Resilient API Caller with automatic fallback, rate limit enforcement, and logging.

This is the central execution layer. Every API call in the skill goes through here.
It checks rate limits, tries the primary API, and automatically falls back to
alternatives if the primary fails or is rate-limited.

Usage:
    from scripts.api_caller import call_api, call_with_fallback

    # Single API call with rate limit check
    result = call_api("finnhub", "analyst_ratings", fetch_fn, ticker="AAPL")

    # Call with automatic fallback chain
    result = call_with_fallback("analyst_ratings", {
        "finnhub": lambda: fetch_finnhub_ratings("AAPL"),
        "yfinance": lambda: fetch_yfinance_ratings("AAPL"),
        "mboum":   lambda: fetch_mboum_ratings("AAPL"),
    })
"""
import os, sys, time, traceback

# Ensure project root is in path
_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from scripts.usage_tracker import get_tracker
from scripts.api_config import API_REGISTRY, get_fallback_chain, is_api_available


def call_api(api_id, data_category, fetch_fn, **kwargs):
    """
    Execute a single API call with rate limit checking, timing, and logging.

    Args:
        api_id: API identifier (e.g. "finnhub")
        data_category: What data is being fetched (e.g. "analyst_ratings")
        fetch_fn: Callable that performs the actual API call
        **kwargs: Passed to fetch_fn

    Returns:
        {"success": bool, "data": any, "api_id": str, "error": str|None}
    """
    tracker = get_tracker()

    # Check rate limit before calling
    can, reason = tracker.can_call(api_id, API_REGISTRY)
    if not can:
        tracker.record_error(api_id, data_category, reason)
        return {"success": False, "data": None, "api_id": api_id, "error": reason}

    # Respect delay between calls
    delay = API_REGISTRY.get(api_id, {}).get("delay_between_calls_sec", 1.0)
    time.sleep(delay)

    # Execute the call
    start = time.time()
    try:
        result = fetch_fn(**kwargs) if kwargs else fetch_fn()
        elapsed_ms = int((time.time() - start) * 1000)
        tracker.record_call(api_id, data_category, success=True, response_time_ms=elapsed_ms)
        return {"success": True, "data": result, "api_id": api_id, "error": None}
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        error_msg = f"{type(e).__name__}: {str(e)}"
        tracker.record_call(api_id, data_category, success=False, response_time_ms=elapsed_ms, details=error_msg)
        tracker.record_error(api_id, data_category, error_msg)
        return {"success": False, "data": None, "api_id": api_id, "error": error_msg}


def call_with_fallback(data_category, api_functions, config=None):
    """
    Try each API in the fallback chain until one succeeds.

    Args:
        data_category: Data category name (maps to FALLBACK_CHAINS)
        api_functions: Dict of {api_id: callable} for each available API
        config: Optional loaded config (for key availability checks)

    Returns:
        {"success": bool, "data": any, "api_id": str, "error": str|None, "attempts": list}
    """
    tracker = get_tracker()
    chain = get_fallback_chain(data_category, config)
    attempts = []

    for api_id in chain:
        if api_id not in api_functions:
            continue

        result = call_api(api_id, data_category, api_functions[api_id])
        attempts.append({"api_id": api_id, "success": result["success"], "error": result.get("error")})

        if result["success"]:
            # Log fallback usage if not the first in chain
            if len(attempts) > 1:
                primary = attempts[0]["api_id"]
                tracker.record_error(primary, data_category,
                                     attempts[0].get("error", "Failed"),
                                     fallback_api=api_id, fallback_success=True)
            return {**result, "attempts": attempts}

    # All failed
    error_summary = "; ".join([f"{a['api_id']}: {a['error']}" for a in attempts])
    if attempts:
        tracker.record_error(attempts[0]["api_id"], data_category,
                             f"All fallbacks failed: {error_summary}",
                             fallback_api=attempts[-1]["api_id"] if len(attempts) > 1 else None,
                             fallback_success=False)
    return {
        "success": False,
        "data": None,
        "api_id": None,
        "error": f"All APIs failed for {data_category}: {error_summary}",
        "attempts": attempts,
    }
