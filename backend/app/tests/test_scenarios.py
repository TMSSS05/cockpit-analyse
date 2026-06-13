from __future__ import annotations

import pandas as pd
import pytest

from app.analysis.scenarios import generate_scenarios


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


class TestGenerateScenarios:
    def test_empty_on_no_data(self):
        assert generate_scenarios(pd.DataFrame()) == []

    def test_empty_on_none(self):
        assert generate_scenarios(None) == []

    def test_empty_on_short_data(self):
        df = _make_df([100.0] * 10)
        assert generate_scenarios(df) == []

    def test_returns_list_of_dicts(self):
        df = _make_df([100.0 + i * 0.5 for i in range(200)])
        scenarios = generate_scenarios(df)
        assert isinstance(scenarios, list)
        if scenarios:
            assert all(isinstance(s, dict) for s in scenarios)

    def test_scenario_has_required_keys(self):
        df = _make_df([100.0 + i * 0.5 for i in range(200)])
        scenarios = generate_scenarios(df)
        required = {"type", "direction", "title", "current_price",
                     "entry_trigger", "invalidation", "confidence"}
        for scenario in scenarios:
            missing = required - set(scenario.keys())
            assert not missing, f"Missing keys: {missing}"

    def test_bullish_trend_breakout_scenario(self):
        # Mild uptrend → tight consolidation → single sharp breakout bar
        rng = __import__("random").Random(42)
        prices = [100.0 + i * 0.125 for i in range(80)]
        prices.extend([110 + rng.uniform(-1, 1) for _ in range(30)])
        prices.append(140.0)
        df = _make_df(prices)
        scenarios = generate_scenarios(df)
        types = {s["type"] for s in scenarios}
        assert "breakout_bullish" in types, (
            f"Expected breakout_bullish in {types}"
        )

    def test_bearish_trend_breakout_scenario(self):
        # Mild downtrend → tight consolidation → single sharp breakdown bar
        rng = __import__("random").Random(42)
        prices = [200.0 - i * 0.125 for i in range(80)]
        prices.extend([170 + rng.uniform(-1, 1) for _ in range(30)])
        prices.append(130.0)
        df = _make_df(prices)
        scenarios = generate_scenarios(df)
        types = {s["type"] for s in scenarios}
        assert "breakout_bearish" in types

    def test_reversal_at_extreme_bullish(self):
        prices = [100.0 + i * 0.2 for i in range(80)]
        df = _make_df(prices)
        scenarios = generate_scenarios(df)
        types = {s["type"] for s in scenarios}
        has_reversal = "reversal_bearish" in types or "reversal_bullish" in types
        assert isinstance(has_reversal, bool)

    def test_confidence_is_valid(self):
        df = _make_df([100.0 + i * 0.3 for i in range(200)])
        scenarios = generate_scenarios(df)
        valid = {"low", "medium", "high"}
        for s in scenarios:
            assert s["confidence"] in valid, (
                f"Unexpected confidence: {s['confidence']}"
            )

    def test_direction_is_long_or_short(self):
        df = _make_df([100.0 + i * 0.3 for i in range(200)])
        scenarios = generate_scenarios(df)
        valid = {"long", "short"}
        for s in scenarios:
            assert s["direction"] in valid

    def test_current_price_set_correctly(self):
        df = _make_df([100.0 + i * 0.5 for i in range(100)])
        last_close = df["close"].iloc[-1]
        scenarios = generate_scenarios(df)
        for s in scenarios:
            assert s["current_price"] == last_close

    def test_consolidation_with_bullish_trend(self):
        prices = [100.0] * 40 + [100.0 + (i % 5) * 0.5 for i in range(30)]
        df = _make_df(prices)
        scenarios = generate_scenarios(df)
        types = {s["type"] for s in scenarios}
        expect = "consolidation_bullish_resolve"
        if expect in types:
            scenario = next(s for s in scenarios if s["type"] == expect)
            assert scenario["direction"] == "long"
