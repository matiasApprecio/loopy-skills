{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from loopy_agent_audit_packager.scripts.audit_packager import to_markdown\
\
\
def test_markdown_contains_core_sections():\
    agent = \{\
        "agent_id": "22222222-2222-2222-2222-222222222222",\
        "name": "Agent",\
        "runtime_type": "OpenClaw v2.1",\
        "current_version": "1.0.0",\
        "risk_level": "low",\
        "roles": [\{"role_key": "rk", "role_name": "rn"\}],\
        "tools": [\{"tool_key": "k", "tool_name": "n", "scope": "s", "approval_required": False\}],\
        "guardrails": [\{"guardrail_key": "no_pii", "summary": "No PII", "policy_id": "GR-001"\}],\
        "data_access": [\{"system_key": "sys", "system_name": "SYS", "classification": "internal", "scope": "read"\}],\
        "dependencies": [\{"dep_type": "service", "dep_ref": "orion", "dep_name": "Orion"\}],\
    \}\
    md = to_markdown(agent)\
    assert "# Agent Audit Report" in md\
    assert "## Tools" in md\
    assert "## Guardrails" in md\
    assert "## Data Access" in md}