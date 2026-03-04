"""
Composite Scoring Engine — Combines fundamental, technical, and sentiment analysis.

Weighting: 40% Fundamental + 30% Technical + 30% Sentiment → 0-10 score.
Each sub-score is computed from its own set of factors, all scored 0-10.
Final score maps to a rating: Buy / Watch·Hold / Sell.

Usage:
    from scripts.scoring import compute_composite_score

    score = compute_composite_score(
        fundamentals=fundamentals_data,
        technicals=technicals_data,
        sentiment=sentiment_data,
        analyst=analyst_data,
        insider=insider_data,
        congress=congress_data,
        tradingview=tradingview_data,
        earnings=earnings_data,
    )
"""
import os, sys

_project_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


# ═══════════════════════════════════════════════════════════════════
#  RATING THRESHOLDS
# ═══════════════════════════════════════════════════════════════════

RATING_MAP = {
    "STRONG_BUY": (8.0, 10.0),
    "BUY":        (6.5, 8.0),
    "WATCH":      (5.0, 6.5),
    "HOLD":       (3.5, 5.0),
    "SELL":       (0.0, 3.5),
}


def score_to_rating(score):
    """Map a 0-10 composite score to a human-readable rating."""
    if score >= 8.0:
        return "STRONG BUY"
    elif score >= 6.5:
        return "BUY"
    elif score >= 5.0:
        return "WATCH·HOLD"
    elif score >= 3.5:
        return "HOLD"
    else:
        return "SELL"


def score_to_confidence(factor_scores):
    """
    Compute confidence level based on how many factors have real data
    vs. defaulting to neutral (5.0).

    Returns: "HIGH" / "MEDIUM" / "LOW"
    """
    if not factor_scores:
        return "LOW"
    total = len(factor_scores)
    non_default = sum(1 for s in factor_scores if abs(s - 5.0) > 0.1)
    ratio = non_default / total
    if ratio >= 0.7:
        return "HIGH"
    elif ratio >= 0.4:
        return "MEDIUM"
    return "LOW"


# ═══════════════════════════════════════════════════════════════════
#  FUNDAMENTAL SCORE  (40% weight, 10 factors)
# ═══════════════════════════════════════════════════════════════════

def _score_fundamental(fundamentals, analyst=None, insider=None, earnings=None):
    """
    Compute fundamental score from 10 factors, each 0-10.

    Factors:
    1. PE ratio (value)         6. Debt-to-Equity (risk)
    2. PB ratio (value)         7. Free Cash Flow (health)
    3. Revenue growth (growth)  8. Return on Equity (efficiency)
    4. EPS growth (growth)      9. Analyst consensus (expert)
    5. Profit margin (quality) 10. Earnings surprises (momentum)
    """
    scores = []
    details = {}

    f = fundamentals or {}
    an = analyst or {}
    ins = insider or {}
    ear = earnings or {}

    # --- 1. PE Ratio (lower = better value, but negative = no earnings) ---
    pe = f.get("pe_ratio") or f.get("forward_pe")
    if pe is not None:
        if pe < 0:
            s, rn = 3, "Negative earnings — company is unprofitable"
        elif pe < 10:
            s, rn = 9, "Deep value — trading well below market average"
        elif pe < 15:
            s, rn = 8, "Attractive — below market average (~20x)"
        elif pe < 20:
            s, rn = 7, "Fair value — near market average"
        elif pe < 25:
            s, rn = 6, "Slightly elevated — above average but reasonable"
        elif pe < 30:
            s, rn = 5, "Elevated — premium valuation"
        elif pe < 40:
            s, rn = 4, "Expensive — high growth expectations priced in"
        elif pe < 60:
            s, rn = 3, "Very expensive — significant downside risk"
        else:
            s, rn = 2, "Extremely expensive — speculative valuation"
        scores.append(s)
        details["pe_ratio"] = {"value": round(pe, 2), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["pe_ratio"] = {"value": None, "score": 5, "note": "No data (neutral)", "rating_note": "No data available"}

    # --- 2. PB Ratio (lower = better value) ---
    pb = f.get("pb_ratio")
    if pb is not None:
        if pb < 1:
            s, rn = 9, "Below book value — deep value opportunity"
        elif pb < 2:
            s, rn = 7, "Reasonable — near book value"
        elif pb < 3:
            s, rn = 6, "Fair — modest premium to book"
        elif pb < 5:
            s, rn = 5, "Elevated — significant premium to book"
        elif pb < 10:
            s, rn = 4, "Expensive — asset-light or high-growth business"
        else:
            s, rn = 2, "Very expensive relative to book value"
        scores.append(s)
        details["pb_ratio"] = {"value": round(pb, 2), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["pb_ratio"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 3. Revenue Growth (higher = better) ---
    rev_g = f.get("revenue_growth")
    if rev_g is not None:
        pct = rev_g * 100 if abs(rev_g) < 5 else rev_g  # handle decimal vs pct
        if pct > 40:
            s, rn = 10, "Hyper-growth — exceptional revenue expansion"
        elif pct > 25:
            s, rn = 9, "Very strong growth — rapidly expanding"
        elif pct > 15:
            s, rn = 8, "Strong growth — well above average"
        elif pct > 8:
            s, rn = 7, "Healthy growth — above GDP growth"
        elif pct > 3:
            s, rn = 6, "Modest growth — in line with economy"
        elif pct > 0:
            s, rn = 5, "Minimal growth — barely expanding"
        elif pct > -5:
            s, rn = 4, "Slight contraction — revenue declining"
        elif pct > -15:
            s, rn = 3, "Significant contraction — shrinking business"
        else:
            s, rn = 1, "Deep contraction — severe revenue decline"
        scores.append(s)
        details["revenue_growth"] = {"value": round(pct, 1), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["revenue_growth"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 4. EPS Growth (higher = better) ---
    eps_g = f.get("earnings_growth")
    if eps_g is not None:
        pct = eps_g * 100 if abs(eps_g) < 5 else eps_g
        if pct > 40:
            s, rn = 10, "Exceptional earnings growth"
        elif pct > 25:
            s, rn = 9, "Very strong earnings expansion"
        elif pct > 15:
            s, rn = 8, "Strong earnings growth"
        elif pct > 8:
            s, rn = 7, "Healthy earnings growth"
        elif pct > 0:
            s, rn = 6, "Modest earnings growth"
        elif pct > -10:
            s, rn = 4, "Earnings declining — watch closely"
        elif pct > -25:
            s, rn = 3, "Significant earnings drop"
        else:
            s, rn = 1, "Severe earnings contraction"
        scores.append(s)
        details["eps_growth"] = {"value": round(pct, 1), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["eps_growth"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 5. Profit Margin (higher = better quality) ---
    margin = f.get("profit_margin") or f.get("operating_margin")
    if margin is not None:
        pct = margin * 100 if abs(margin) < 1 else margin
        if pct > 30:
            s, rn = 9, "Exceptional margins — high-quality business"
        elif pct > 20:
            s, rn = 8, "Strong margins — competitive advantage"
        elif pct > 10:
            s, rn = 7, "Healthy margins — solid profitability"
        elif pct > 5:
            s, rn = 6, "Modest margins — typical for sector"
        elif pct > 0:
            s, rn = 5, "Thin margins — low pricing power"
        elif pct > -10:
            s, rn = 3, "Negative margins — losing money"
        else:
            s, rn = 1, "Deep losses — unsustainable without capital"
        scores.append(s)
        details["profit_margin"] = {"value": round(pct, 1), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["profit_margin"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 6. Debt-to-Equity (lower = safer) ---
    de = f.get("debt_to_equity")
    if de is not None:
        # yfinance reports D/E as a ratio (sometimes *100)
        de_ratio = de / 100 if de > 10 else de
        if de_ratio < 0.3:
            s, rn = 9, "Very low debt — conservative balance sheet"
        elif de_ratio < 0.5:
            s, rn = 8, "Low debt — strong financial position"
        elif de_ratio < 1.0:
            s, rn = 7, "Moderate debt — manageable leverage"
        elif de_ratio < 1.5:
            s, rn = 6, "Above-average debt — monitor interest costs"
        elif de_ratio < 2.0:
            s, rn = 5, "High debt — elevated financial risk"
        elif de_ratio < 3.0:
            s, rn = 3, "Very high debt — vulnerable to rate hikes"
        else:
            s, rn = 2, "Extremely leveraged — significant default risk"
        scores.append(s)
        details["debt_to_equity"] = {"value": round(de_ratio, 2), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["debt_to_equity"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 7. Free Cash Flow (positive and growing = healthy) ---
    fcf = f.get("free_cash_flow")
    if fcf is not None:
        # Normalize to billions for readability
        fcf_b = fcf / 1e9
        if fcf_b > 10:
            s, rn = 9, "Exceptional cash generation — >$10B FCF"
        elif fcf_b > 5:
            s, rn = 8, "Strong cash flow — well-funded operations"
        elif fcf_b > 1:
            s, rn = 7, "Healthy cash flow — self-funding growth"
        elif fcf_b > 0.1:
            s, rn = 6, "Positive but modest cash flow"
        elif fcf_b > 0:
            s, rn = 5, "Barely positive cash flow"
        else:
            s, rn = 2, "Negative FCF — burning cash"
        scores.append(s)
        details["free_cash_flow"] = {"value": f"${fcf_b:.2f}B", "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["free_cash_flow"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 8. Return on Equity (higher = more efficient) ---
    roe = f.get("roe")
    if roe is not None:
        pct = roe * 100 if abs(roe) < 1 else roe
        if pct > 30:
            s, rn = 9, "Exceptional ROE — very efficient capital use"
        elif pct > 20:
            s, rn = 8, "Strong ROE — above-average efficiency"
        elif pct > 15:
            s, rn = 7, "Healthy ROE — good capital allocation"
        elif pct > 10:
            s, rn = 6, "Adequate ROE — near market average"
        elif pct > 5:
            s, rn = 5, "Below-average ROE"
        elif pct > 0:
            s, rn = 4, "Low ROE — weak capital efficiency"
        else:
            s, rn = 2, "Negative ROE — destroying shareholder value"
        scores.append(s)
        details["roe"] = {"value": round(pct, 1), "score": s, "rating_note": rn}
    else:
        scores.append(5)
        details["roe"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No data available"}

    # --- 9. Analyst Consensus ---
    if an:
        buy = an.get("buy", 0) + an.get("strong_buy", 0)
        hold = an.get("hold", 0)
        sell = an.get("sell", 0) + an.get("strong_sell", 0)
        total = buy + hold + sell
        if total > 0:
            buy_pct = buy / total
            if buy_pct > 0.7:
                s, rn = 9, "Strong buy consensus — 70%+ analysts bullish"
            elif buy_pct > 0.5:
                s, rn = 7, "Majority buy — over half of analysts bullish"
            elif buy_pct > 0.3:
                s, rn = 5, "Mixed — analysts divided"
            else:
                s, rn = 3, "Bearish consensus — majority hold/sell"
            scores.append(s)
            details["analyst_consensus"] = {
                "buy": buy, "hold": hold, "sell": sell,
                "buy_pct": round(buy_pct * 100, 1), "score": s,
                "rating_note": rn,
            }
        else:
            scores.append(5)
            details["analyst_consensus"] = {"value": None, "score": 5, "note": "No analyst data", "rating_note": "No analyst coverage"}
    else:
        # Try yfinance recommendation key
        rec = f.get("recommendation", "")
        if rec:
            rec_map = {"strong_buy": 9, "buy": 8, "overweight": 7, "hold": 5, "underweight": 4, "sell": 3, "strong_sell": 2}
            rn_map = {"strong_buy": "Strong buy", "buy": "Buy", "overweight": "Overweight", "hold": "Hold", "underweight": "Underweight", "sell": "Sell", "strong_sell": "Strong sell"}
            s = rec_map.get(rec.lower(), 5)
            rn = rn_map.get(rec.lower(), rec)
            scores.append(s)
            details["analyst_consensus"] = {"recommendation": rec, "score": s, "rating_note": rn}
        else:
            scores.append(5)
            details["analyst_consensus"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No analyst data available"}

    # --- 10. Earnings Surprises (positive surprises = good execution) ---
    if ear:
        surprise_avg = ear.get("surprise_avg", 0)
        beat_count = ear.get("beat_count", 0)
        miss_count = ear.get("miss_count", 0)
        total_e = beat_count + miss_count
        if total_e > 0:
            beat_ratio = beat_count / total_e
            if beat_ratio >= 0.8 and surprise_avg > 5:
                s, rn = 9, "Consistently beats estimates by wide margin"
            elif beat_ratio >= 0.6:
                s, rn = 7, "Usually beats estimates — reliable execution"
            elif beat_ratio >= 0.4:
                s, rn = 5, "Mixed track record — hits and misses"
            else:
                s, rn = 3, "Frequently misses estimates — poor visibility"
            scores.append(s)
            details["earnings_surprises"] = {
                "beat_count": beat_count, "miss_count": miss_count,
                "surprise_avg_pct": round(surprise_avg, 2), "score": s,
                "rating_note": rn,
            }
        else:
            scores.append(5)
            details["earnings_surprises"] = {"value": None, "score": 5, "note": "No earnings data", "rating_note": "No earnings data"}
    else:
        scores.append(5)
        details["earnings_surprises"] = {"value": None, "score": 5, "note": "No data", "rating_note": "No earnings data available"}

    avg = round(sum(scores) / len(scores), 2) if scores else 5.0
    return {
        "fundamental_score": avg,
        "factor_scores": scores,
        "factor_details": details,
        "confidence": score_to_confidence(scores),
    }


# ═══════════════════════════════════════════════════════════════════
#  SENTIMENT SCORE  (30% weight, 7 factors)
# ═══════════════════════════════════════════════════════════════════

def _score_sentiment(reddit=None, stocktwits=None, news=None, rss=None,
                     insider=None, congress=None, tradingview=None):
    """
    Compute sentiment score from 7 factors, each 0-10.

    Factors:
    1. Reddit mentions & trend        5. RSS buzz / mention count
    2. StockTwits bull/bear ratio      6. Insider buy/sell ratio
    3. News sentiment (AI-scored)      7. Congress trade activity
    4. TradingView consensus
    """
    scores = []
    details = {}

    # --- 1. Reddit Mentions (ApeWisdom) ---
    rd = reddit or {}
    mentions = rd.get("mentions", 0)
    mentions_prior = rd.get("mentions_24h_ago", 0)
    if mentions > 0:
        # Trending up = bullish social sentiment
        trend = mentions / max(mentions_prior, 1)
        rank = rd.get("rank")
        if rank and rank <= 10:
            s, rn = 8, f"Top 10 trending (#{rank}) — high retail interest"
        elif trend > 2.0:
            s, rn = 8, "Mentions doubling — surging interest"
        elif trend > 1.3:
            s, rn = 7, "Mentions rising — growing attention"
        elif trend > 1.0:
            s, rn = 6, "Stable mentions — steady interest"
        elif trend > 0.7:
            s, rn = 5, "Mentions declining slightly"
        else:
            s, rn = 4, "Mentions dropping — fading interest"
        scores.append(s)
        details["reddit_sentiment"] = {
            "mentions": mentions, "trend": round(trend, 2),
            "rank": rank, "score": s,
            "source": "ApeWisdom", "rating_note": rn,
        }
    else:
        scores.append(5)
        details["reddit_sentiment"] = {"value": None, "score": 5, "note": "Not trending on Reddit", "source": "ApeWisdom", "rating_note": "Not trending on Reddit"}

    # --- 2. StockTwits Bull/Bear ---
    st = stocktwits or {}
    bull_pct = st.get("bull_pct", 50)
    msg_count = st.get("messages_count", 0)
    if msg_count > 0:
        if bull_pct > 80:
            s, rn = 9, f"Very bullish — {bull_pct:.0f}% bull sentiment"
        elif bull_pct > 65:
            s, rn = 7, f"Bullish — {bull_pct:.0f}% bull sentiment"
        elif bull_pct > 50:
            s, rn = 6, f"Slightly bullish — {bull_pct:.0f}% bull"
        elif bull_pct > 35:
            s, rn = 4, f"Bearish lean — only {bull_pct:.0f}% bull"
        else:
            s, rn = 2, f"Very bearish — only {bull_pct:.0f}% bull"
        scores.append(s)
        details["stocktwits_sentiment"] = {
            "bull_pct": bull_pct, "messages": msg_count, "score": s,
            "source": "StockTwits", "rating_note": rn,
        }
    else:
        scores.append(5)
        details["stocktwits_sentiment"] = {"value": None, "score": 5, "note": "No StockTwits data", "source": "StockTwits", "rating_note": "No data — possibly rate limited"}

    # --- 3. News Sentiment (Alpha Vantage AI-scored, -1 to +1) ---
    nw = news or {}
    avg_sent = nw.get("avg_sentiment")
    article_count = nw.get("article_count", 0)
    news_source = nw.get("source", "Alpha Vantage")
    if avg_sent is not None and article_count > 0:
        # Map -1..+1 to 0..10
        s = round(max(0, min(10, (avg_sent + 1) * 5)), 1)
        if avg_sent > 0.25:
            rn = f"Positive coverage — avg sentiment {avg_sent:+.2f}"
        elif avg_sent > 0.1:
            rn = f"Mildly positive — avg sentiment {avg_sent:+.2f}"
        elif avg_sent > -0.1:
            rn = f"Neutral coverage — avg sentiment {avg_sent:+.2f}"
        elif avg_sent > -0.25:
            rn = f"Mildly negative — avg sentiment {avg_sent:+.2f}"
        else:
            rn = f"Negative coverage — avg sentiment {avg_sent:+.2f}"
        scores.append(s)
        details["news_sentiment"] = {
            "avg_sentiment": round(avg_sent, 3), "articles": article_count, "score": s,
            "source": news_source, "rating_note": rn,
        }
    elif article_count > 0:
        # We have articles but no AI sentiment (Finnhub free tier)
        # More coverage = more attention (neutral-positive)
        s = min(7, 5 + article_count / 10)
        s = round(s, 1)
        rn = f"{article_count} articles found — no AI sentiment available"
        scores.append(s)
        details["news_sentiment"] = {
            "articles": article_count, "score": s,
            "source": news_source, "rating_note": rn, "note": "No AI sentiment, using article count",
        }
    else:
        scores.append(5)
        details["news_sentiment"] = {"value": None, "score": 5, "source": news_source, "rating_note": "No news data available", "note": "No news data"}

    # --- 4. TradingView Consensus (cross-check from 26 indicators) ---
    tv = tradingview or {}
    tv_rec = tv.get("recommendation", "")
    if tv_rec:
        tv_map = {
            "STRONG_BUY": 9, "BUY": 7.5, "NEUTRAL": 5,
            "SELL": 3, "STRONG_SELL": 1.5,
        }
        rn_map = {
            "STRONG_BUY": "Strong buy — most indicators bullish",
            "BUY": "Buy — majority of indicators bullish",
            "NEUTRAL": "Neutral — indicators mixed",
            "SELL": "Sell — majority of indicators bearish",
            "STRONG_SELL": "Strong sell — most indicators bearish",
        }
        s = tv_map.get(tv_rec, 5)
        buy_c = tv.get("buy_count", 0)
        sell_c = tv.get("sell_count", 0)
        neut_c = tv.get("neutral_count", 0)
        rn = rn_map.get(tv_rec, tv_rec)
        if buy_c + sell_c + neut_c > 0:
            rn += f" ({buy_c}B/{neut_c}N/{sell_c}S)"
        scores.append(s)
        details["tradingview_consensus"] = {
            "recommendation": tv_rec,
            "buy_count": buy_c,
            "sell_count": sell_c,
            "neutral_count": neut_c,
            "score": s,
            "source": "TradingView (tradingview-ta)", "rating_note": rn,
        }
    else:
        scores.append(5)
        details["tradingview_consensus"] = {"value": None, "score": 5, "source": "TradingView (tradingview-ta)", "rating_note": "No TradingView data available", "note": "No TradingView data"}

    # --- 5. RSS Buzz (Seeking Alpha + news feeds) ---
    rs = rss or {}
    rss_mentions = rs.get("mention_count", 0)
    rss_articles = rs.get("articles", [])
    if rss_mentions > 0 or rss_articles:
        count = rss_mentions or len(rss_articles)
        if count > 10:
            s, rn = 8, f"Heavily discussed — {count} mentions across feeds"
        elif count > 5:
            s, rn = 7, f"Good coverage — {count} mentions"
        elif count > 2:
            s, rn = 6, f"Some coverage — {count} mentions"
        else:
            s, rn = 5, f"Minimal coverage — {count} mention(s)"
        scores.append(s)
        details["rss_buzz"] = {"mention_count": count, "score": s, "source": "Seeking Alpha / RSS feeds", "rating_note": rn}
    else:
        scores.append(5)
        details["rss_buzz"] = {"value": None, "score": 5, "source": "Seeking Alpha / RSS feeds", "rating_note": "No RSS mentions found", "note": "No RSS mentions"}

    # --- 6. Insider Activity (buy/sell ratio) ---
    ins = insider or {}
    ins_buys = ins.get("buys_last_50", 0)
    ins_sells = ins.get("sells_last_50", 0)
    ins_signal = ins.get("net_insider_signal", "")
    if ins_buys + ins_sells > 0:
        ratio = ins_buys / max(ins_buys + ins_sells, 1)
        if ratio > 0.7:
            s, rn = 9, f"Heavy insider buying — {ins_buys} buys vs {ins_sells} sells"
        elif ratio > 0.5:
            s, rn = 7, f"Net insider buying — {ins_buys} buys vs {ins_sells} sells"
        elif ratio > 0.3:
            s, rn = 5, f"Mixed insider activity — {ins_buys} buys vs {ins_sells} sells"
        else:
            s, rn = 3, f"Heavy insider selling — {ins_buys} buys vs {ins_sells} sells"
        scores.append(s)
        details["insider_activity"] = {
            "buys": ins_buys, "sells": ins_sells,
            "signal": ins_signal, "score": s,
            "source": "Finnhub", "rating_note": rn,
        }
    else:
        scores.append(5)
        details["insider_activity"] = {"value": None, "score": 5, "source": "Finnhub", "rating_note": "No insider trade data available", "note": "No insider data"}

    # --- 7. Congress Trades ---
    cong = congress or {}
    trades = cong.get("congress_trades", [])
    if isinstance(trades, list) and trades:
        buys = sum(1 for t in trades[:20] if "purchase" in str(t.get("type", "")).lower() or "buy" in str(t.get("type", "")).lower())
        sells = sum(1 for t in trades[:20] if "sale" in str(t.get("type", "")).lower() or "sell" in str(t.get("type", "")).lower())
        total_ct = buys + sells
        if total_ct > 0:
            buy_ratio = buys / total_ct
            if buy_ratio > 0.6:
                s, rn = 8, f"Congress members buying — {buys} buys vs {sells} sells"
            elif buy_ratio > 0.4:
                s, rn = 6, f"Mixed Congress activity — {buys} buys vs {sells} sells"
            else:
                s, rn = 3, f"Congress members selling — {buys} buys vs {sells} sells"
        else:
            s, rn = 5, "Congress trades found but no clear buy/sell signal"
        scores.append(s)
        details["congress_trades"] = {"buys": buys, "sells": sells, "score": s, "source": "Mboum Finance", "rating_note": rn}
    else:
        scores.append(5)
        details["congress_trades"] = {"value": None, "score": 5, "source": "Mboum Finance", "rating_note": "No Congress trade data available", "note": "No Congress data"}

    avg = round(sum(scores) / len(scores), 2) if scores else 5.0
    return {
        "sentiment_score": avg,
        "factor_scores": scores,
        "factor_details": details,
        "confidence": score_to_confidence(scores),
    }


# ═══════════════════════════════════════════════════════════════════
#  COMPOSITE SCORE  (40/30/30)
# ═══════════════════════════════════════════════════════════════════

def compute_composite_score(fundamentals=None, technicals=None, sentiment_data=None,
                            analyst=None, insider=None, congress=None,
                            tradingview=None, earnings=None,
                            reddit=None, stocktwits=None, news=None, rss=None,
                            weight_fundamental=0.40, weight_technical=0.30,
                            weight_sentiment=0.30,
                            sector_modifier=0.0):
    """
    Compute a composite 0-10 score from fundamental, technical, and sentiment inputs.

    The technical score comes pre-computed from technical_analysis.py.
    Fundamental and sentiment scores are computed here from raw API data.

    Args:
        fundamentals: Dict from yfinance_fundamentals() or similar
        technicals:   Dict from compute_technicals() — must contain "tech_score"
        analyst:      Dict from finnhub_analyst_ratings() or similar
        insider:      Dict from sec_insider_trades() or similar
        congress:     Dict from mboum_congress_trades() or similar
        tradingview:  Dict from tradingview_consensus()
        earnings:     Dict from finnhub_earnings()
        reddit:       Dict from apewisdom_reddit_sentiment()
        stocktwits:   Dict from stocktwits_sentiment()
        news:         Dict from alpha_vantage_news_sentiment() or finnhub_news_sentiment()
        rss:          Dict with RSS article mentions
        weight_*:     Override default weights (must sum to 1.0)

    Returns:
        dict with composite_score, rating, sub-scores, and full factor breakdown
    """
    # Validate weights
    total_weight = weight_fundamental + weight_technical + weight_sentiment
    if abs(total_weight - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

    # --- Fundamental sub-score ---
    fund_result = _score_fundamental(fundamentals, analyst, insider, earnings)
    fund_score = fund_result["fundamental_score"]

    # --- Technical sub-score (pre-computed) ---
    tech_score = 5.0
    tech_details = {}
    if technicals:
        tech_score = technicals.get("tech_score", 5.0)
        tech_details = {
            "tech_score": tech_score,
            "rsi": technicals.get("rsi_14"),
            "macd_bullish": technicals.get("macd_bullish"),
            "above_sma50": technicals.get("above_sma50"),
            "above_sma200": technicals.get("above_sma200"),
            "bb_position": technicals.get("bb_position"),
            "volume_ratio": technicals.get("volume_ratio"),
            "adx": technicals.get("adx"),
        }

    # --- Sentiment sub-score ---
    sent_result = _score_sentiment(
        reddit=reddit, stocktwits=stocktwits, news=news,
        rss=rss, insider=insider, congress=congress,
        tradingview=tradingview,
    )
    sent_score = sent_result["sentiment_score"]

    # --- Weighted composite ---
    composite = (
        fund_score * weight_fundamental +
        tech_score * weight_technical +
        sent_score * weight_sentiment
    )

    # --- Sector rotation modifier (tailwind/headwind) ---
    # Clamp to -0.5 to +0.5 range, then apply
    sector_mod = max(-0.5, min(0.5, sector_modifier))
    composite += sector_mod
    composite = round(max(0.0, min(10.0, composite)), 2)  # clamp to 0-10

    # --- Overall confidence ---
    all_factor_scores = (
        fund_result["factor_scores"] +
        [tech_score] +
        sent_result["factor_scores"]
    )
    confidence = score_to_confidence(all_factor_scores)

    rating = score_to_rating(composite)

    return {
        "composite_score": composite,
        "rating": rating,
        "confidence": confidence,
        "sector_modifier": sector_mod,
        "weights": {
            "fundamental": weight_fundamental,
            "technical": weight_technical,
            "sentiment": weight_sentiment,
        },
        "sub_scores": {
            "fundamental": {
                "score": fund_score,
                "weight": weight_fundamental,
                "weighted": round(fund_score * weight_fundamental, 2),
                "confidence": fund_result["confidence"],
                "factors": fund_result["factor_details"],
            },
            "technical": {
                "score": tech_score,
                "weight": weight_technical,
                "weighted": round(tech_score * weight_technical, 2),
                "confidence": "HIGH" if technicals else "LOW",
                "factors": tech_details,
            },
            "sentiment": {
                "score": sent_score,
                "weight": weight_sentiment,
                "weighted": round(sent_score * weight_sentiment, 2),
                "confidence": sent_result["confidence"],
                "factors": sent_result["factor_details"],
            },
        },
    }


# ═══════════════════════════════════════════════════════════════════
#  QUICK SCORE (for scanners — lighter weight, fewer API calls)
# ═══════════════════════════════════════════════════════════════════

def compute_quick_score(fundamentals=None, technicals=None, tradingview=None):
    """
    Compute a fast approximate score using only yfinance + TradingView.
    Good for scanning many tickers quickly without burning API quota.

    Base weighting: 50% fundamental + 30% technical + 20% TradingView.
    When a data source is entirely missing, its weight is redistributed
    proportionally among the sources that *did* return data so that a
    failed API call doesn't drag the score to a flat 5.0.

    Returns dict with quick_score, rating, per-source scores, and
    ``sources_used`` / ``sources_missing`` lists for transparency.
    """
    # ── Fundamental quick check (PE, growth, margin) ──
    has_fund = fundamentals is not None and len(fundamentals) > 0
    f = fundamentals or {}
    fund_scores = []

    pe = f.get("pe_ratio") or f.get("forward_pe")
    if pe is not None and pe > 0:
        s = max(2, min(9, 10 - pe / 5))
        fund_scores.append(round(s, 1))
    else:
        fund_scores.append(5)

    rev_g = f.get("revenue_growth")
    if rev_g is not None:
        pct = rev_g * 100 if abs(rev_g) < 5 else rev_g
        s = max(1, min(10, 5 + pct / 5))
        fund_scores.append(round(s, 1))
    else:
        fund_scores.append(5)

    margin = f.get("profit_margin")
    if margin is not None:
        pct = margin * 100 if abs(margin) < 1 else margin
        s = max(1, min(9, 4 + pct / 5))
        fund_scores.append(round(s, 1))
    else:
        fund_scores.append(5)

    fund_avg = sum(fund_scores) / len(fund_scores)

    # ── Technical (pre-computed) ──
    has_tech = technicals is not None and len(technicals) > 0
    tech = technicals.get("tech_score", 5.0) if has_tech else 5.0

    # ── TradingView ──
    has_tv = tradingview is not None and len(tradingview) > 0
    tv_score = 5.0
    tv = tradingview or {}
    tv_rec = tv.get("recommendation", "")
    if tv_rec:
        tv_map = {"STRONG_BUY": 9, "BUY": 7.5, "NEUTRAL": 5, "SELL": 3, "STRONG_SELL": 1.5}
        tv_score = tv_map.get(tv_rec, 5)

    # ── Weighted composite with redistribution ──
    # Only include sources that actually returned data.  If a source is
    # missing its weight is redistributed proportionally to the others.
    weight_map = {"fundamental": 0.50, "technical": 0.30, "tradingview": 0.20}
    score_map = {"fundamental": fund_avg, "technical": tech, "tradingview": tv_score}
    available = {"fundamental": has_fund, "technical": has_tech, "tradingview": has_tv}

    sources_used = [k for k, v in available.items() if v]
    sources_missing = [k for k, v in available.items() if not v]

    if sources_used:
        total_weight = sum(weight_map[k] for k in sources_used)
        composite = sum(
            score_map[k] * (weight_map[k] / total_weight)
            for k in sources_used
        )
    else:
        # All sources failed — return neutral 5.0
        composite = 5.0

    composite = round(composite, 2)

    return {
        "quick_score": composite,
        "rating": score_to_rating(composite),
        "confidence": "LOW" if len(sources_used) <= 1 else "MEDIUM",
        "fundamental_avg": round(fund_avg, 2),
        "technical": tech,
        "tradingview": tv_score,
        "sources_used": sources_used,
        "sources_missing": sources_missing,
        "note": "Quick score — use full analysis for investment decisions",
    }


# ═══════════════════════════════════════════════════════════════════
#  PORTFOLIO ACTION MAPPER
# ═══════════════════════════════════════════════════════════════════

def score_to_portfolio_action(score, current_holding=False):
    """
    Map composite score to portfolio action for the Weekly Review use case.

    Returns one of: BUY / HOLD / TRIM / SELL (for existing holdings)
    Or: BUY / WATCH / PASS (for scanner candidates)
    """
    rating = score_to_rating(score)

    if current_holding:
        if rating == "STRONG BUY":
            return "BUY MORE"
        elif rating == "BUY":
            return "HOLD"
        elif rating == "WATCH·HOLD":
            return "HOLD"
        elif rating == "HOLD":
            return "TRIM"
        else:
            return "SELL"
    else:
        if rating in ("STRONG BUY", "BUY"):
            return "BUY"
        elif rating == "WATCH·HOLD":
            return "WATCH"
        else:
            return "PASS"
