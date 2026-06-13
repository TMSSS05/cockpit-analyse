from __future__ import annotations

import pandas as pd
import pytest

from app.analysis.indicators import add_all_indicators


def _make_candle_df(close_prices: list[float]) -> pd.DataFrame:
    n = len(close_prices)
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=n, freq="h"),
        "open": close_prices,
        "high": [p * 1.01 for p in close_prices],
        "low": [p * 0.99 for p in close_prices],
        "close": close_prices,
        "volume": [1000.0] * n,
    })


class TestIndicators:
    def test_all_indicators_present(self):
        prices = [100.0 + (i % 10) * 2 for i in range(100)]
        df = _make_candle_df(prices)
        df = add_all_indicators(df)

        expected_cols = [
            "ema_20", "ema_50", "ema_200",
            "rsi", "atr", "adx",
            "bb_upper", "bb_lower", "bb_width",
            "macd", "macd_signal", "macd_hist",
        ]
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_minimum_data(self):
        df = _make_candle_df([100.0] * 5)
        df = add_all_indicators(df)
        assert df is not None
        assert len(df) == 5

    def test_ema_increasing_prices(self):
        prices = [100.0 + i * 0.5 for i in range(60)]
        df = _make_candle_df(prices)
        df = add_all_indicators(df)
        assert not pd.isna(df["ema_20"].iloc[-1])
        assert df["ema_20"].iloc[-1] > 100.0

    def test_rsi_uptrend(self):
        prices = [100.0 + i * 1.0 for i in range(60)]
        df = _make_candle_df(prices)
        df = add_all_indicators(df)
        assert df["rsi"].iloc[-1] > 60

    def test_rsi_downtrend(self):
        prices = [130.0 - i * 1.0 for i in range(60)]
        df = _make_candle_df(prices)
        df = add_all_indicators(df)
        assert df["rsi"].iloc[-1] < 40

    def test_rsi_midrange_on_stable(self):
        prices = [100.0] * 30
        df = _make_candle_df(prices)
        df = add_all_indicators(df)
        rsi = df["rsi"].dropna().iloc[-1]
        assert 30 < rsi < 70

    def test_atr_positive(self):
        prices = [100.0 + i * 0.5 for i in range(60)]
        df = _make_candle_df(prices)
        df = add_all_indicators(df)
        assert not pd.isna(df["atr"].iloc[-1])
        assert df["atr"].iloc[-1] > 0
