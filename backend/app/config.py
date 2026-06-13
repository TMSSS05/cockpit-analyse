"""Application configuration via pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Market Analysis Cockpit configuration."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    # Data sources
    USE_MOCK_DATA: bool = False
    YFINANCE_ENABLED: bool = True
    CCXT_ENABLED: bool = True

    # DuckDB cache
    DUCKDB_PATH: str = str(DATA_DIR / "market_data.duckdb")
    CACHE_EXPIRE_HOURS: int = 1

    # Analysis thresholds
    PROXIMITY_ATR_MULTIPLIER: float = 0.5  # level is "close" if within 0.5 ATR
    HIGH_VOLATILITY_ATR_PERCENTILE: float = 0.75
    STRONG_TREND_ADX: float = 25.0
    RSI_EXTREME_HIGH: float = 70.0
    RSI_EXTREME_LOW: float = 30.0

    # Session times (UTC)
    ASIA_START: str = "00:00"
    ASIA_END: str = "08:00"
    LONDON_START: str = "08:00"
    LONDON_END: str = "16:00"
    NY_START: str = "13:00"
    NY_END: str = "21:00"

    # Market assets
    ASSETS: dict[str, dict[str, str | None]] = {
        "XAUUSD": {"name": "Gold", "yfinance": "GC=F", "ccxt": None, "type": "commodity"},
        "BTC": {"name": "Bitcoin", "yfinance": "BTC-USD", "ccxt": "BTC/USDT", "type": "crypto"},
        "NASDAQ": {"name": "Nasdaq", "yfinance": "^IXIC", "ccxt": None, "type": "index"},
        "OIL": {"name": "Crude Oil", "yfinance": "CL=F", "ccxt": None, "type": "commodity"},
        "EURUSD": {"name": "EUR/USD", "yfinance": "EURUSD=X", "ccxt": None, "type": "forex"},
    }

    TIMEFRAMES: dict[str, str] = {
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
    }

    model_config = {"env_prefix": "MAC_", "env_file": ".env"}

    SYMBOLS_TO_YFINANCE: ClassVar[dict[str, str]] = {
        "XAUUSD": "GC=F",
        "BTC": "BTC-USD",
        "NASDAQ": "^IXIC",
        "OIL": "CL=F",
        "EURUSD": "EURUSD=X",
    }


settings = Settings()
