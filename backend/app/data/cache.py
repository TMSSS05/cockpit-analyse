from __future__ import annotations

import duckdb
import pandas as pd
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import settings


class MarketDataCache:
    """Local DuckDB cache for market data to reduce API calls."""

    def __init__(self) -> None:
        db_path = Path(settings.DUCKDB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(db_path))
        self._init_tables()

    def _init_tables(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS candles (
                symbol VARCHAR,
                timeframe VARCHAR,
                timestamp TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, timeframe, timestamp)
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                symbol VARCHAR PRIMARY KEY,
                data JSON,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_cached_candles(
        self, symbol: str, timeframe: str, count: int = 200
    ) -> pd.DataFrame | None:
        expiry = datetime.now(UTC) - timedelta(hours=settings.CACHE_EXPIRE_HOURS)
        result = self._conn.execute(
            """
            SELECT timestamp, open, high, low, close, volume
            FROM candles
            WHERE symbol = ? AND timeframe = ? AND cached_at > ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            [symbol, timeframe, expiry, count],
        )
        df = result.fetchdf()
        if df.empty:
            return None
        return df.sort_values("timestamp").reset_index(drop=True)

    def store_candles(
        self, symbol: str, timeframe: str, df: pd.DataFrame
    ) -> None:
        if df.empty:
            return
        data = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
        data["symbol"] = symbol
        data["timeframe"] = timeframe
        data["cached_at"] = datetime.now(UTC)
        self._conn.execute("DELETE FROM candles WHERE symbol = ? AND timeframe = ?", [symbol, timeframe])
        self._conn.execute(
            "INSERT INTO candles (symbol, timeframe, timestamp, open, high, low, close, volume, cached_at) "
            "SELECT symbol, timeframe, timestamp, open, high, low, close, volume, cached_at FROM data",
        )

    def get_cached_analysis(self, symbol: str) -> dict | None:
        result = self._conn.execute(
            "SELECT data FROM analysis_cache WHERE symbol = ?",
            [symbol],
        )
        row = result.fetchone()
        if row:
            import json
            return json.loads(row[0])
        return None

    def store_analysis(self, symbol: str, data: dict) -> None:
        import json
        self._conn.execute(
            "INSERT OR REPLACE INTO analysis_cache (symbol, data, cached_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            [symbol, json.dumps(data)],
        )

    def close(self) -> None:
        self._conn.close()
