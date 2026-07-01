"""FastAPI application entry point with lifespan, CORS, and route registration."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.db.mongo import connect as mongo_connect, disconnect as mongo_disconnect
from backend.db.cache import connect as redis_connect, disconnect as redis_disconnect
from backend.services.queue_consumer import start as queue_start, stop as queue_stop

from backend.api.transactions import router as tx_router
from backend.api.alerts import router as alert_router
from backend.api.graph import router as graph_router
from backend.api.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await mongo_connect()
    await redis_connect()
    await queue_start(num_workers=4)
    yield
    # Shutdown
    await queue_stop()
    await mongo_disconnect()
    await redis_disconnect()


app = FastAPI(
    title="FinGuard AML API",
    description="Real-time Anti-Money Laundering transaction analyser",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tx_router,    prefix="/api", tags=["Transactions"])
app.include_router(alert_router, prefix="/api", tags=["Alerts"])
app.include_router(graph_router, prefix="/api", tags=["Graph"])
app.include_router(ws_router,    tags=["WebSocket"])

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "FinGuard AML"}
