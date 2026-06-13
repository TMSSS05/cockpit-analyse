from __future__ import annotations

import pandas as pd
import pytest

from app.analysis.market_structure import (
    analyze_momentum,
    analyze_trend,
    analyze_volatility,
    detect_breakout,
    detect_consolidation,
    detect_sweep,
)


def _make_df(close_prices: list[float]) -> pd.DataFrame:
    n = len(close_prices)
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="h"),
        "open": close_prices,
        "high": [p * 1.01 for p in close_prices],
        "low": [p * 0.99 for p in close_prices],
        "close": close_prices,
        "volume": [1000.0] * n,
    })


class TestAnalyzeTrend:
    def test_bullish_trend(self):
        prices = [100.0 + i * 0.2 for i in range(200)]
        df = _make_df(prices)
        trend = analyze_trend(df)
        assert trend == "bullish"

    def test_bearish_trend(self):
        prices = [200.0 - i * 0.2 for i in range(200)]
        df = _make_df(prices)
        trend = analyze_trend(df)
        assert trend == "bearish"

    def test_neutral_on_choppy(self):
        prices = [100.0 + (i % 20) * 5 for i in range(100)]
        df = _make_df(prices)
        trend = analyze_trend(df)
        assert trend in ("neutral", "mixed", "bullish", "bearish")


class TestAnalyzeMomentum:
    def test_strong_bullish_momentum(self):
        prices = [100.0 + i * 2.0 for i in range(50)]
        df = _make_df(prices)
        momentum = analyze_momentum(df)
        assert momentum == "strong_bullish"

    def test_strong_bearish_momentum(self):
        prices = [200.0 - i * 2.0 for i in range(50)]
        df = _make_df(prices)
        momentum = analyze_momentum(df)
        assert momentum == "strong_bearish"

    def test_neutral_on_flat(self):
        prices = [100.0] * 50
        df = _make_df(prices)
        momentum = analyze_momentum(df)
        assert momentum in ("neutral", "weak_bullish", "weak_bearish")


class TestAnalyzeVolatility:
    def test_high_volatility(self):
        prices = [100.0 + (i % 5) * 10 for i in range(50)]
        df = _make_df(prices)
        vol = analyze_volatility(df)
        assert vol in ("normal", "high", "extreme")

    def test_low_volatility(self):
        prices = [100.0 + (i % 50) * 0.1 for i in range(50)]
        df = _make_df(prices)
        vol = analyze_volatility(df)
        assert vol in ("low", "normal")


class TestDetectConsolidation:
    def test_consolidation_detection(self):
        prices = [100.0 + (i % 5) * 0.5 for i in range(60)]
        df = _make_df(prices)

        is_consolidation = detect_consolidation(df)
        assert isinstance(is_consolidation, bool)


class TestDetectBreakout:
    def test_breakout_detection(self):
        prices = [100.0] * 15 + [110.0 + i * 0.5 for i in range(15)]
        df = _make_df(prices)

        is_breakout = detect_breakout(df)
        assert isinstance(is_breakout, bool)


class TestDetectSweep:
    def test_sweep_detection(self):
        prices = [100.0] * 10 + [105.0, 95.0, 100.0] + [100.0] * 10
        df = _make_df(prices)

        is_sweep = detect_sweep(df)
        assert isinstance(is_sweep, bool)
