"""
CineOps Master Orchestrator.
Coordinates the multi-agent production lifecycle across Director, ObsProducer, and StudioHead.
Supports both Live real-time execution and Deterministic Replay mode.
"""

import os
import json
import time
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from libs.models import (
    CineOpsProductionEvent,
    EventType,
    AgentRole,
    StoryboardPayload,
    ToolCallPayload,
    ToolResultPayload,
)
from libs.event_bus import event_bus, EventBus
from external.gemini_client import GeminiClient
from external.grafana_mcp import GrafanaMCPClient
from services.agents.director import DirectorAgent
from services.agents.obs_producer import ObservabilityProducerAgent
from services.agents.studio_head import StudioHeadAgent


class CineOpsOrchestrator:
    """Master Orchestrator running the film production pipeline."""

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        grafana_mcp: Optional[GrafanaMCPClient] = None,
        bus: Optional[EventBus] = None,
    ) -> None:
        self.gemini = gemini_client or GeminiClient()
        self.mcp = grafana_mcp or GrafanaMCPClient()
        self.bus = bus or event_bus
        self.director = DirectorAgent(self.gemini)
        self.obs_producer = ObservabilityProducerAgent(self.mcp, self.gemini)
        self.studio_head = StudioHeadAgent(self.gemini)

    async def _emit(
        self,
        production_id: str,
        scene_num: int,
        scene_title: str,
        sender: AgentRole,
        event_type: EventType,
        payload: Dict[str, Any],
    ) -> None:
        event = CineOpsProductionEvent(
            production_id=production_id,
            scene_number=scene_num,
            scene_title=scene_title,
            sender=sender,
            event_type=event_type,
            payload=payload,
        )
        await self.bus.publish(event)

    async def run_live_production(self, mission: str, scenario_type: str = "microservice_rescue") -> str:
        """Execute live end-to-end multi-agent production pipeline."""
        production_id = f"PROD-{uuid.uuid4().hex[:8].upper()}"
        start_time = time.time()

        # Step 1: Director crafts Storyboard Breakdown
        storyboard = self.director.create_storyboard(mission)
        await self._emit(production_id, 0, "Production Kickoff", AgentRole.DIRECTOR, EventType.STORYBOARD_BREAKDOWN, storyboard.model_dump())

        evidences: List[Dict[str, Any]] = []

        # Scene 1: Metrics investigation
        await self._emit(production_id, 1, "Scene 1: Anomaly Triage", AgentRole.DIRECTOR, EventType.AGENT_THOUGHT, {"thought": "P0 Alert detected. Requesting Grafana Prometheus telemetry to isolate error spike."})
        await self._emit(production_id, 1, "Scene 1: Anomaly Triage", AgentRole.OBS_PRODUCER, EventType.MCP_TOOL_CALL, {"mcp_server": "grafana-mcp", "tool_name": "grafana_query_prometheus", "arguments": {"query": "sum(rate(http_requests_total{status=~'5..'}[5m]))", "start": "now-15m"}})
        
        m_res = self.obs_producer.execute_metrics_investigation("sum(rate(http_requests_total{status=~'5..'}[5m]))")
        await self._emit(production_id, 1, "Scene 1: Anomaly Triage", AgentRole.OBS_PRODUCER, EventType.MCP_TOOL_RESULT, m_res["tool_result"])
        await self._emit(production_id, 1, "Scene 1: Anomaly Triage", AgentRole.OBS_PRODUCER, EventType.SCENE_EVIDENCE, {"summary": m_res["evidence_summary"], "key_metrics": m_res["key_metrics"]})
        evidences.append(m_res)

        # Scene 2: Log investigation
        await self._emit(production_id, 2, "Scene 2: Root Cause Hunting", AgentRole.DIRECTOR, EventType.AGENT_THOUGHT, {"thought": "Prometheus confirms 42% 5xx spike. Dispatching ObsProducer to scan Loki error stacktraces."})
        await self._emit(production_id, 2, "Scene 2: Root Cause Hunting", AgentRole.OBS_PRODUCER, EventType.MCP_TOOL_CALL, {"mcp_server": "grafana-mcp", "tool_name": "grafana_query_loki", "arguments": {"query": "{service='payment-api'} |= 'ERROR'", "limit": 20}})
        
        l_res = self.obs_producer.execute_logs_investigation("{service='payment-api'} |= 'ERROR'")
        await self._emit(production_id, 2, "Scene 2: Root Cause Hunting", AgentRole.OBS_PRODUCER, EventType.MCP_TOOL_RESULT, l_res["tool_result"])
        await self._emit(production_id, 2, "Scene 2: Root Cause Hunting", AgentRole.OBS_PRODUCER, EventType.SCENE_EVIDENCE, {"summary": l_res["evidence_summary"], "stacktrace": l_res["stacktrace_sample"]})
        evidences.append(l_res)

        # Scene 3: Safety audit & auto-healing
        await self._emit(production_id, 3, "Scene 3: Safety Audit & Self-Healing", AgentRole.DIRECTOR, EventType.AGENT_THOUGHT, {"thought": "Root cause identified as DB pool exhaustion. Proposing pool expansion from 20 to 100."})
        verdict = self.studio_head.audit_remediation("Scale DB Connection Pool 20 -> 100", "DBConnectionPoolTimeout")
        await self._emit(production_id, 3, "Scene 3: Safety Audit & Self-Healing", AgentRole.STUDIO_HEAD, EventType.SAFETY_VERDICT, verdict.model_dump())
        
        healing_res = self.studio_head.execute_self_healing(verdict)
        await self._emit(production_id, 3, "Scene 3: Safety Audit & Self-Healing", AgentRole.STUDIO_HEAD, EventType.SCENE_EVIDENCE, healing_res)
        evidences.append(healing_res)

        # Final Wrap: Wrap-up report
        elapsed = time.time() - start_time
        wrap_report = self.director.generate_wrap_report(production_id, mission, elapsed, evidences)
        await self._emit(production_id, 3, "Production Wrap", AgentRole.DIRECTOR, EventType.PRODUCTION_WRAP, wrap_report.model_dump())

        return production_id

    async def run_replay_production(self, scenario_type: str = "microservice_rescue", interval_sec: float = 0.5) -> str:
        """Stream a pre-recorded golden production run for 100% deterministic demo playback."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scenario_path = os.path.join(base_dir, "scenarios", f"{scenario_type}.json")
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Scenario {scenario_type} not found at {scenario_path}")

        with open(scenario_path, "r", encoding="utf-8") as f:
            events_data = json.load(f)

        production_id = f"REPLAY-{uuid.uuid4().hex[:8].upper()}"
        for item in events_data:
            item["production_id"] = production_id
            item["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            event = CineOpsProductionEvent(**item)
            await self.bus.publish(event)
            if interval_sec > 0:
                await asyncio.sleep(interval_sec)

        return production_id
