from __future__ import annotations

import pandas as pd
import pytest

from app.analysis.levels import (
    compute_all_levels,
    detect_session_high_low,
    find_swing_points,
    get_closest_level,
    get_previous_day_levels,
    get_weekly_levels,
)


def _make_daily_df(n_days: int = 10) -> pd.DataFrame:
    base = pd.Timestamp("2025-01-01")
    return pd.DataFrame({
        "timestamp": [base + pd.Timedelta(days=i) for i in range(n_days)],
        "open": [100.0 + i * 0.5 for i in range(n_days)],
        "high": [102.0 + i * 0.5 for i in range(n_days)],
        "low": [98.0 + i * 0.5 for i in range(n_days)],
        "close": [101.0 + i * 0.5 for i in range(n_days)],
        "volume": [1000.0] * n_days,
    })


def _make_intraday_df(n_hours: int = 48) -> pd.DataFrame:
    base = pd.Timestamp("2025-01-01 00:00")
    return pd.DataFrame({
        "timestamp": [base + pd.Timedelta(hours=i) for i in range(n_hours)],
        "open": [100.0 + i * 0.1 for i in range(n_hours)],
        "high": [101.0 + i * 0.1 for i in range(n_hours)],
        "low": [99.0 + i * 0.1 for i in range(n_hours)],
        "close": [100.5 + i * 0.1 for i in range(n_hours)],
        "volume": [1000.0] * n_hours,
    })


class TestSessionHighLow:
    def test_detects_high_low_in_range(self):
        df = _make_intraday_df(48)
        result = detect_session_high_low(df, "00:00", "08:00", "asia")
        assert result is not None
        assert "asia_high" in result
        assert "asia_low" in result
        assert result["asia_high"] > result["asia_low"]

    def test_returns_none_if_no_candles(self):
        result = detect_session_high_low(pd.DataFrame(), "00:00", "08:00", "test")
        assert result is None


class TestPreviousDayLevels:
    def test_returns_high_low(self):
        df = _make_daily_df(5)
        levels = get_previous_day_levels(df)
        assert "previous_day_high" in levels
        assert "previous_day_low" in levels
        assert levels["previous_day_high"] > levels["previous_day_low"]

    def test_empty_on_no_data(self):
        assert get_previous_day_levels(pd.DataFrame()) == {}


class TestWeeklyLevels:
    def test_returns_weekly_stats(self):
        df = _make_daily_df(20)
        levels = get_weekly_levels(df)
        assert "previous_week_high" in levels or "weekly_open" in levels

    def test_empty_on_no_data(self):
        assert get_weekly_levels(pd.DataFrame()) == {}


class TestSwingPoints:
    def test_finds_swings(self):
        base = pd.Timestamp("2025-01-01")
        df = pd.DataFrame({
            "timestamp": [base + pd.Timedelta(days=i) for i in range(20)],
            "open": [100, 101, 102, 103, 104, 103, 102, 101, 100, 99, 100, 101, 102, 103, 104, 103, 102, 101, 100, 99],
            "high": [101, 102, 103, 104, 105, 104, 103, 102, 101, 100, 101, 102, 103, 104, 105, 104, 103, 102, 101, 100],
            "low": [99, 100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100, 101, 102, 103, 102, 101, 100, 99, 98],
            "close": [101, 102, 103, 104, 105, 104, 103, 102, 101, 100, 101, 102, 103, 104, 105, 104, 103, 102, 101, 100],
            "volume": [1000.0] * 20,
        })
        swings = find_swing_points(df, window=3)
        assert "swing_high" in swings or "swing_low" in swings

    def test_empty_on_short_data(self):
        df = _make_daily_df(3)
        assert find_swing_points(df) == {}


class TestClosestLevel:
    def test_above_level(self):
        levels = [{"type": "resistance", "price": 110.0, "importance": "high"}]
        closest = get_closest_level(105.0, levels)
        assert closest is not None
        assert closest["price"] == 110.0

    def test_below_level(self):
        levels = [{"type": "support", "price": 100.0, "importance": "high"}]
        closest = get_closest_level(105.0, levels)
        assert closest is not None
        assert closest["price"] == 100.0

    def test_finds_closest(self):
        levels = [
            {"type": "far", "price": 200.0, "importance": "low"},
            {"type": "close", "price": 106.0, "importance": "high"},
        ]
        closest = get_closest_level(105.0, levels)
        assert closest is not None
        assert closest["price"] == 106.0

    def test_returns_none_if_no_levels(self):
        assert get_closest_level(100.0, []) is None


class TestComputeAllLevels:
    def test_returns_list(self):
        df = _make_daily_df(20)
        levels = compute_all_levels(df)
        assert isinstance(levels, list)
        assert len(levels) > 0
