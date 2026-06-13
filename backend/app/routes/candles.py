from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.data.market_data import MarketDataProvider
from app.data.cache import MarketDataCache

router = APIRouter(prefix="/api/candles", tags=["candles"])


@router.get("/{symbol}")
async def get_candles(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe: 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(200, ge=10, le=1000),
):
    provider = MarketDataProvider()
    cache = MarketDataCache()

    symbol_upper = symbol.upper()

    if symbol_upper not in settings.ASSETS:
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol_upper}")

    df = await provider.get_historical_data(symbol_upper, timeframe)

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol_upper} on {timeframe}")

    # Trim to requested limit
    if len(df) > limit:
        df = df.tail(limit)

    candles = []
    for _, row in df.iterrows():
        candles.append({
            "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
            "volume": round(float(row["volume"]), 2),
        })

    return {
        "symbol": symbol_upper,
        "timeframe": timeframe,
        "count": len(candles),
        "candles": candles,
    }
