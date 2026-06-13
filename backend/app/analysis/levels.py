from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def detect_session_high_low(
    df: pd.DataFrame,
    session_start: str,
    session_end: str,
    label: str,
) -> dict | None:
    """Find the high and low within a session time window.

    session_start/session_end: HH:MM format in UTC.
    """
    if df is None or df.empty:
        return None

    df = df.copy()
    df["time"] = df["timestamp"].dt.strftime("%H:%M")

    session_mask = (df["time"] >= session_start) & (df["time"] <= session_end)
    session_candles = df[session_mask]
    if session_candles.empty:
        return None

    high = float(session_candles["high"].max())
    low = float(session_candles["low"].min())
    return {
        f"{label}_high": high,
        f"{label}_low": low,
        f"{label}_high_index": session_candles["high"].idxmax(),
        f"{label}_low_index": session_candles["low"].idxmin(),
    }


def get_previous_day_levels(df: pd.DataFrame) -> dict:
    """Extract previous day high, low, and daily open."""
    if df is None or df.empty:
        return {}

    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    unique_dates = sorted(df["date"].unique())
    if len(unique_dates) < 2:
        # If only one day, use the current day
        today = unique_dates[-1]
        prev_day_data = df[df["date"] == today]
    else:
        prev_date = unique_dates[-2]
        prev_day_data = df[df["date"] == prev_date]

    if prev_day_data.empty:
        return {}

    return {
        "previous_day_high": float(prev_day_data["high"].max()),
        "previous_day_low": float(prev_day_data["low"].min()),
        "daily_open": float(prev_day_data["open"].iloc[0]),
    }


def get_weekly_levels(df: pd.DataFrame) -> dict:
    """Extract weekly open and previous week high/low."""
    if df is None or df.empty:
        return {}

    df = df.copy()
    df["week"] = df["timestamp"].dt.isocalendar().week
    unique_weeks = sorted(df["week"].unique())
    if len(unique_weeks) < 2:
        current_week = unique_weeks[-1]
        week_data = df[df["week"] == current_week]
    else:
        prev_week = unique_weeks[-2]
        week_data = df[df["week"] == prev_week]

    if week_data.empty:
        return {}

    return {
        "previous_week_high": float(week_data["high"].max()),
        "previous_week_low": float(week_data["low"].min()),
        "weekly_open": float(week_data["open"].iloc[0]),
    }


def find_swing_points(df: pd.DataFrame, window: int = 5) -> dict:
    """Find swing highs and lows using local maxima/minima.

    window: number of candles on each side to confirm the swing.
    """
    if df is None or len(df) < window * 2 + 1:
        return {}

    highs = df["high"].values
    lows = df["low"].values

    swing_highs = []
    swing_lows = []

    for i in range(window, len(df) - window):
        if highs[i] == max(highs[i - window : i + window + 1]):
            swing_highs.append({
                "price": float(highs[i]),
                "index": i,
                "timestamp": str(df.iloc[i]["timestamp"]),
            })
        if lows[i] == min(lows[i - window : i + window + 1]):
            swing_lows.append({
                "price": float(lows[i]),
                "index": i,
                "timestamp": str(df.iloc[i]["timestamp"]),
            })

    # Return the most recent swing high and low
    result = {}
    if swing_highs:
        latest_sh = swing_highs[-1]
        result["swing_high"] = latest_sh["price"]
        result["swing_high_index"] = latest_sh["index"]

    if swing_lows:
        latest_sl = swing_lows[-1]
        result["swing_low"] = latest_sl["price"]
        result["swing_low_index"] = latest_sl["index"]

    # Also return the highest swing and lowest swing for range
    if swing_highs:
        highest = max(sh["price"] for sh in swing_highs)
        result["swing_high_high"] = highest

    if swing_lows:
        lowest = min(sl["price"] for sl in swing_lows)
        result["swing_low_low"] = lowest

    return result


def compute_all_levels(df: pd.DataFrame) -> list[dict]:
    """Compute all key levels for a symbol, returning a list of dicts."""
    levels = []
    df_daily = df  # Use daily data if available

    # Previous day levels
    prev_day = get_previous_day_levels(df_daily)
    for key in ["previous_day_high", "previous_day_low", "daily_open"]:
        if key in prev_day:
            levels.append({
                "type": key,
                "price": prev_day[key],
                "importance": "high",
            })

    # Weekly levels
    weekly = get_weekly_levels(df_daily)
    for key in ["previous_week_high", "previous_week_low", "weekly_open"]:
        if key in weekly:
            levels.append({
                "type": key,
                "price": weekly[key],
                "importance": "high",
            })

    # Session levels (Asia)
    asia = detect_session_high_low(df, "00:00", "08:00", "asia")
    if asia:
        for label, key in [("asia_high", "asia_high"), ("asia_low", "asia_low")]:
            if key in asia:
                levels.append({
                    "type": label,
                    "price": asia[key],
                    "importance": "low",
                })

    # Session levels (London)
    london = detect_session_high_low(df, "08:00", "16:00", "london")
    if london:
        for label, key in [("london_high", "london_high"), ("london_low", "london_low")]:
            if key in london:
                levels.append({
                    "type": label,
                    "price": london[key],
                    "importance": "medium",
                })

    # Swing points
    swings = find_swing_points(df, window=3)
    if "swing_high" in swings:
        levels.append({
            "type": "swing_high",
            "price": swings["swing_high"],
            "importance": "high",
        })
    if "swing_low" in swings:
        levels.append({
            "type": "swing_low",
            "price": swings["swing_low"],
            "importance": "high",
        })

    return levels


def get_closest_level(current_price: float, levels: list[dict]) -> dict | None:
    """Find the closest level (above or below) to current price."""
    if not levels or current_price is None:
        return None

    above = [l for l in levels if l["price"] > current_price]
    below = [l for l in levels if l["price"] < current_price]

    closest_above = min(above, key=lambda l: l["price"] - current_price) if above else None
    closest_below = max(below, key=lambda l: current_price - l["price"]) if below else None

    if closest_above and closest_below:
        dist_above = closest_above["price"] - current_price
        dist_below = current_price - closest_below["price"]
        return closest_above if dist_above < dist_below else closest_below
    return closest_above or closest_below
