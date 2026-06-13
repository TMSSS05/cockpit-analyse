"""Mock market data for fallback when live sources are unavailable."""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import UTC, datetime, timedelta


def generate_mock_candles(
    symbol: str,
    timeframe: str = "1h",
    count: int = 200,
    base_price: float | None = None,
) -> pd.DataFrame:
    """Generate realistic-looking mock OHLCV data.

    Parameters
    ----------
    symbol : str
        Asset symbol (e.g., XAUUSD, BTC).
    timeframe : str
        Candle resolution.
    count : int
        Number of candles to generate.
    base_price : float | None
        Starting price.  Auto-selected by symbol if None.

    Returns
    -------
    pd.DataFrame
        Columns: timestamp, open, high, low, close, volume
    """
    base_prices = {
        "XAUUSD": 2650.0,
        "BTC": 67000.0,
        "NASDAQ": 18500.0,
        "OIL": 72.0,
        "EURUSD": 1.0800,
    }
    price = base_price or base_prices.get(symbol, 100.0)

    duration_map: dict[str, timedelta] = {
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
    }
    step = duration_map.get(timeframe, timedelta(hours=1))

    now = datetime.now(UTC)
    timestamps = [now - step * (count - 1 - i) for i in range(count)]

    np.random.seed(42 + hash(symbol) % 1000)

    # Generate a realistic walk with mean-reversion and momentum
    closes = [price]
    for i in range(1, count):
        ret = np.random.normal(0, 0.002)  # 0.2% typical return
        # Add some momentum
        if i > 5:
            recent_trend = np.mean(closes[-5:]) - closes[-5]
            ret += recent_trend / price * 0.3
        new_close = closes[-1] * (1 + ret)
        closes.append(new_close)

    closes_arr = np.array(closes)
    tick_size = price * 0.005  # ~0.5% for spreads

    opens = closes_arr * (1 + np.random.normal(0, 0.001, count))
    highs = np.maximum(opens, closes_arr) + np.abs(np.random.normal(0, tick_size * 2, count))
    lows = np.minimum(opens, closes_arr) - np.abs(np.random.normal(0, tick_size * 2, count))
    volumes = np.random.lognormal(10, 1, count).astype(np.int64)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes_arr,
        "volume": volumes,
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def generate_mock_analysis(symbol: str) -> dict:
    """Return a plausible mock analysis for a symbol."""
    analyses = {
        "XAUUSD": {
            "trend": {"M15": "bullish", "H1": "bullish", "H4": "bullish", "D1": "neutral"},
            "volatility": "normal",
            "momentum": "weak_bullish",
            "consolidation": False,
            "breakout": False,
            "sweep": False,
            "key_levels": [
                {"type": "previous_day_high", "price": 2675.30, "importance": "high"},
                {"type": "previous_day_low", "price": 2632.10, "importance": "high"},
                {"type": "daily_open", "price": 2650.00, "importance": "medium"},
                {"type": "weekly_open", "price": 2640.50, "importance": "medium"},
                {"type": "asia_high", "price": 2660.40, "importance": "low"},
                {"type": "asia_low", "price": 2645.80, "importance": "low"},
                {"type": "swing_high", "price": 2680.00, "importance": "high"},
                {"type": "swing_low", "price": 2620.00, "importance": "high"},
            ],
            "scenarios": {
                "primary": "Tendance H4 haussière, H1 en consolidation. Prix proche du high de la veille. Volatilité normale. Attendre un retest du daily open pour valider.",
                "alternative": "Si le prix casse le high de la veille avec momentum, extension vers le swing high à 2680.",
                "no_trade": "Si le prix sweep le high asiatique et retourne en range, éviter. Faux breakout possible.",
            },
            "indicators": {
                "ema_20": 2655.00,
                "ema_50": 2645.00,
                "ema_200": 2620.00,
                "rsi": 58.5,
                "atr": 12.4,
                "adx": 22.0,
            },
        },
        "BTC": {
            "trend": {"M15": "bullish", "H1": "bullish", "H4": "neutral", "D1": "bullish"},
            "volatility": "high",
            "momentum": "strong_bullish",
            "consolidation": False,
            "breakout": True,
            "sweep": False,
            "key_levels": [
                {"type": "previous_day_high", "price": 68500.0, "importance": "high"},
                {"type": "previous_day_low", "price": 65800.0, "importance": "high"},
                {"type": "daily_open", "price": 67000.0, "importance": "medium"},
                {"type": "weekly_open", "price": 66200.0, "importance": "medium"},
                {"type": "asia_high", "price": 67500.0, "importance": "low"},
                {"type": "asia_low", "price": 66800.0, "importance": "low"},
                {"type": "swing_high", "price": 69000.0, "importance": "high"},
                {"type": "swing_low", "price": 65000.0, "importance": "high"},
            ],
            "scenarios": {
                "primary": "Momentum positif mais volatilité élevée. Si le prix tient au-dessus de 67000, biais haussier intraday.",
                "alternative": "Rejet au swing high 69000 possible. Range asiatique à surveiller pour direction.",
                "no_trade": "Éviter de trader autour du weekly open. Attendre une clôture claire au-dessus de 68500 ou un retest du daily open.",
            },
            "indicators": {
                "ema_20": 67200.0,
                "ema_50": 66500.0,
                "ema_200": 64000.0,
                "rsi": 62.0,
                "atr": 1800.0,
                "adx": 28.0,
            },
        },
        "NASDAQ": {
            "trend": {"M15": "bearish", "H1": "bearish", "H4": "neutral", "D1": "bullish"},
            "volatility": "normal",
            "momentum": "weak_bearish",
            "consolidation": True,
            "breakout": False,
            "sweep": False,
            "key_levels": [
                {"type": "previous_day_high", "price": 18650.0, "importance": "high"},
                {"type": "previous_day_low", "price": 18380.0, "importance": "high"},
                {"type": "daily_open", "price": 18500.0, "importance": "medium"},
                {"type": "weekly_open", "price": 18420.0, "importance": "medium"},
                {"type": "swing_high", "price": 18750.0, "importance": "high"},
                {"type": "swing_low", "price": 18250.0, "importance": "high"},
            ],
            "scenarios": {
                "primary": "Contexte à surveiller avec VIX et taux US. Marché en consolidation entre 18380 et 18650.",
                "alternative": "Si le prix tient au-dessus du daily open, biais intraday plus constructif vers 18650.",
                "no_trade": "Range serré, ADX faible. Attendre un breakout clair ou une expansion de volatilité.",
            },
            "indicators": {
                "ema_20": 18520.0,
                "ema_50": 18480.0,
                "ema_200": 18200.0,
                "rsi": 48.0,
                "atr": 120.0,
                "adx": 18.0,
            },
        },
        "OIL": {
            "trend": {"M15": "bearish", "H1": "bearish", "H4": "bearish", "D1": "neutral"},
            "volatility": "high",
            "momentum": "strong_bearish",
            "consolidation": False,
            "breakout": False,
            "sweep": True,
            "key_levels": [
                {"type": "previous_day_high", "price": 74.50, "importance": "high"},
                {"type": "previous_day_low", "price": 70.80, "importance": "high"},
                {"type": "daily_open", "price": 72.00, "importance": "medium"},
                {"type": "weekly_open", "price": 73.20, "importance": "medium"},
                {"type": "swing_high", "price": 76.00, "importance": "high"},
                {"type": "swing_low", "price": 69.50, "importance": "high"},
            ],
            "scenarios": {
                "primary": "Volatilité forte autour des news stocks pétrole. Tendance baissière H4, possible sweep du low précédent.",
                "alternative": "Rebond technique possible si le prix tient 70.80. Surveiller les stocks API/EIA.",
                "no_trade": "Éviter avant les news. Si sweep du low confirmé, attendre une clôture H1 pour direction.",
            },
            "indicators": {
                "ema_20": 72.80,
                "ema_50": 73.50,
                "ema_200": 75.00,
                "rsi": 38.0,
                "atr": 2.1,
                "adx": 30.0,
            },
        },
        "EURUSD": {
            "trend": {"M15": "neutral", "H1": "bullish", "H4": "neutral", "D1": "bearish"},
            "volatility": "low",
            "momentum": "neutral",
            "consolidation": True,
            "breakout": False,
            "sweep": False,
            "key_levels": [
                {"type": "previous_day_high", "price": 1.0850, "importance": "high"},
                {"type": "previous_day_low", "price": 1.0760, "importance": "high"},
                {"type": "daily_open", "price": 1.0800, "importance": "medium"},
                {"type": "weekly_open", "price": 1.0780, "importance": "medium"},
                {"type": "swing_high", "price": 1.0900, "importance": "high"},
                {"type": "swing_low", "price": 1.0720, "importance": "high"},
            ],
            "scenarios": {
                "primary": "Volatilité faible, range serré. Marché en consolidation entre 1.0760 et 1.0850. Attendre un catalyst.",
                "alternative": "Si le prix casse 1.0850, ouverture vers 1.0900. Si le prix casse 1.0760, extension vers 1.0720.",
                "no_trade": "ADX trop faible, pas de tendance claire. Meilleur trade est de ne pas trader.",
            },
            "indicators": {
                "ema_20": 1.0810,
                "ema_50": 1.0790,
                "ema_200": 1.0820,
                "rsi": 52.0,
                "atr": 0.0045,
                "adx": 15.0,
            },
        },
    }
    return analyses.get(symbol, analyses["XAUUSD"])


def generate_mock_weekly_levels(symbol: str) -> list[dict]:
    """Generate mock weekly levels for a symbol."""
    base = generate_mock_analysis(symbol)
    all_levels = base["key_levels"]
    # Add weekly levels
    if symbol == "XAUUSD":
        all_levels.append({"type": "previous_week_high", "price": 2690.00, "importance": "high"})
        all_levels.append({"type": "previous_week_low", "price": 2610.00, "importance": "high"})
    elif symbol == "BTC":
        all_levels.append({"type": "previous_week_high", "price": 70000.00, "importance": "high"})
        all_levels.append({"type": "previous_week_low", "price": 64500.00, "importance": "high"})
    else:
        all_levels.append({"type": "previous_week_high", "price": base["key_levels"][0]["price"] * 1.02, "importance": "high"})
        all_levels.append({"type": "previous_week_low", "price": base["key_levels"][1]["price"] * 0.98, "importance": "high"})
    return all_levels
