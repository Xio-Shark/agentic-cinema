"""
Pydantic Data Models for CineOps Studio.
Strictly implements the event stream JSON Schema defined in DESIGN_AGENT_COMMUNICATION_SPEC.md.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid


class AgentRole(str, Enum):
    DIRECTOR = "Director"
    OBS_PRODUCER = "ObservabilityProducer"
    STUDIO_HEAD = "StudioHead"
    SYSTEM = "System"


class EventType(str, Enum):
    STORYBOARD_BREAKDOWN = "STORYBOARD_BREAKDOWN"
    AGENT_THOUGHT = "AGENT_THOUGHT"
    MCP_TOOL_CALL = "MCP_TOOL_CALL"
    MCP_TOOL_RESULT = "MCP_TOOL_RESULT"
    SCENE_EVIDENCE = "SCENE_EVIDENCE"
    SAFETY_VERDICT = "SAFETY_VERDICT"
    PRODUCTION_WRAP = "PRODUCTION_WRAP"


class SceneItem(BaseModel):
    scene_number: int
    title: str
    assigned_agent: AgentRole
    objective: str
    status: str = "PENDING"  # PENDING | IN_PROGRESS | COMPLETED


class StoryboardPayload(BaseModel):
    mission: str
    total_scenes: int
    scenes: List[SceneItem]


class ToolCallPayload(BaseModel):
    mcp_server: str = "grafana-mcp"
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str


class ToolResultPayload(BaseModel):
    call_id: str
    status: str  # success | error
    execution_time_ms: int
    data_summary: str
    raw_data: Optional[Any] = None


class SafetyVerdictPayload(BaseModel):
    action_proposed: str
    decision: str  # APPROVED | BLOCKED
    blast_radius: str  # LOW | MEDIUM | HIGH
    justification: str
    audit_hash: str


class WrapReportPayload(BaseModel):
    production_id: str
    mission: str
    duration_seconds: float
    total_scenes_completed: int
    root_cause_identified: str
    remediation_status: str
    telemetry_evidence_summary: str
    cost_and_performance_impact: str


class CineOpsProductionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    production_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    scene_number: int
    scene_title: str
    sender: AgentRole
    event_type: EventType
    payload: Dict[str, Any]
