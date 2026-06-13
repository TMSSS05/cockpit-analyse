"""Drawings CRUD — persist chart overlay drawings (Fibonacci, trend lines, etc.) to DuckDB."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import duckdb
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/drawings", tags=["drawings"])

class DrawingPoint(BaseModel):
    timestamp: float | None = None
    price: float | None = None
    value: float | None = None


class DrawingCreate(BaseModel):
    symbol: str
    timeframe: str
    overlay_name: str
    id: str | None = None
    points: list[DrawingPoint] = []
    styles: dict = {}


class DrawingUpdate(BaseModel):
    points: list[DrawingPoint] | None = None
    styles: dict | None = None


class DrawingOut(BaseModel):
    id: str
    symbol: str
    timeframe: str
    overlay_name: str
    points: list[dict]
    styles: dict
    created_at: str
    updated_at: str


def _get_conn() -> duckdb.DuckDBPyConnection:
    path = settings.DUCKDB_PATH
    return duckdb.connect(str(path))


def _ensure_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS drawings (
            id           TEXT PRIMARY KEY,
            symbol       TEXT NOT NULL,
            timeframe    TEXT NOT NULL,
            overlay_name TEXT NOT NULL,
            points       JSON,
            styles       JSON,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )


def _row_to_drawing(row: tuple) -> DrawingOut:
    return DrawingOut(
        id=row[0],
        symbol=row[1],
        timeframe=row[2],
        overlay_name=row[3],
        points=json.loads(row[4]) if isinstance(row[4], str) else (row[4] or []),
        styles=json.loads(row[5]) if isinstance(row[5], str) else (row[5] or {}),
        created_at=str(row[6]) if row[6] else "",
        updated_at=str(row[7]) if row[7] else "",
    )


@router.get("/{symbol}")
async def list_drawings(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe filter"),
):
    """Get all persisted drawings for a symbol + timeframe pair."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        rows = conn.execute(
            "SELECT * FROM drawings WHERE symbol = ? AND timeframe = ? ORDER BY created_at",
            [symbol.upper(), timeframe],
        ).fetchall()
        return {"drawings": [_row_to_drawing(r) for r in rows]}
    finally:
        conn.close()


@router.post("")
async def create_drawing(body: DrawingCreate):
    """Save a new drawing overlay."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        drawing_id = body.id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO drawings (id, symbol, timeframe, overlay_name, points, styles, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                drawing_id,
                body.symbol.upper(),
                body.timeframe,
                body.overlay_name,
                json.dumps([p.model_dump() for p in body.points]),
                json.dumps(body.styles),
                now,
                now,
            ],
        )
        row = conn.execute("SELECT * FROM drawings WHERE id = ?", [drawing_id]).fetchone()
        if row is None:
            raise HTTPException(status_code=500, detail="Failed to create drawing")
        return _row_to_drawing(row)
    finally:
        conn.close()


@router.put("/{drawing_id}")
async def update_drawing(drawing_id: str, body: DrawingUpdate):
    """Update points and/or styles of an existing drawing."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        existing = conn.execute("SELECT * FROM drawings WHERE id = ?", [drawing_id]).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Drawing not found")

        now = datetime.now(timezone.utc).isoformat()
        if body.points is not None:
            conn.execute(
                "UPDATE drawings SET points = ?, updated_at = ? WHERE id = ?",
                [json.dumps([p.model_dump() for p in body.points]), now, drawing_id],
            )
        if body.styles is not None:
            conn.execute(
                "UPDATE drawings SET styles = ?, updated_at = ? WHERE id = ?",
                [json.dumps(body.styles), now, drawing_id],
            )
        if body.points is None and body.styles is None:
            conn.execute("UPDATE drawings SET updated_at = ? WHERE id = ?", [now, drawing_id])

        row = conn.execute("SELECT * FROM drawings WHERE id = ?", [drawing_id]).fetchone()
        return _row_to_drawing(row)
    finally:
        conn.close()


@router.delete("/{drawing_id}")
async def delete_drawing(drawing_id: str):
    """Remove a drawing overlay."""
    conn = _get_conn()
    try:
        _ensure_table(conn)
        existing = conn.execute("SELECT * FROM drawings WHERE id = ?", [drawing_id]).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Drawing not found")
        conn.execute("DELETE FROM drawings WHERE id = ?", [drawing_id])
        return {"deleted": drawing_id}
    finally:
        conn.close()
