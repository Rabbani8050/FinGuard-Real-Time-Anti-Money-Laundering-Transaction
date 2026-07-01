"""WS /ws/live — push scored transactions to the dashboard in real time."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio, json
from datetime import datetime

router = APIRouter()
_connections: list[WebSocket] = []


async def broadcast(payload: dict) -> None:
    dead = []
    for ws in _connections:
        try:
            await ws.send_text(json.dumps(payload, default=str))
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)


@router.websocket("/ws/live")
async def live_feed(ws: WebSocket):
    await ws.accept()
    _connections.append(ws)
    try:
        while True:
            await ws.receive_text()   # keep-alive ping from client
    except WebSocketDisconnect:
        _connections.remove(ws)
