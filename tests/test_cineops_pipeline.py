"""
Comprehensive Test Suite for CineOps Studio.
Validates Models, EventBus, Grafana MCP Client, Agents, and Orchestrator in both Live and Replay modes.
"""

import pytest
import asyncio
from libs.models import (
    CineOpsProductionEvent,
    EventType,
    AgentRole,
    StoryboardPayload,
    SafetyVerdictPayload,
    WrapReportPayload,
)
from libs.event_bus import EventBus
from external.grafana_mcp import GrafanaMCPClient
from external.gemini_client import GeminiClient
from services.agents.director import DirectorAgent
from services.agents.obs_producer import ObservabilityProducerAgent
from services.agents.studio_head import StudioHeadAgent
from services.orchestrator import CineOpsOrchestrator


def test_models_serialization():
    """Verify strong typing and JSON serialization of production events."""
    event = CineOpsProductionEvent(
        production_id="PROD-TEST-101",
        scene_number=1,
        scene_title="Scene 1: Anomaly Test",
        sender=AgentRole.OBS_PRODUCER,
        event_type=EventType.MCP_TOOL_CALL,
        payload={"tool_name": "grafana_query_prometheus", "arguments": {"query": "up"}},
    )
    dumped = event.model_dump()
    assert dumped["production_id"] == "PROD-TEST-101"
    assert dumped["sender"] == "ObservabilityProducer"
    assert dumped["event_type"] == "MCP_TOOL_CALL"


def test_grafana_mcp_tool_definitions():
    """Verify MCP Tool definitions conform to Model Context Protocol standards."""
    mcp = GrafanaMCPClient()
    tools = mcp.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "grafana_query_prometheus" in tool_names
    assert "grafana_query_loki" in tool_names
    assert "grafana_query_pyroscope" in tool_names
    assert "grafana_get_active_alerts" in tool_names


def test_agents_local_contracts():
    """Verify contracts and responses of all 3 specialized agents."""
    gc = GeminiClient()
    gm = GrafanaMCPClient()
    
    # 1. Director
    director = DirectorAgent(gc)
    storyboard = director.create_storyboard("Test Outage Mission")
    assert isinstance(storyboard, StoryboardPayload)
    assert len(storyboard.scenes) == 3

    # 2. Obs Producer
    obs = ObservabilityProducerAgent(gm, gc)
    m_res = obs.execute_metrics_investigation("up")
    assert "key_metrics" in m_res
    l_res = obs.execute_logs_investigation("{service='test'}")
    assert "stacktrace_sample" in l_res

    # 3. Studio Head
    head = StudioHeadAgent(gc)
    verdict = head.audit_remediation("Scale Pool", "ConnectionTimeout")
    assert isinstance(verdict, SafetyVerdictPayload)
    assert verdict.decision == "APPROVED"
    assert verdict.blast_radius == "LOW"


@pytest.mark.asyncio
async def test_orchestrator_live_pipeline():
    """Verify end-to-end live multi-agent execution pipeline."""
    bus = EventBus()
    orch = CineOpsOrchestrator(bus=bus)
    prod_id = await orch.run_live_production("P0 Payment Gateway Crisis")
    assert prod_id.startswith("PROD-")
    history = bus.get_history()
    assert len(history) >= 10
    event_types = [e.event_type for e in history]
    assert EventType.STORYBOARD_BREAKDOWN in event_types
    assert EventType.MCP_TOOL_CALL in event_types
    assert EventType.SAFETY_VERDICT in event_types
    assert EventType.PRODUCTION_WRAP in event_types


@pytest.mark.asyncio
async def test_orchestrator_replay_mode():
    """Verify deterministic replay streaming from golden scenarios."""
    bus = EventBus()
    orch = CineOpsOrchestrator(bus=bus)
    replay_id = await orch.run_replay_production("microservice_rescue", interval_sec=0.01)
    assert replay_id.startswith("REPLAY-")
    history = bus.get_history()
    assert len(history) == 13
    assert history[-1].event_type == EventType.PRODUCTION_WRAP
