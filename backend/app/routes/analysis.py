from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.analysis.indicators import add_all_indicators
from app.analysis.market_structure import (
    analyze_momentum,
    analyze_trend,
    analyze_volatility,
    detect_breakout,
    detect_consolidation,
    detect_sweep,
)
from app.analysis.scenarios import generate_scenarios
from app.analysis.scoring import compute_analysis_score, score_to_action_bias, score_to_label
from app.data.market_data import MarketDataProvider

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/{symbol}")
async def get_analysis(
    symbol: str,
    timeframe: str = Query("1h", description="Primary analysis timeframe"),
):
    provider = MarketDataProvider()
    symbol_upper = symbol.upper()

    if symbol_upper not in settings.ASSETS:
        raise HTTPException(status_code=404, detail=f"Unknown symbol: {symbol_upper}")

    df = await provider.get_historical_data(symbol_upper, timeframe)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol_upper}")

    df = add_all_indicators(df)
    last = df.iloc[-1]

    trend = analyze_trend(df)
    momentum = analyze_momentum(df)
    volatility = analyze_volatility(df)
    is_consolidation = detect_consolidation(df)
    is_breakout = detect_breakout(df)
    is_sweep = detect_sweep(df)
    score = compute_analysis_score(df)
    scenarios = generate_scenarios(df)

    return {
        "symbol": symbol_upper,
        "timeframe": timeframe,
        "price": round(float(last["close"]), 2),
        "timestamp": str(last.name) if hasattr(last.name, "isoformat") else str(last.name),
        "indicators": {
            "ema_20": round(float(last.get("ema_20", 0)), 2),
            "ema_50": round(float(last.get("ema_50", 0)), 2),
            "ema_200": round(float(last.get("ema_200", 0)), 2),
            "rsi": round(float(last.get("rsi", 0)), 1),
            "atr": round(float(last.get("atr", 0)), 2),
            "adx": round(float(last.get("adx", 0)), 1),
            "bb_upper": round(float(last.get("bb_upper", 0)), 2),
            "bb_middle": round(float(last.get("bb_middle", 0)), 2),
            "bb_lower": round(float(last.get("bb_lower", 0)), 2),
            "macd_line": round(float(last.get("macd_line", 0)), 2),
            "macd_signal": round(float(last.get("macd_signal", 0)), 2),
            "macd_hist": round(float(last.get("macd_hist", 0)), 2),
        },
        "structure": {
            "trend": trend,
            "momentum": momentum,
            "volatility": volatility,
            "consolidation": is_consolidation,
            "breakout": is_breakout,
            "sweep": is_sweep,
        },
        "score": {
            "value": score,
            "label": score_to_label(score),
            "action_bias": score_to_action_bias(score),
        },
        "scenarios": scenarios,
    }
