from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("")
async def list_assets():
    timeframes = list(settings.TIMEFRAMES.keys())
    return {
        "assets": [
            {
                "symbol": symbol,
                "name": meta.get("name", symbol),
                "timeframes": timeframes,
            }
            for symbol, meta in settings.ASSETS.items()
        ],
    }
