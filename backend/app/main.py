from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.assets import router as assets_router
from app.routes.candles import router as candles_router
from app.routes.analysis import router as analysis_router
from app.routes.levels import router as levels_router
from app.routes.brief import router as brief_router
from app.routes.drawings import router as drawings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Market Analysis Cockpit",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(assets_router)
app.include_router(candles_router)
app.include_router(analysis_router)
app.include_router(levels_router)
app.include_router(brief_router)
app.include_router(drawings_router)

