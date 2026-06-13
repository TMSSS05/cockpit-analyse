from __future__ import annotations

import pandas as pd

from app.analysis.indicators import add_all_indicators
from app.analysis.market_structure import (
    analyze_momentum,
    analyze_trend,
    analyze_volatility,
    detect_breakout,
    detect_consolidation,
    detect_sweep,
)
from app.config import settings


def compute_analysis_score(df: pd.DataFrame) -> int:
    """Score the current market setup from -10 to +10.

    Positive score = bullish bias, negative = bearish bias.
    Score magnitude indicates confidence in the bias.
    """
    if df is None or df.empty or len(df) < 50:
        return 0

    df = add_all_indicators(df)
    last = df.iloc[-1]

    trend = analyze_trend(df)
    momentum = analyze_momentum(df)
    volatility = analyze_volatility(df)
    is_consolidation = detect_consolidation(df)
    is_breakout = detect_breakout(df)
    is_sweep = detect_sweep(df)

    score = 0

    # Trend contribution (max +/-3)
    trend_scores = {
        "bullish": 3,
        "bearish": -3,
        "mixed": 0,
        "neutral": 0,
    }
    score += trend_scores.get(trend, 0)

    # Momentum contribution (max +/-3)
    momentum_scores = {
        "strong_bullish": 3,
        "weak_bullish": 1,
        "neutral": 0,
        "weak_bearish": -1,
        "strong_bearish": -3,
    }
    score += momentum_scores.get(momentum, 0)

    # Structure contribution (max +/-2)
    if trend == "bullish" and is_breakout:
        score += 2
    elif trend == "bullish" and is_consolidation:
        score += 1
    elif trend == "bullish" and is_sweep:
        score += 1
    elif trend == "bearish" and is_breakout:
        score -= 2
    elif trend == "bearish" and is_consolidation:
        score -= 1
    elif trend == "bearish" and is_sweep:
        score -= 1

    # RSI extreme contribution (max +/-1)
    rsi = last.get("rsi", 50)
    if rsi is not None and not pd.isna(rsi):
        if rsi > settings.RSI_EXTREME_HIGH:
            score -= 1  # Overbought = potential pullback or reversal
        elif rsi < settings.RSI_EXTREME_LOW:
            score += 1  # Oversold = potential bounce

    # Volatility adjustment (max +/-1)
    vol_adjustments = {
        "extreme": -1,  # Extreme = lower confidence
        "high": 0,
        "normal": 1,
        "low": 0,
    }
    score += vol_adjustments.get(volatility, 0)

    # Clamp to [-10, 10]
    return max(-10, min(10, score))


def score_to_label(score: int) -> str:
    if score >= 7:
        return "strong_bullish"
    if score >= 4:
        return "bullish"
    if score >= 1:
        return "slightly_bullish"
    if score >= -1:
        return "neutral"
    if score >= -4:
        return "slightly_bearish"
    if score >= -7:
        return "bearish"
    return "strong_bearish"


def score_to_action_bias(score: int) -> str:
    if score >= 4:
        return "Look for long opportunities"
    if score >= 1:
        return "Lean bullish, wait for confirmation"
    if score >= -1:
        return "No clear bias, wait for setup"
    if score >= -4:
        return "Lean bearish, wait for confirmation"
    return "Look for short opportunities"
