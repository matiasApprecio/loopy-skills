{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
audit_packager.py\
\
Genera Markdown de auditoria sin secretos.\
Input: un "agent descriptor" en el formato Loopy (agent object o payload completo).\
Fuente configurada por AGENT_DESCRIPTOR_SOURCE:\
- inline_json: AGENT_DESCRIPTOR_INLINE_JSON\
- file: AGENT_DESCRIPTOR_FILE_PATH\
\
En runtime real, integrar con build_descriptor o fuente interna.\
"""\
\
import json\
import os\
from datetime import datetime, timezone\
from typing import Any, Dict, List, Optional\
\
from loopy_agent_registry.scripts.common import looks_like_pii\
\
\
def _load_descriptor() -> Dict[str, Any]:\
    source = os.getenv("AGENT_DESCRIPTOR_SOURCE", "inline_json").strip()\
    if source == "inline_json":\
        raw = os.getenv("AGENT_DESCRIPTOR_INLINE_JSON", "\{\}")\
        return json.loads(raw)\
    if source == "file":\
        path = os.getenv("AGENT_DESCRIPTOR_FILE_PATH", "")\
        if not path:\
            return \{\}\
        with open(path, "r", encoding="utf-8") as f:\
            return json.load(f)\
    return \{\}\
\
\
def _sanitize_text(s: str) -> str:\
    if not s:\
        return ""\
    if looks_like_pii(s):\
        return "[REDACTED_PII]"\
    return s\
\
\
def to_markdown(descriptor_or_payload: Dict[str, Any], recent_timeline: Optional[List[Dict[str, Any]]] = None) -> str:\
    # Accept payload or agent object\
    agent = descriptor_or_payload.get("agent") if "agent" in descriptor_or_payload else descriptor_or_payload\
    if not isinstance(agent, dict):\
        agent = \{\}\
\
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")\
\
    name = _sanitize_text(str(agent.get("name", "")))\
    agent_id = str(agent.get("agent_id", ""))\
    runtime = _sanitize_text(str(agent.get("runtime_type", "")))\
    ver = _sanitize_text(str(agent.get("current_version", "")))\
    risk = str(agent.get("risk_level", ""))\
    rationale = _sanitize_text(str(agent.get("risk_rationale", "")))\
\
    roles = agent.get("roles", []) or []\
    tasks = agent.get("tasks", []) or []\
    tools = agent.get("tools", []) or []\
    guardrails = agent.get("guardrails", []) or []\
    data_access = agent.get("data_access", []) or []\
    deps = agent.get("dependencies", []) or []\
\
    md = []\
    md.append("# Agent Audit Report")\
    md.append("")\
    md.append(f"- Generated: \{now\}")\
    md.append(f"- Agent name: \{name\}")\
    md.append(f"- Agent id: \{agent_id\}")\
    md.append(f"- Runtime: \{runtime\}")\
    md.append(f"- Version: \{ver\}")\
    md.append(f"- Risk level: \{risk\}")\
    if risk == "high":\
        md.append(f"- Risk rationale: \{rationale\}")\
    md.append("")\
\
    md.append("## Roles")\
    if roles:\
        for r in roles:\
            md.append(f"- \{r.get('role_key','')\}: \{_sanitize_text(str(r.get('role_name','')))\}")\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Tasks")\
    if tasks:\
        for t in tasks:\
            md.append(f"- \{t.get('task_ref','')\}: \{_sanitize_text(str(t.get('title','')))\} (\{_sanitize_text(str(t.get('status','')))\})")\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Tools")\
    if tools:\
        for t in tools:\
            scope = _sanitize_text(str(t.get("scope", "")))\
            ar = bool(t.get("approval_required", False))\
            md.append(f"- \{t.get('tool_key','')\}: \{_sanitize_text(str(t.get('tool_name','')))\} | scope: \{scope\} | approval_required: \{ar\}")\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Guardrails")\
    if guardrails:\
        for g in guardrails:\
            pid = _sanitize_text(str(g.get("policy_id", "")))\
            pid_part = f" | policy_id: \{pid\}" if pid else ""\
            md.append(f"- \{g.get('guardrail_key','')\}: \{_sanitize_text(str(g.get('summary','')))\}\{pid_part\}")\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Data Access")\
    if data_access:\
        for d in data_access:\
            md.append(\
                f"- \{d.get('system_key','')\}: \{_sanitize_text(str(d.get('system_name','')))\} "\
                f"| classification: \{d.get('classification','')\} | scope: \{_sanitize_text(str(d.get('scope','')))\}"\
            )\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Dependencies")\
    if deps:\
        for d in deps:\
            md.append(f"- \{d.get('dep_type','')\}: \{d.get('dep_ref','')\} (\{_sanitize_text(str(d.get('dep_name','')))\})")\
    else:\
        md.append("- None")\
    md.append("")\
\
    md.append("## Recent Timeline (Summary)")\
    if recent_timeline:\
        for e in recent_timeline[:20]:\
            ts = _sanitize_text(str(e.get("event_ts", "")))\
            et = _sanitize_text(str(e.get("event_type", "")))\
            md.append(f"- \{ts\} | \{et\}")\
    else:\
        md.append("- Not provided")\
    md.append("")\
\
    return "\\n".join(md)\
\
\
if __name__ == "__main__":\
    d = _load_descriptor()\
    print(to_markdown(d))}