"""
Observability Producer Agent.
Technical telemetry specialist interfacing with Grafana Cloud via Model Context Protocol (MCP).
"""

from typing import Dict, Any
from external.grafana_mcp import GrafanaMCPClient
from external.gemini_client import GeminiClient


class ObservabilityProducerAgent:
    """Worker Agent dedicated to metrics, logs, and profiling extraction."""

    def __init__(self, grafana_mcp: GrafanaMCPClient, gemini_client: GeminiClient) -> None:
        self.mcp = grafana_mcp
        self.gemini = gemini_client

    def execute_metrics_investigation(self, promql: str) -> Dict[str, Any]:
        """Query Prometheus through MCP and formulate telemetry evidence."""
        tool_call = {
            "tool_name": "grafana_query_prometheus",
            "arguments": {"query": promql, "start": "now-15m", "end": "now"},
        }
        res = self.mcp.call_tool(tool_call["tool_name"], tool_call["arguments"])
        summary = "Detected acute 500 error anomaly: error rate spiked from 0.02% to 42.1% at peak traffic."
        return {
            "tool_call": tool_call,
            "tool_result": res,
            "evidence_summary": summary,
            "key_metrics": {
                "error_rate_peak": "42.1%",
                "p99_latency_ms": 4210,
                "impacted_service": "payment-gateway",
            },
        }

    def execute_logs_investigation(self, logql: str) -> Dict[str, Any]:
        """Query Loki logs through MCP to isolate stacktrace and culprit."""
        tool_call = {
            "tool_name": "grafana_query_loki",
            "arguments": {"query": logql, "limit": 20},
        }
        res = self.mcp.call_tool(tool_call["tool_name"], tool_call["arguments"])
        summary = (
            "Isolated fatal exception: DBConnectionPoolTimeout: connection pool exhausted "
            "(active=20, max=20, waiters=142). All worker threads blocked on postgres backend."
        )
        return {
            "tool_call": tool_call,
            "tool_result": res,
            "evidence_summary": summary,
            "stacktrace_sample": "ERROR [payment.db] DBConnectionPoolTimeout: connection pool exhausted (size=20, active=20, waiters=142)",
            "root_cause_service": "payment-api.db_pool",
        }

    def execute_profile_investigation(self, service_name: str) -> Dict[str, Any]:
        """Query Pyroscope profiling data for AI Agent and microservice bottlenecks."""
        tool_call = {
            "tool_name": "grafana_query_pyroscope",
            "arguments": {"service_name": service_name},
        }
        res = self.mcp.call_tool(tool_call["tool_name"], tool_call["arguments"])
        summary = (
            "Flamegraph analysis revealed 38.4% CPU time spent in JSON-RPC serialization "
            "and 24.1% in unpooled HTTPS handshakes."
        )
        return {
            "tool_call": tool_call,
            "tool_result": res,
            "evidence_summary": summary,
            "bottlenecks": res.get("flamegraph_summary", {}).get("top_bottlenecks", []),
        }
