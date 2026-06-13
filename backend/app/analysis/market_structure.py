from __future__ import annotations

from typing import Literal

import pandas as pd

from app.analysis.indicators import add_all_indicators
from app.config import settings

TrendLabel = Literal["bullish", "bearish", "neutral", "mixed"]
VolatilityLabel = Literal["low", "normal", "high", "extreme"]
MomentumLabel = Literal[
    "strong_bullish", "weak_bullish", "neutral", "weak_bearish", "strong_bearish"
]


def analyze_trend(df: pd.DataFrame) -> TrendLabel:
    """Determine trend direction for a single timeframe.

    Uses EMA positioning, slope, and price relative to EMA 200.
    """
    df = add_all_indicators(df)
    if df.empty or len(df) < 50:
        return "neutral"

    last = df.iloc[-1]
    price = last["close"]
    ema_20 = last.get("ema_20", price)
    ema_50 = last.get("ema_50", price)
    ema_200 = last.get("ema_200", price)
    adx = last.get("adx", 0)

    # Price vs EMA 200 (major trend filter)
    above_200 = price > ema_200
    below_200 = price < ema_200

    # EMA alignment
    ema_bullish = ema_20 > ema_50
    ema_bearish = ema_20 < ema_50

    # Price vs EMAs
    price_above_20 = price > ema_20
    price_above_50 = price > ema_50

    if adx is None or pd.isna(adx):
        adx = 0

    is_trending = adx > settings.STRONG_TREND_ADX

    if is_trending and above_200 and ema_bullish and price_above_20 and price_above_50:
        return "bullish"
    if is_trending and below_200 and ema_bearish and not price_above_20 and not price_above_50:
        return "bearish"

    # Mixed signals
    if above_200 and not ema_bullish:
        return "mixed"
    if below_200 and not ema_bearish:
        return "mixed"

    if above_200 and price_above_50:
        return "bullish"
    if below_200 and not price_above_50:
        return "bearish"

    return "neutral"


def analyze_multi_timeframe_trend(
    df_5m: pd.DataFrame,
    df_15m: pd.DataFrame,
    df_1h: pd.DataFrame,
    df_4h: pd.DataFrame,
    df_1d: pd.DataFrame,
) -> dict[str, TrendLabel]:
    """Analyze trend across all timeframes."""
    trend_5m = analyze_trend(df_5m) if df_5m is not None and not df_5m.empty else "neutral"
    trend_15m = analyze_trend(df_15m) if df_15m is not None and not df_15m.empty else "neutral"
    trend_1h = analyze_trend(df_1h) if df_1h is not None and not df_1h.empty else "neutral"
    trend_4h = analyze_trend(df_4h) if df_4h is not None and not df_4h.empty else "neutral"
    trend_1d = analyze_trend(df_1d) if df_1d is not None and not df_1d.empty else "neutral"

    return {
        "5m": trend_5m,
        "15m": trend_15m,
        "1h": trend_1h,
        "4h": trend_4h,
        "1d": trend_1d,
    }


def analyze_volatility(df: pd.DataFrame) -> VolatilityLabel:
    """Analyze volatility regime using ATR, Bollinger Band width, and price range."""
    df = add_all_indicators(df)
    if df.empty or len(df) < 20:
        return "normal"

    # Tight price range is direct evidence of low volatility
    recent_range = df["high"].tail(10).max() - df["low"].tail(10).min()
    total_range = df["high"].tail(50).max() - df["low"].tail(50).min()
    range_ratio = recent_range / total_range if total_range > 0 else 1.0
    if range_ratio < 0.3:
        return "low"

    atr = df["atr"].iloc[-1]
    atr_mean = df["atr"].rolling(20).mean().iloc[-1]
    if atr_mean is None or pd.isna(atr_mean) or atr_mean == 0:
        return "normal"
    atr_ratio = atr / atr_mean

    bb_width = df["bb_width"].iloc[-1]
    bb_mean = df["bb_width"].rolling(20).mean().iloc[-1]
    if bb_mean is None or pd.isna(bb_mean) or bb_mean == 0:
        return "normal"
    bb_ratio = bb_width / bb_mean

    vol_score = (atr_ratio + bb_ratio) / 2

    if vol_score > 1.8:
        return "extreme"
    if vol_score > 1.3:
        return "high"
    if vol_score < 0.7:
        return "low"
    return "normal"

    atr = df["atr"].iloc[-1]
    atr_mean = df["atr"].rolling(20).mean().iloc[-1]

    if atr_mean is None or pd.isna(atr_mean) or atr_mean == 0:
        return "normal"

    atr_ratio = atr / atr_mean

    bb_width = df["bb_width"].iloc[-1] if "bb_width" in df.columns else 0
    bb_mean = df["bb_width"].rolling(20).mean().iloc[-1] if "bb_width" in df.columns else 0

    if bb_mean and not pd.isna(bb_mean) and bb_mean > 0:
        bb_ratio = bb_width / bb_mean
    else:
        bb_ratio = 1.0

    vol_score = (atr_ratio + bb_ratio) / 2

    if vol_score > 1.8:
        return "extreme"
    if vol_score > 1.3:
        return "high"
    if vol_score < 0.7:
        return "low"
    return "normal"


def analyze_momentum(df: pd.DataFrame) -> MomentumLabel:
    """Analyze momentum using RSI, MACD, and EMA slope."""
    df = add_all_indicators(df)
    if df.empty or len(df) < 30:
        return "neutral"

    last = df.iloc[-1]
    rsi = last.get("rsi", 50)
    macd_hist = last.get("macd_hist", 0)

    # EMA 20 slope (using last 3 candles)
    if "ema_20" in df.columns and len(df) >= 3:
        ema_slope = df["ema_20"].iloc[-1] - df["ema_20"].iloc[-3]
    else:
        ema_slope = 0

    # Recent close momentum
    recent_closes = df["close"].tail(5)
    close_momentum = (recent_closes.iloc[-1] > recent_closes.iloc[0]) if len(recent_closes) >= 5 else None

    if rsi is None or pd.isna(rsi):
        rsi = 50
    if macd_hist is None or pd.isna(macd_hist):
        macd_hist = 0

    # Scoring
    score = 0
    if rsi > 60:
        score += 1
    if rsi > 70:
        score += 1
    if rsi < 40:
        score -= 1
    if rsi < 30:
        score -= 1

    if macd_hist > 0:
        score += 1
    else:
        score -= 1

    if ema_slope > 0:
        score += 1
    else:
        score -= 1

    if close_momentum is True:
        score += 1
    elif close_momentum is False:
        score -= 1

    if score >= 3:
        return "strong_bullish"
    if score >= 1:
        return "weak_bullish"
    if score <= -3:
        return "strong_bearish"
    if score <= -1:
        return "weak_bearish"
    return "neutral"


def detect_consolidation(df: pd.DataFrame) -> bool:
    """Detect if market is consolidating (low ADX, low ATR, tight range)."""
    df = add_all_indicators(df)
    if df.empty or len(df) < 20:
        return False

    adx = df["adx"].iloc[-1]
    atr = df["atr"].iloc[-1]
    atr_mean = df["atr"].rolling(20).mean().iloc[-1]

    # Recent range
    recent_range = df["high"].tail(10).max() - df["low"].tail(10).min()
    total_range = df["high"].tail(50).max() - df["low"].tail(50).min()

    if atr_mean is None or pd.isna(atr_mean) or atr_mean == 0 or total_range == 0:
        return False

    atr_ratio = atr / atr_mean
    range_ratio = recent_range / total_range

    if pd.isna(adx) or atr_ratio is None:
        return False

    # Primary: classic consolidation — all conditions met
    if adx < settings.STRONG_TREND_ADX and atr_ratio < 0.9 and range_ratio < 0.3:
        return True

    # Fallback: ultra-tight range (< 15%) — price is pinned, ADX/ATR lag is tolerable
    if range_ratio < 0.15:
        return True

    # Fallback: low ADX + moderate contraction — ATR may not have fully converged,
    # and range ratio can be slightly higher (up to 35%) while still in choppy consolidation
    if adx < settings.STRONG_TREND_ADX and range_ratio < 0.35 and atr_ratio < 1.0:
        return True

    # Fallback: absolute tightness (< 0.5% of price) — catches pinned price
    # where range_ratio ≈ 1.0 because the full window is equally tight
    last_close = df["close"].iloc[-1]
    if last_close > 0 and recent_range / last_close < 0.005:
        return True

    return False


def detect_breakout(df: pd.DataFrame) -> bool:
    """Detect potential breakout.

    Close above recent range high or below low,
    with expanding ATR and aligned momentum.
    """
    df = add_all_indicators(df)
    if df.empty or len(df) < 20:
        return False

    recent_high = df["high"].iloc[-11:-1].max()
    recent_low = df["low"].iloc[-11:-1].min()
    last_close = df["close"].iloc[-1]

    atr = df["atr"].iloc[-1]
    atr_prev = df["atr"].iloc[-2] if len(df) >= 2 else atr
    atr_expanding = atr > atr_prev

    momentum = analyze_momentum(df)
    momentum_aligned = "bullish" in momentum or "bearish" in momentum

    broke_high = last_close > recent_high
    broke_low = last_close < recent_low

    # ADX guard: avoid flagging strong trends as breakouts
    # unless price was tightly consolidating beforehand
    last = df.iloc[-1]
    adx_val = last.get("adx", 0)
    if not pd.isna(adx_val) and adx_val >= settings.STRONG_TREND_ADX:
        pre_range = recent_high - recent_low
        if pre_range / last_close >= 0.05:
            return False

    # Low-ADX guard: avoid flagging noise as breakouts in non-trending markets
    # Requires strong momentum to confirm — weak momentum + low ADX = noise, not breakout
    if not pd.isna(adx_val) and adx_val < settings.STRONG_TREND_ADX:
        momentum = analyze_momentum(df)
        if "strong" not in str(momentum):
            return False

    return bool((broke_high or broke_low) and atr_expanding and momentum_aligned)


def detect_sweep(df: pd.DataFrame) -> bool:
    """Detect potential sweep (liquidity grab).

    Price breaks a key level but closes back inside the range
    with weakening momentum.
    """
    df = add_all_indicators(df)
    if df.empty or len(df) < 20:
        return False

    recent_high = df["high"].iloc[-11:-1].max()
    recent_low = df["low"].iloc[-11:-1].min()
    last = df.iloc[-1]

    # Long wick detection
    wick_upper = last["high"] - max(last["open"], last["close"])
    wick_lower = min(last["open"], last["close"]) - last["low"]
    range_size = last["high"] - last["low"]

    if range_size == 0:
        return False

    long_wick_above = wick_upper > range_size * 0.5
    long_wick_below = wick_lower > range_size * 0.5

    # Price broke level but closed back
    broke_high = last["high"] > recent_high
    broke_low = last["low"] < recent_low
    closed_back = (last["close"] < recent_high) and (last["close"] > recent_low)

    condition_above = broke_high and long_wick_above and closed_back
    condition_below = broke_low and long_wick_below and closed_back

    return bool(condition_above or condition_below)
