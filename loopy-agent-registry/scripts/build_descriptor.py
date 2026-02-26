"""
build_descriptor.py

Transforma el contexto del agente OpenClaw al JSON que acepta Loopy.
Este script asume que OpenClaw expone un dict "agent_context".
En tu runtime real, reemplaza get_openclaw_context() con el acceso nativo.

Salida: dict listo para validate y send.
"""

from typing import Any, Dict, List, Optional
from .common import ALLOWED_EVENT_TYPES


def get_openclaw_context() -> Dict[str, Any]:
    """
    Placeholder: en OpenClaw real, esto debe leer:
    - agent_id estable
    - nombre, descripcion
    - runtime/version
    - roles, tareas, tools, guardrails, data access, dependencies
    """
    return {
        "agent_id": "00000000-0000-0000-0000-000000000001",
        "name": "Example Agent",
        "description": "Agente de ejemplo sin PII",
        "runtime_type": "OpenClaw v2.1",
        "current_version": "1.0.0",
        "risk_level": "low",
        "risk_rationale": "",
        "roles": [{"role_key": "example", "role_name": "Example"}],
        "tasks": [{"task_ref": "JIRA-123", "title": "Demo task", "status": "open"}],
        "tools": [{"tool_key": "http", "tool_name": "HTTP Client", "scope": "POST webhook", "approval_required": False}],
        "guardrails": [{"guardrail_key": "no_pii", "summary": "No incluir PII", "policy_id": "GR-001"}],
        "data_access": [{"system_key": "loopy", "system_name": "Loopy", "classification": "internal", "scope": "registry"}],
        "dependencies": [{"dep_type": "service", "dep_ref": "orion", "dep_name": "Orion"}],
    }


def build_payload(
    organization_id: str,
    event_type: str,
    agent_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"event_type invalid: {event_type}")

    ctx = agent_fields or get_openclaw_context()

    agent: Dict[str, Any] = {
        "agent_id": ctx["agent_id"],
        "name": ctx.get("name", ""),
        "description": ctx.get("description", ""),
        "runtime_type": ctx.get("runtime_type", "OpenClaw"),
        "current_version": ctx.get("current_version", "0.0.0"),
        "risk_level": ctx.get("risk_level", "low"),
        "risk_rationale": ctx.get("risk_rationale", ""),
        "roles": ctx.get("roles", []) or [],
        "tasks": ctx.get("tasks", []) or [],
        "tools": ctx.get("tools", []) or [],
        "guardrails": ctx.get("guardrails", []) or [],
        "data_access": ctx.get("data_access", []) or [],
        "dependencies": ctx.get("dependencies", []) or [],
    }

    # Heartbeat minimal
    if event_type == "agent.heartbeat":
        agent = {"agent_id": agent["agent_id"]}

    payload: Dict[str, Any] = {
        "idempotency_key": "",  # se completa en send_registry_event.py
        "organization_id": organization_id,
        "event_type": event_type,
        "agent": agent,
    }
    return payload