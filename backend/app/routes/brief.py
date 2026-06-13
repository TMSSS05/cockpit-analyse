from __future__ import annotations

from fastapi import APIRouter, Query

from app.analysis.scenarios import generate_scenarios
from app.analysis.scoring import compute_analysis_score, score_to_action_bias, score_to_label
from app.config import settings
from app.data.market_data import MarketDataProvider

router = APIRouter(prefix="/api/brief", tags=["brief"])

MARKET_NAMES = {sym: cfg["name"] for sym, cfg in settings.ASSETS.items()}


@router.get("")
async def get_market_brief(
    timeframe: str = Query("4h", description="Timeframe for the brief"),
    symbols: str = Query(None, description="Comma-separated symbols, defaults to all"),
):
    provider = MarketDataProvider()
    target_symbols = [s.strip().upper() for s in symbols.split(",")] if symbols else list(settings.ASSETS.keys())

    results = []
    for symbol in target_symbols:
        df = await provider.get_historical_data(symbol, timeframe)
        if df is None or df.empty:
            continue

        price = float(df["close"].iloc[-1])
        score = compute_analysis_score(df)
        scenarios = generate_scenarios(df)

        results.append({
            "symbol": symbol,
            "name": MARKET_NAMES.get(symbol, symbol),
            "price": round(price, 2),
            "score": {
                "value": score,
                "label": score_to_label(score),
                "action_bias": score_to_action_bias(score),
            },
            "scenario_count": len(scenarios),
        })

    return {
        "timeframe": timeframe,
        "asset_count": len(results),
        "assets": results,
    }
