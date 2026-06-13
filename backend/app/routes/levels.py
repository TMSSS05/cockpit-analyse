from fastapi import APIRouter, HTTPException, Query

from app.analysis.levels import compute_all_levels, get_closest_level
from app.data.market_data import MarketDataProvider

router = APIRouter(prefix="/api/levels", tags=["levels"])


@router.get("/{symbol}")
async def get_levels(
    symbol: str,
    timeframe: str = Query("4h", description="Timeframe for level calculation"),
):
    provider = MarketDataProvider()
    symbol_upper = symbol.upper()

    df = await provider.get_historical_data(symbol_upper, timeframe)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol_upper}")

    levels = compute_all_levels(df)
    price = float(df["close"].iloc[-1])
    closest = get_closest_level(price, levels)

    return {
        "symbol": symbol_upper,
        "timeframe": timeframe,
        "current_price": round(price, 2),
        "levels": levels,
        "closest_level": closest,
    }
