from __future__ import annotations

from typing import Literal

import pandas as pd

from app.analysis.indicators import add_all_indicators
from app.analysis.levels import compute_all_levels, get_closest_level
from app.analysis.market_structure import (
    analyze_momentum,
    analyze_trend,
    analyze_volatility,
    detect_breakout,
    detect_consolidation,
    detect_sweep,
)

ScenarioType = Literal[
    "breakout_bullish",
    "breakout_bearish",
    "range_high_break",
    "range_low_break",
    "sweep_bullish",
    "sweep_bearish",
    "consolidation_bullish_resolve",
    "consolidation_bearish_resolve",
    "pullback_bullish_continuation",
    "pullback_bearish_continuation",
    "reversal_bullish",
    "reversal_bearish",
]


def generate_scenarios(df: pd.DataFrame) -> list[dict]:
    """Generate trade scenarios for the current market setup.

    Returns a list of scenarios with type, direction, entry trigger,
    invalidation condition, and confidence rating.
    """
    if df is None or df.empty or len(df) < 50:
        return []

    df = add_all_indicators(df)
    last = df.iloc[-1]
    price = last["close"]

    trend = analyze_trend(df)
    momentum = analyze_momentum(df)
    volatility = analyze_volatility(df)
    is_consolidation = detect_consolidation(df)
    is_breakout = detect_breakout(df)
    is_sweep = detect_sweep(df)

    levels = compute_all_levels(df)
    closest_level = get_closest_level(price, levels)

    scenarios = []

    # Scenario 1: Breakout continuation
    if trend == "bullish" and is_breakout and momentum in ("weak_bullish", "strong_bullish"):
        scenarios.append(_make_scenario(
            "breakout_bullish", "long", "Breakout with bullish alignment",
            "Pullback to broken resistance now support",
            "Close below breakout candle low", "high", price,
        ))
    elif trend == "bearish" and is_breakout and momentum in ("weak_bearish", "strong_bearish"):
        scenarios.append(_make_scenario(
            "breakout_bearish", "short", "Breakout with bearish alignment",
            "Pullback to broken support now resistance",
            "Close above breakout candle high", "high", price,
        ))

    # Scenario 2: Range plays with closest level
    if is_consolidation and closest_level:
        if closest_level["price"] > price:
            scenarios.append(_make_scenario(
                "range_high_break", "long", "Range play to resistance",
                f"Ride to {closest_level['type']} at {closest_level['price']:.2f}",
                "Close below range low", "medium", price,
            ))
        else:
            scenarios.append(_make_scenario(
                "range_low_break", "short", "Range play to support",
                f"Ride to {closest_level['type']} at {closest_level['price']:.2f}",
                "Close above range high", "medium", price,
            ))

    # Scenario 3: Sweep reversal
    if is_sweep:
        if trend == "bullish" or "bull" in momentum:
            scenarios.append(_make_scenario(
                "sweep_bullish", "long", "Sweep of low, bullish reversal",
                "Liquidity grab confirmed, look for buy entry",
                "Close below sweep low", "medium", price,
            ))
        elif trend == "bearish" or "bear" in momentum:
            scenarios.append(_make_scenario(
                "sweep_bearish", "short", "Sweep of high, bearish reversal",
                "Liquidity grab confirmed, look for sell entry",
                "Close above sweep high", "medium", price,
            ))

    # Scenario 4: Pullback in trend
    if trend == "bullish" and "bear" in momentum:
        scenarios.append(_make_scenario(
            "pullback_bullish_continuation",
            "long",
            "Bullish pullback entry",
            "Price pulling back in uptrend, look for support holds",
            "Close below recent swing low",
            "medium",
            price,
        ))
    elif trend == "bearish" and "bull" in momentum:
        scenarios.append(_make_scenario(
            "pullback_bearish_continuation",
            "short",
            "Bearish pullback entry",
            "Price pulling back in downtrend, look for resistance holds",
            "Close above recent swing high",
            "medium",
            price,
        ))

    # Scenario 5: Reversal at extremes
    if volatility == "extreme" and momentum == "strong_bullish":
        scenarios.append(_make_scenario(
            "reversal_bearish",
            "short",
            "Exhaustion after strong bullish move",
            "Extended move with extreme volatility — potential reversal",
            "New high with same momentum",
            "low",
            price,
        ))
    elif volatility == "extreme" and momentum == "strong_bearish":
        scenarios.append(_make_scenario(
            "reversal_bullish",
            "long",
            "Exhaustion after strong bearish move",
            "Extended move with extreme volatility — potential reversal",
            "New low with same momentum",
            "low",
            price,
        ))

    # Scenario 6: Consolidation resolution
    if is_consolidation and trend == "bullish":
        scenarios.append(_make_scenario(
            "consolidation_bullish_resolve",
            "long",
            "Consolidation bullish resolution expected",
            "Bull flag / range, expect upward resolution",
            "Close below consolidation low",
            "medium",
            price,
        ))
    elif is_consolidation and trend == "bearish":
        scenarios.append(_make_scenario(
            "consolidation_bearish_resolve",
            "short",
            "Consolidation bearish resolution expected",
            "Bear flag / range, expect downward resolution",
            "Close above consolidation high",
            "medium",
            price,
        ))

    return scenarios


def _make_scenario(
    scenario_type: str,
    direction: str,
    title: str,
    trigger: str,
    invalidation: str,
    confidence: str,
    current_price: float,
) -> dict:
    return {
        "type": scenario_type,
        "direction": direction,
        "title": title,
        "current_price": current_price,
        "entry_trigger": trigger,
        "invalidation": invalidation,
        "confidence": confidence,
    }
