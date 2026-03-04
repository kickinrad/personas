"""
Technical Analysis Engine — Local computations using pandas-ta + TradingView.

All TA is computed locally from OHLCV data (no API calls needed for the core
indicators). TradingView consensus is fetched as an optional cross-check.

Usage:
    from scripts.technical_analysis import compute_technicals
    ta = compute_technicals(price_df)  # pandas DataFrame with OHLCV columns
"""
import os, sys
import pandas as pd
import numpy as np

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Try importing pandas-ta; fall back gracefully
try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False


def compute_technicals(df, ticker=""):
    """
    Compute all technical indicators from an OHLCV DataFrame.

    Args:
        df: pandas DataFrame with columns: Open, High, Low, Close, Volume
            (as returned by yfinance's history())
        ticker: symbol name (for labeling)

    Returns:
        dict with all computed indicators and technical scores
    """
    if df is None or df.empty or len(df) < 20:
        raise ValueError(f"Insufficient data for TA: {len(df) if df is not None else 0} rows (need 20+)")

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    latest_close = float(close.iloc[-1])

    result = {
        "ticker": ticker,
        "latest_close": latest_close,
        "data_points": len(df),
    }

    # ── Moving Averages ─────────────────────────────────────────
    result["sma_20"] = _safe_last(close.rolling(20).mean())
    result["sma_50"] = _safe_last(close.rolling(50).mean())
    result["sma_200"] = _safe_last(close.rolling(200).mean())
    result["ema_12"] = _safe_last(close.ewm(span=12).mean())
    result["ema_26"] = _safe_last(close.ewm(span=26).mean())
    result["ema_50"] = _safe_last(close.ewm(span=50).mean())

    # Trend signals
    result["above_sma50"] = latest_close > result["sma_50"] if result["sma_50"] else None
    result["above_sma200"] = latest_close > result["sma_200"] if result["sma_200"] else None
    result["golden_cross"] = (result["sma_50"] or 0) > (result["sma_200"] or 0) if result["sma_50"] and result["sma_200"] else None
    result["death_cross"] = (result["sma_50"] or 0) < (result["sma_200"] or 0) if result["sma_50"] and result["sma_200"] else None

    # ── RSI ──────────────────────────────────────────────────────
    if HAS_PANDAS_TA:
        rsi_series = ta.rsi(close, length=14)
        result["rsi_14"] = _safe_last(rsi_series)
    else:
        result["rsi_14"] = _compute_rsi(close, 14)

    # ── MACD ─────────────────────────────────────────────────────
    if HAS_PANDAS_TA:
        macd_df = ta.macd(close, fast=12, slow=26, signal=9)
        if macd_df is not None and not macd_df.empty:
            cols = macd_df.columns
            result["macd_line"] = _safe_last(macd_df[cols[0]])
            result["macd_signal"] = _safe_last(macd_df[cols[1]])
            result["macd_histogram"] = _safe_last(macd_df[cols[2]])
        else:
            result["macd_line"] = result["macd_signal"] = result["macd_histogram"] = None
    else:
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        result["macd_line"] = _safe_last(macd_line)
        result["macd_signal"] = _safe_last(signal_line)
        result["macd_histogram"] = _safe_last(macd_line - signal_line)

    result["macd_bullish"] = (result["macd_line"] or 0) > (result["macd_signal"] or 0) if result["macd_line"] is not None else None

    # ── Bollinger Bands ──────────────────────────────────────────
    if HAS_PANDAS_TA:
        bb = ta.bbands(close, length=20, std=2)
        if bb is not None and not bb.empty:
            cols = bb.columns
            result["bb_lower"] = _safe_last(bb[cols[0]])
            result["bb_mid"] = _safe_last(bb[cols[1]])
            result["bb_upper"] = _safe_last(bb[cols[2]])
        else:
            result["bb_lower"] = result["bb_mid"] = result["bb_upper"] = None
    else:
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        result["bb_mid"] = _safe_last(sma20)
        result["bb_upper"] = _safe_last(sma20 + 2 * std20)
        result["bb_lower"] = _safe_last(sma20 - 2 * std20)

    if result["bb_upper"] and result["bb_lower"]:
        bb_range = result["bb_upper"] - result["bb_lower"]
        result["bb_position"] = (latest_close - result["bb_lower"]) / bb_range if bb_range > 0 else 0.5
    else:
        result["bb_position"] = None

    # ── ATR (Average True Range) ─────────────────────────────────
    if HAS_PANDAS_TA:
        atr_series = ta.atr(high, low, close, length=14)
        result["atr_14"] = _safe_last(atr_series)
    else:
        result["atr_14"] = _compute_atr(high, low, close, 14)

    # ── ADX (Average Directional Index) ──────────────────────────
    if HAS_PANDAS_TA:
        adx_df = ta.adx(high, low, close, length=14)
        if adx_df is not None and not adx_df.empty:
            result["adx"] = _safe_last(adx_df.iloc[:, 0])
        else:
            result["adx"] = None
    else:
        result["adx"] = None  # Complex to compute without library

    # ── Stochastic Oscillator ────────────────────────────────────
    if HAS_PANDAS_TA:
        stoch = ta.stoch(high, low, close, k=14, d=3)
        if stoch is not None and not stoch.empty:
            result["stoch_k"] = _safe_last(stoch.iloc[:, 0])
            result["stoch_d"] = _safe_last(stoch.iloc[:, 1])
        else:
            result["stoch_k"] = result["stoch_d"] = None
    else:
        result["stoch_k"] = result["stoch_d"] = None

    # ── Volume Analysis ──────────────────────────────────────────
    vol_avg_20 = volume.rolling(20).mean()
    result["volume_avg_20"] = _safe_last(vol_avg_20)
    result["volume_latest"] = int(volume.iloc[-1])
    result["volume_ratio"] = float(volume.iloc[-1] / vol_avg_20.iloc[-1]) if _safe_last(vol_avg_20) else None

    # ── Support / Resistance Levels ──────────────────────────────
    result["support_resistance"] = compute_support_resistance(df)

    # ── Fibonacci Retracement ────────────────────────────────────
    result["fibonacci"] = compute_fibonacci(df)

    # ── Pivot Points ─────────────────────────────────────────────
    result["pivot_points"] = compute_pivot_points(df)

    # ── Technical Score (0-10) ───────────────────────────────────
    result["technical_score"] = _compute_tech_score(result)
    result["tech_score"] = result["technical_score"]  # alias used by scoring.py

    return result


def compute_support_resistance(df, num_levels=3):
    """
    Identify key support and resistance levels from price history.
    Uses local minima/maxima over rolling windows.
    """
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    latest = float(close.iloc[-1])

    # Find swing highs and lows using a window
    window = min(20, len(df) // 5) if len(df) > 25 else 5
    supports = []
    resistances = []

    for i in range(window, len(df) - window):
        # Swing low = local minimum
        if low.iloc[i] == low.iloc[i-window:i+window+1].min():
            supports.append(float(low.iloc[i]))
        # Swing high = local maximum
        if high.iloc[i] == high.iloc[i-window:i+window+1].max():
            resistances.append(float(high.iloc[i]))

    # Cluster nearby levels and pick the strongest
    supports = _cluster_levels(supports, tolerance=0.02)
    resistances = _cluster_levels(resistances, tolerance=0.02)

    # Filter: supports below current price, resistances above
    supports = sorted([s for s in supports if s < latest], reverse=True)[:num_levels]
    resistances = sorted([r for r in resistances if r > latest])[:num_levels]

    return {
        "supports": [round(s, 2) for s in supports],
        "resistances": [round(r, 2) for r in resistances],
    }


def compute_fibonacci(df, lookback=100):
    """
    Compute Fibonacci retracement and extension levels from recent swing high/low.
    """
    if len(df) < 20:
        return {}
    subset = df.tail(min(lookback, len(df)))
    swing_high = float(subset["High"].max())
    swing_low = float(subset["Low"].min())
    diff = swing_high - swing_low

    if diff <= 0:
        return {}

    # Retracement levels (from high)
    retracements = {
        "0.0% (High)": round(swing_high, 2),
        "23.6%": round(swing_high - 0.236 * diff, 2),
        "38.2%": round(swing_high - 0.382 * diff, 2),
        "50.0%": round(swing_high - 0.500 * diff, 2),
        "61.8%": round(swing_high - 0.618 * diff, 2),
        "78.6%": round(swing_high - 0.786 * diff, 2),
        "100.0% (Low)": round(swing_low, 2),
    }

    # Extension levels (from low)
    extensions = {
        "127.2%": round(swing_low + 1.272 * diff, 2),
        "161.8%": round(swing_low + 1.618 * diff, 2),
        "200.0%": round(swing_low + 2.000 * diff, 2),
        "261.8%": round(swing_low + 2.618 * diff, 2),
    }

    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        "retracements": retracements,
        "extensions": extensions,
    }


def compute_pivot_points(df):
    """Compute classic pivot points from the last completed trading day."""
    if len(df) < 2:
        return {}
    prev = df.iloc[-2]
    h, l, c = float(prev["High"]), float(prev["Low"]), float(prev["Close"])
    pp = (h + l + c) / 3
    return {
        "pivot": round(pp, 2),
        "r1": round(2 * pp - l, 2),
        "r2": round(pp + (h - l), 2),
        "r3": round(h + 2 * (pp - l), 2),
        "s1": round(2 * pp - h, 2),
        "s2": round(pp - (h - l), 2),
        "s3": round(l - 2 * (h - pp), 2),
    }


# ─── HELPERS ─────────────────────────────────────────────────────

def _safe_last(series):
    """Get the last non-NaN value from a pandas Series."""
    if series is None:
        return None
    try:
        val = series.dropna().iloc[-1]
        return round(float(val), 4) if pd.notna(val) else None
    except (IndexError, TypeError):
        return None


def _compute_rsi(close, period=14):
    """Manual RSI calculation (fallback when pandas-ta unavailable)."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return _safe_last(rsi)


def _compute_atr(high, low, close, period=14):
    """Manual ATR calculation."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return _safe_last(atr)


def _cluster_levels(levels, tolerance=0.02):
    """Cluster nearby price levels and return the average of each cluster."""
    if not levels:
        return []
    levels = sorted(levels)
    clusters = [[levels[0]]]
    for level in levels[1:]:
        if abs(level - clusters[-1][-1]) / clusters[-1][-1] < tolerance:
            clusters[-1].append(level)
        else:
            clusters.append([level])
    # Return average of each cluster, weighted by count (more touches = stronger)
    result = []
    for cluster in clusters:
        result.append((sum(cluster) / len(cluster), len(cluster)))
    # Sort by number of touches (strongest first)
    result.sort(key=lambda x: -x[1])
    return [r[0] for r in result]


def _compute_tech_score(ta_data):
    """
    Compute a 0-10 technical score from computed indicators.

    8 factors, each scored 0-10:
    1. Trend (price vs 50/200 SMA)
    2. RSI (14)
    3. MACD signal
    4. Bollinger Band position
    5. S/R proximity
    6. Volume trend
    7. Fibonacci level
    8. ADX strength (or stochastic if ADX unavailable)
    """
    scores = []

    # 1. Trend: above 50 & 200 SMA = bullish
    trend_score = 5  # neutral
    if ta_data.get("above_sma200") is True:
        trend_score += 2
    elif ta_data.get("above_sma200") is False:
        trend_score -= 2
    if ta_data.get("above_sma50") is True:
        trend_score += 2
    elif ta_data.get("above_sma50") is False:
        trend_score -= 2
    if ta_data.get("golden_cross"):
        trend_score += 1
    scores.append(max(0, min(10, trend_score)))

    # 2. RSI: 30-70 neutral, <30 oversold (bullish), >70 overbought (bearish for new buys)
    rsi = ta_data.get("rsi_14")
    if rsi is not None:
        if rsi < 30:
            scores.append(8)  # oversold = buying opportunity
        elif rsi < 40:
            scores.append(7)
        elif rsi < 60:
            scores.append(5)  # neutral
        elif rsi < 70:
            scores.append(4)
        else:
            scores.append(2)  # overbought
    else:
        scores.append(5)

    # 3. MACD: bullish crossover = positive
    if ta_data.get("macd_bullish") is True:
        macd_score = 7
        if (ta_data.get("macd_histogram") or 0) > 0:
            macd_score = 8
        scores.append(macd_score)
    elif ta_data.get("macd_bullish") is False:
        scores.append(3)
    else:
        scores.append(5)

    # 4. Bollinger Band position: near lower band = opportunity, near upper = caution
    bb_pos = ta_data.get("bb_position")
    if bb_pos is not None:
        if bb_pos < 0.2:
            scores.append(8)  # near lower band
        elif bb_pos < 0.4:
            scores.append(6)
        elif bb_pos < 0.6:
            scores.append(5)  # mid-band
        elif bb_pos < 0.8:
            scores.append(4)
        else:
            scores.append(2)  # near upper band
    else:
        scores.append(5)

    # 5. Support/Resistance proximity
    sr = ta_data.get("support_resistance", {})
    supports = sr.get("supports", [])
    resistances = sr.get("resistances", [])
    latest = ta_data.get("latest_close", 0)
    sr_score = 5
    if supports and latest > 0:
        nearest_support_pct = (latest - supports[0]) / latest
        if nearest_support_pct < 0.03:
            sr_score = 7  # close to support = potential bounce
        elif nearest_support_pct < 0.05:
            sr_score = 6
    if resistances and latest > 0:
        nearest_resist_pct = (resistances[0] - latest) / latest
        if nearest_resist_pct < 0.03:
            sr_score -= 2  # close to resistance = potential rejection
    scores.append(max(0, min(10, sr_score)))

    # 6. Volume: above-average volume confirms trend
    vol_ratio = ta_data.get("volume_ratio")
    if vol_ratio is not None:
        if vol_ratio > 2.0:
            scores.append(8)  # high volume
        elif vol_ratio > 1.2:
            scores.append(6)
        elif vol_ratio > 0.8:
            scores.append(5)  # average
        else:
            scores.append(3)  # low volume = weak conviction
    else:
        scores.append(5)

    # 7. Fibonacci: price near key retracement = support
    fib = ta_data.get("fibonacci", {})
    retracements = fib.get("retracements", {})
    fib_score = 5
    if retracements and latest > 0:
        for level_name, level_price in retracements.items():
            pct_from_level = abs(latest - level_price) / latest
            if pct_from_level < 0.02:  # within 2% of a Fibonacci level
                if "61.8" in level_name or "50.0" in level_name:
                    fib_score = 7  # strong Fib level
                else:
                    fib_score = 6
                break
    scores.append(fib_score)

    # 8. ADX strength / Stochastic
    adx = ta_data.get("adx")
    if adx is not None:
        if adx > 25:
            scores.append(7)  # strong trend
        elif adx > 20:
            scores.append(6)
        else:
            scores.append(4)  # weak/no trend
    else:
        stoch_k = ta_data.get("stoch_k")
        if stoch_k is not None:
            if stoch_k < 20:
                scores.append(8)  # oversold
            elif stoch_k > 80:
                scores.append(2)  # overbought
            else:
                scores.append(5)
        else:
            scores.append(5)

    return round(sum(scores) / len(scores), 1) if scores else 5.0
