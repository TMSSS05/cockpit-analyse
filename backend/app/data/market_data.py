from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import pandas as pd
import yfinance as yf

from app.config import settings
from app.data.cache import MarketDataCache
from app.data.mock_data import generate_mock_candles

log = logging.getLogger(__name__)

_cache: MarketDataCache | None = None


def get_cache() -> MarketDataCache:
    global _cache
    if _cache is None:
        _cache = MarketDataCache()
    return _cache


def get_candles(
    symbol: str,
    timeframe: str = "1h",
    count: int = 200,
    force_mock: bool = False,
) -> pd.DataFrame:
    """Fetch OHLCV candles for a symbol.

    Tries live data first (yfinance), falls back to cache, then mock data.
    """
    if force_mock or settings.USE_MOCK_DATA:
        log.info("Using mock data for %s", symbol)
        return generate_mock_candles(symbol, timeframe, count)

    cache = get_cache()
    cached = cache.get_cached_candles(symbol, timeframe, count)
    if cached is not None:
        return cached

    df = _fetch_live_candles(symbol, timeframe, count)
    if df is not None and not df.empty:
        cache.store_candles(symbol, timeframe, df)
        return df

    log.warning("Live data failed for %s, using mock fallback", symbol)
    return generate_mock_candles(symbol, timeframe, count)


def _fetch_live_candles(symbol: str, timeframe: str, count: int) -> pd.DataFrame | None:
    yf_symbol = settings.SYMBOLS_TO_YFINANCE.get(symbol)
    if not yf_symbol or not settings.YFINANCE_ENABLED:
        return None

    try:
        interval_map = {
            "5m": "5m",
            "15m": "15m",
            "1h": "60m",
            "4h": "1h",   # Will fetch 1h and resample
            "1d": "1d",
        }
        interval = interval_map.get(timeframe, "1h")
        period = _period_for_count(interval, count)

        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            return None

        df = df.rename(columns={
            "Open": "open", "High": "high",
            "Low": "low", "Close": "close", "Volume": "volume",
        })
        df = df[["open", "high", "low", "close", "volume"]]
        df.index.name = "timestamp"
        df = df.reset_index()

        # Resample to 4h if needed
        if timeframe == "4h" and interval == "1h":
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")
            resampled = df.resample("4h", closed="left", label="left").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }).dropna().reset_index()

            now = datetime.now(UTC)
            resampled = resampled[resampled["timestamp"] <= now - timedelta(hours=4)]
            df = resampled

        return df.tail(count).reset_index(drop=True)

    except Exception as e:
        log.error("yfinance error for %s: %s", symbol, e)
        return None


def _period_for_count(interval: str, count: int) -> str:
    rough_days = {
        "5m": count * 5 // (60 * 24) + 2,
        "15m": count * 15 // (60 * 24) + 2,
        "60m": count // 24 + 2,
        "1d": count + 5,
    }
    days = rough_days.get(interval, count)
    if days <= 7:
        return f"{max(days, 1)}d"
    if days <= 30:
        return "1mo"
    if days <= 90:
        return "3mo"
    return "6mo"


def get_latest_price(symbol: str) -> float | None:
    """Get the latest price for a symbol."""
    df = get_candles(symbol, "1h", count=5, force_mock=settings.USE_MOCK_DATA)
    if df is not None and not df.empty:
        return float(df["close"].iloc[-1])
    return None


def get_current_analysis(symbol: str) -> dict:
    """Get full analysis for a symbol. Tries cache first, then computes fresh."""
    cache = get_cache()
    cached = cache.get_cached_analysis(symbol)
    if cached:
        return cached

    # Compute fresh analysis (delegated to analysis modules via route)
    return {}


def get_assets_config() -> dict[str, dict[str, str | None]]:
    return settings.ASSETS


class MarketDataProvider:
    """Async wrapper for route convenience."""

    async def get_historical_data(
        self, symbol: str, timeframe: str = "1h", count: int = 200
    ) -> pd.DataFrame:
        return get_candles(symbol, timeframe, count)
