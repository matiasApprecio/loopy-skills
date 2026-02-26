import pytest

from loopy_agent_registry.scripts.validate_descriptor import ValidationError, validate


def base_payload():
    return {
        "idempotency_key": "x",
        "organization_id": "11111111-1111-1111-1111-111111111111",
        "event_type": "agent.updated",
        "agent": {
            "agent_id": "22222222-2222-2222-2222-222222222222",
            "name": "A",
            "description": "",
            "runtime_type": "OpenClaw v2.1",
            "current_version": "1.0.0",
            "risk_level": "low",
            "risk_rationale": "",
            "roles": [{"role_key": "rk", "role_name": "rn"}],
            "tasks": [{"task_ref": "JIRA-1", "title": "T", "status": "open"}],
            "tools": [{"tool_key": "k", "tool_name": "n", "scope": "s", "approval_required": False}],
            "guardrails": [{"guardrail_key": "g", "summary": "no pii", "policy_id": "P1"}],
            "data_access": [{"system_key": "sys", "system_name": "SYS", "classification": "internal", "scope": "read"}],
            "dependencies": [{"dep_type": "service", "dep_ref": "x", "dep_name": "X"}],
        },
    }


def test_valid_payload():
    p = base_payload()
    validate(p)


def test_high_risk_requires_rationale():
    p = base_payload()
    p["agent"]["risk_level"] = "high"
    p["agent"]["risk_rationale"] = ""
    with pytest.raises(ValidationError) as e:
        validate(p)
    assert "agent.risk_rationale" in str(e.value)


def test_heartbeat_minimal_ok():
    p = {
        "idempotency_key": "x",
        "organization_id": "11111111-1111-1111-1111-111111111111",
        "event_type": "agent.heartbeat",
        "agent": {"agent_id": "22222222-2222-2222-2222-222222222222"},
    }
    validate(p)


def test_reject_pii_email_in_description():
    p = base_payload()
    p["agent"]["description"] = "contacto: test@example.com"
    with pytest.raises(ValidationError):
        validate(p)