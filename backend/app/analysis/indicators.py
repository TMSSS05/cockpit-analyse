from __future__ import annotations

import pandas as pd
import numpy as np


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators to a OHLCV DataFrame.

    Adds columns: ema_20, ema_50, ema_200, rsi, atr, adx,
                   bb_width, macd, macd_signal, macd_hist
    """
    df = df.copy()
    df = _add_ema(df, 20)
    df = _add_ema(df, 50)
    df = _add_ema(df, 200)
    df = _add_rsi(df, 14)
    df = _add_atr(df, 14)
    df = _add_adx(df, 14)
    df = _add_bollinger_bands(df, 20)
    df = _add_macd(df)
    return df


def _add_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:
    df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    return df


def _add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()
    avg_loss_safe = avg_loss.replace(0, np.nan)
    rs = avg_gain / avg_loss_safe
    df["rsi"] = 100 - (100 / (1 + rs))
    # All gains (loss=0, gain>0) → RSI=100
    # All losses (gain=0, loss>0) → RSI=0
    # No movement (both=0) → RSI=50
    df["rsi"] = df["rsi"].fillna(100.0).replace([np.inf, -np.inf], 100.0)
    both_zero = (avg_gain == 0) & (avg_loss == 0)
    df.loc[both_zero, "rsi"] = 50.0
    return df


def _add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    high, low, close = df["high"], df["low"], df["close"]
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr"] = tr.ewm(span=period, adjust=False).mean()
    return df


def _add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    high, low, close = df["high"], df["low"], df["close"]

    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = minus_dm.abs()

    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)

    atr = tr.ewm(span=period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr.replace(0, np.nan))

    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    df["adx"] = dx.ewm(span=period, adjust=False).mean()
    return df


def _add_bollinger_bands(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    sma = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()
    df["bb_upper"] = sma + 2 * std
    df["bb_lower"] = sma - 2 * std
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / sma * 100
    return df


def _add_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df


def get_current_indicator_values(df: pd.DataFrame, indicators: dict | None = None) -> dict:
    """Extract latest indicator values as a dict."""
    if df is None or df.empty:
        return {}

    last = df.iloc[-1]
    result = {
        "ema_20": round(float(last.get("ema_20", 0)), 2) if "ema_20" in df.columns else None,
        "ema_50": round(float(last.get("ema_50", 0)), 2) if "ema_50" in df.columns else None,
        "ema_200": round(float(last.get("ema_200", 0)), 2) if "ema_200" in df.columns else None,
        "rsi": round(float(last.get("rsi", 50)), 1) if "rsi" in df.columns else None,
        "atr": round(float(last.get("atr", 0)), 2) if "atr" in df.columns else None,
        "adx": round(float(last.get("adx", 20)), 1) if "adx" in df.columns else None,
        "bb_width": round(float(last.get("bb_width", 0)), 2) if "bb_width" in df.columns else None,
        "macd": round(float(last.get("macd", 0)), 4) if "macd" in df.columns else None,
        "macd_signal": round(float(last.get("macd_signal", 0)), 4) if "macd_signal" in df.columns else None,
        "macd_hist": round(float(last.get("macd_hist", 0)), 4) if "macd_hist" in df.columns else None,
    }
    return {k: v for k, v in result.items() if v is not None}
