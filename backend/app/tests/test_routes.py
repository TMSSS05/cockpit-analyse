from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthRoute:
    async def test_health_returns_ok(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data


class TestAssetsRoute:
    async def test_list_assets(self, client: AsyncClient):
        response = await client.get("/api/assets")
        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert len(data["assets"]) > 0
        for asset in data["assets"]:
            assert "symbol" in asset
            assert "name" in asset
            assert "timeframes" in asset


class TestCandlesRoute:
    async def test_get_candles_xauusd(self, client: AsyncClient):
        response = await client.get("/api/candles/XAUUSD?timeframe=1h&limit=50")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert data["symbol"] == "XAUUSD"
            assert len(data["candles"]) > 0

    async def test_candles_unknown_symbol(self, client: AsyncClient):
        response = await client.get("/api/candles/UNKNOWN?timeframe=1h")
        assert response.status_code == 404

    async def test_candles_invalid_limit(self, client: AsyncClient):
        response = await client.get("/api/candles/XAUUSD?timeframe=1h&limit=5")
        assert response.status_code == 422


class TestAnalysisRoute:
    async def test_get_analysis_xauusd(self, client: AsyncClient):
        response = await client.get("/api/analysis/XAUUSD?timeframe=1h")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "indicators" in data
            assert "structure" in data
            assert "score" in data
            assert "scenarios" in data

    async def test_analysis_unknown_symbol(self, client: AsyncClient):
        response = await client.get("/api/analysis/UNKNOWN?timeframe=1h")
        assert response.status_code == 404


class TestLevelsRoute:
    async def test_get_levels_xauusd(self, client: AsyncClient):
        response = await client.get("/api/levels/XAUUSD?timeframe=4h")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "levels" in data
            assert "closest_level" in data


class TestBriefRoute:
    async def test_get_brief(self, client: AsyncClient):
        response = await client.get("/api/brief?timeframe=4h")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "assets" in data
            assert "asset_count" in data

    async def test_brief_specific_symbols(self, client: AsyncClient):
        response = await client.get("/api/brief?timeframe=4h&symbols=XAUUSD,BTC-USD")
        assert response.status_code in (200, 404)
