"""
validate_descriptor.py

Valida el payload contra el esquema exacto esperado por Loopy.
Incluye reglas extra:
- risk_level=high requiere risk_rationale no vacio.
- No permitir PII obvia en campos de texto.
"""

from typing import Any, Dict, List, Tuple

from .common import (
    ALLOWED_EVENT_TYPES,
    CLASSIFICATIONS,
    DEP_TYPES,
    RISK_LEVELS,
    looks_like_pii,
)


class ValidationError(Exception):
    def __init__(self, errors: List[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


def _req(obj: Dict[str, Any], key: str, errors: List[str]) -> Any:
    if key not in obj:
        errors.append(f"missing required field: {key}")
        return None
    return obj[key]


def _is_uuid_like(value: str) -> bool:
    # Lax UUID check; keep deterministic and portable
    import re
    return bool(re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value or ""))


def validate(payload: Dict[str, Any]) -> None:
    errors: List[str] = []

    idem = _req(payload, "idempotency_key", errors)
    org_id = _req(payload, "organization_id", errors)
    ev = _req(payload, "event_type", errors)
    agent = _req(payload, "agent", errors)

    if org_id and not _is_uuid_like(org_id):
        errors.append("organization_id must be UUID")

    if ev and ev not in ALLOWED_EVENT_TYPES:
        errors.append("event_type invalid")

    if not isinstance(agent, dict):
        errors.append("agent must be object")
    else:
        agent_id = agent.get("agent_id")
        if not agent_id or not _is_uuid_like(agent_id):
            errors.append("agent.agent_id must be UUID")

        if ev != "agent.heartbeat":
            _validate_full_agent(agent, errors)
        else:
            # heartbeat minimal: only agent_id required
            pass

    if errors:
        raise ValidationError(errors)


def _validate_text_field(value: Any, field_path: str, errors: List[str], allow_empty: bool = True) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        errors.append(f"{field_path} must be string")
        return
    if not allow_empty and not value.strip():
        errors.append(f"{field_path} must be non-empty")
    if looks_like_pii(value):
        errors.append(f"{field_path} appears to contain PII")


def _validate_full_agent(agent: Dict[str, Any], errors: List[str]) -> None:
    # required in full agent
    for f in ["name", "runtime_type", "current_version", "risk_level"]:
        if f not in agent:
            errors.append(f"missing agent.{f}")

    _validate_text_field(agent.get("name"), "agent.name", errors, allow_empty=False)
    _validate_text_field(agent.get("description", ""), "agent.description", errors, allow_empty=True)
    _validate_text_field(agent.get("runtime_type"), "agent.runtime_type", errors, allow_empty=False)
    _validate_text_field(agent.get("current_version"), "agent.current_version", errors, allow_empty=False)

    risk = agent.get("risk_level")
    if risk and risk not in RISK_LEVELS:
        errors.append("agent.risk_level invalid")
    if risk == "high":
        rr = agent.get("risk_rationale", "")
        _validate_text_field(rr, "agent.risk_rationale", errors, allow_empty=False)

    # arrays
    _validate_roles(agent.get("roles", []), errors)
    _validate_tasks(agent.get("tasks", []), errors)
    _validate_tools(agent.get("tools", []), errors)
    _validate_guardrails(agent.get("guardrails", []), errors)
    _validate_data_access(agent.get("data_access", []), errors)
    _validate_dependencies(agent.get("dependencies", []), errors)


def _validate_roles(roles: Any, errors: List[str]) -> None:
    if roles is None:
        return
    if not isinstance(roles, list):
        errors.append("agent.roles must be array")
        return
    for i, r in enumerate(roles):
        if not isinstance(r, dict):
            errors.append(f"agent.roles[{i}] must be object")
            continue
        _validate_text_field(r.get("role_key"), f"agent.roles[{i}].role_key", errors, allow_empty=False)
        _validate_text_field(r.get("role_name"), f"agent.roles[{i}].role_name", errors, allow_empty=False)


def _validate_tasks(tasks: Any, errors: List[str]) -> None:
    if tasks is None:
        return
    if not isinstance(tasks, list):
        errors.append("agent.tasks must be array")
        return
    for i, t in enumerate(tasks):
        if not isinstance(t, dict):
            errors.append(f"agent.tasks[{i}] must be object")
            continue
        _validate_text_field(t.get("task_ref"), f"agent.tasks[{i}].task_ref", errors, allow_empty=False)
        _validate_text_field(t.get("title"), f"agent.tasks[{i}].title", errors, allow_empty=False)
        _validate_text_field(t.get("status"), f"agent.tasks[{i}].status", errors, allow_empty=False)


def _validate_tools(tools: Any, errors: List[str]) -> None:
    if tools is None:
        return
    if not isinstance(tools, list):
        errors.append("agent.tools must be array")
        return
    for i, t in enumerate(tools):
        if not isinstance(t, dict):
            errors.append(f"agent.tools[{i}] must be object")
            continue
        _validate_text_field(t.get("tool_key"), f"agent.tools[{i}].tool_key", errors, allow_empty=False)
        _validate_text_field(t.get("tool_name"), f"agent.tools[{i}].tool_name", errors, allow_empty=False)
        _validate_text_field(t.get("scope"), f"agent.tools[{i}].scope", errors, allow_empty=False)
        ar = t.get("approval_required", False)
        if not isinstance(ar, bool):
            errors.append(f"agent.tools[{i}].approval_required must be boolean")


def _validate_guardrails(guardrails: Any, errors: List[str]) -> None:
    if guardrails is None:
        return
    if not isinstance(guardrails, list):
        errors.append("agent.guardrails must be array")
        return
    for i, g in enumerate(guardrails):
        if not isinstance(g, dict):
            errors.append(f"agent.guardrails[{i}] must be object")
            continue
        _validate_text_field(g.get("guardrail_key"), f"agent.guardrails[{i}].guardrail_key", errors, allow_empty=False)
        _validate_text_field(g.get("summary"), f"agent.guardrails[{i}].summary", errors, allow_empty=False)
        pid = g.get("policy_id", "")
        if pid is not None:
            _validate_text_field(pid, f"agent.guardrails[{i}].policy_id", errors, allow_empty=True)


def _validate_data_access(da: Any, errors: List[str]) -> None:
    if da is None:
        return
    if not isinstance(da, list):
        errors.append("agent.data_access must be array")
        return
    for i, d in enumerate(da):
        if not isinstance(d, dict):
            errors.append(f"agent.data_access[{i}] must be object")
            continue
        _validate_text_field(d.get("system_key"), f"agent.data_access[{i}].system_key", errors, allow_empty=False)
        _validate_text_field(d.get("system_name"), f"agent.data_access[{i}].system_name", errors, allow_empty=False)
        cl = d.get("classification")
        if cl not in CLASSIFICATIONS:
            errors.append(f"agent.data_access[{i}].classification invalid")
        _validate_text_field(d.get("scope"), f"agent.data_access[{i}].scope", errors, allow_empty=False)


def _validate_dependencies(deps: Any, errors: List[str]) -> None:
    if deps is None:
        return
    if not isinstance(deps, list):
        errors.append("agent.dependencies must be array")
        return
    for i, d in enumerate(deps):
        if not isinstance(d, dict):
            errors.append(f"agent.dependencies[{i}] must be object")
            continue
        dt = d.get("dep_type")
        if dt not in DEP_TYPES:
            errors.append(f"agent.dependencies[{i}].dep_type invalid")
        _validate_text_field(d.get("dep_ref"), f"agent.dependencies[{i}].dep_ref", errors, allow_empty=False)
        _validate_text_field(d.get("dep_name"), f"agent.dependencies[{i}].dep_name", errors, allow_empty=False)