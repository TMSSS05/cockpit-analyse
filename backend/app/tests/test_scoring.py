from __future__ import annotations

import pandas as pd
import pytest

from app.analysis.scoring import (
    compute_analysis_score,
    score_to_label,
    score_to_action_bias,
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


class TestComputeAnalysisScore:
    def test_zero_on_no_data(self):
        assert compute_analysis_score(pd.DataFrame()) == 0

    def test_zero_on_none(self):
        assert compute_analysis_score(None) == 0

    def test_zero_on_short_data(self):
        df = _make_df([100.0] * 10)
        assert compute_analysis_score(df) == 0

    def test_returns_int(self):
        df = _make_df([100.0 + i * 0.5 for i in range(100)])
        score = compute_analysis_score(df)
        assert isinstance(score, int)

    def test_score_in_range(self):
        df = _make_df([100.0 + i * 0.5 for i in range(100)])
        score = compute_analysis_score(df)
        assert -10 <= score <= 10, f"Score {score} out of [-10, 10]"

    def test_bullish_trend_positive_score(self):
        prices = [100.0 + i * 0.5 for i in range(200)]
        df = _make_df(prices)
        score = compute_analysis_score(df)
        assert score > 0, f"Expected positive score for uptrend, got {score}"

    def test_bearish_trend_negative_score(self):
        prices = [200.0 - i * 0.5 for i in range(200)]
        df = _make_df(prices)
        score = compute_analysis_score(df)
        assert score < 0, f"Expected negative score for downtrend, got {score}"

    def test_neutral_market_near_zero(self):
        prices = [100.0 + ((i + 10) % 20) * 2 for i in range(100)]
        df = _make_df(prices)
        score = compute_analysis_score(df)
        assert -3 <= score <= 3, (
            f"Expected neutral score near zero, got {score}"
        )

    def test_clamped_to_max_10(self):
        prices = [100.0 + i * 2.0 for i in range(200)]
        df = _make_df(prices)
        score = compute_analysis_score(df)
        assert score <= 10

    def test_clamped_to_min_minus_10(self):
        prices = [200.0 - i * 2.0 for i in range(200)]
        df = _make_df(prices)
        score = compute_analysis_score(df)
        assert score >= -10

    def test_score_is_deterministic(self):
        prices = [100.0 + i * 0.3 for i in range(100)]
        df = _make_df(prices)
        score1 = compute_analysis_score(df)
        score2 = compute_analysis_score(df)
        assert score1 == score2


class TestScoreToLabel:
    @pytest.mark.parametrize("score,expected", [
        (10, "strong_bullish"),
        (7, "strong_bullish"),
        (6, "bullish"),
        (4, "bullish"),
        (3, "slightly_bullish"),
        (1, "slightly_bullish"),
        (0, "neutral"),
        (-1, "neutral"),
        (-2, "slightly_bearish"),
        (-4, "slightly_bearish"),
        (-5, "bearish"),
        (-7, "bearish"),
        (-8, "strong_bearish"),
        (-10, "strong_bearish"),
    ])
    def test_labels(self, score: int, expected: str):
        assert score_to_label(score) == expected


class TestScoreToActionBias:
    @pytest.mark.parametrize("score,expected_substring", [
        (10, "long opportunities"),
        (7, "long opportunities"),
        (4, "long opportunities"),
        (3, "Lean bullish"),
        (1, "Lean bullish"),
        (0, "No clear bias"),
        (-1, "No clear bias"),
        (-2, "Lean bearish"),
        (-4, "Lean bearish"),
        (-5, "short opportunities"),
        (-10, "short opportunities"),
    ])
    def test_action_biases(self, score: int, expected_substring: str):
        bias = score_to_action_bias(score)
        assert expected_substring in bias, (
            f"Expected '{expected_substring}' in '{bias}' for score={score}"
        )
