"""GET /api/graph — account linkage graph for the canvas visualisation."""
from fastapi import APIRouter
from backend.services.graph_builder import get_graph_payload

router = APIRouter()


@router.get("/graph")
async def get_graph():
    return get_graph_payload()
