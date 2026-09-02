"""
FastAPI Server Gateway for CineOps Studio.
Exposes REST endpoints and real-time Server-Sent Events (SSE) stream.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from libs.event_bus import event_bus
from services.orchestrator import CineOpsOrchestrator


class ProductionStartRequest(BaseModel):
    mission: Optional[str] = None
    scenario_type: str = "microservice_rescue"
    mode: str = "replay"  # live | replay
    interval_sec: float = 0.5


app = FastAPI(
    title="CineOps Studio API",
    description="Enterprise Multi-Agent Observability Platform with Hollywood-Grade Orchestration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = CineOpsOrchestrator()


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Verify backend and MCP readiness."""
    return {
        "status": "HEALTHY",
        "service": "CineOps Studio Gateway",
        "gemini_configured": bool(orchestrator.gemini.api_key),
        "grafana_configured": bool(orchestrator.mcp.token),
        "mcp_tools_available": len(orchestrator.mcp.list_tools()),
    }


@app.get("/api/scenarios")
async def list_scenarios() -> Dict[str, Any]:
    """List available cinematic incident response storylines."""
    return {
        "scenarios": [
            {
                "id": "microservice_rescue",
                "name": "Scene A: Microservice Snowball Outage & Self-Healing",
                "default_mission": "Payment Gateway P0 Outage: 500 Error Spike Investigation & Autonomous Healing",
                "track": "Grafana Labs (Prometheus + Loki)",
            },
            {
                "id": "agent_observability",
                "name": "Scene B: AI Agent Fleet Meta-Observability & Token Optimization",
                "default_mission": "AI Agent Fleet Meta-Observability: Token Budget & Pyroscope Latency Optimization",
                "track": "Grafana Labs (Prometheus + Pyroscope)",
            },
        ]
    }


@app.post("/api/production/start")
async def start_production(
    req: ProductionStartRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Start an autonomous production run in background."""
    mission = req.mission or "Autonomous Incident Response & Observability"
    event_bus.clear()

    if req.mode == "live":
        background_tasks.add_task(
            orchestrator.run_live_production, mission, req.scenario_type
        )
    else:
        background_tasks.add_task(
            orchestrator.run_replay_production,
            req.scenario_type,
            req.interval_sec,
        )

    return {
        "status": "STARTED",
        "mode": req.mode,
        "scenario_type": req.scenario_type,
        "mission": mission,
    }


@app.get("/api/production/events")
async def stream_events(request: Request) -> StreamingResponse:
    """Server-Sent Events endpoint streaming structured production events in real-time."""
    return StreamingResponse(
        event_bus.subscribe(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/production/clear")
async def clear_production() -> Dict[str, str]:
    """Reset event bus history."""
    event_bus.clear()
    return {"status": "CLEARED"}


# Mount static web frontend if built
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
