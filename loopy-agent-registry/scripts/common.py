{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import hashlib\
import json\
import os\
import re\
from dataclasses import dataclass\
from datetime import datetime, timezone\
from typing import Any, Dict, Optional\
\
DEFAULT_WEBHOOK_URL = "https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook"\
\
ALLOWED_EVENT_TYPES = \{\
    "agent.registered",\
    "agent.updated",\
    "agent.heartbeat",\
    "agent.revoked",\
\}\
\
RISK_LEVELS = \{"low", "medium", "high"\}\
CLASSIFICATIONS = \{"public", "internal", "confidential", "restricted"\}\
DEP_TYPES = \{"subagent", "service", "dataset", "queue", "api"\}\
\
\
@dataclass\
class LoopyConfig:\
    webhook_url: str\
    organization_id: str\
    token: str\
\
\
def get_config() -> LoopyConfig:\
    webhook_url = os.getenv("LOOPY_WEBHOOK_URL", DEFAULT_WEBHOOK_URL).strip()\
    organization_id = os.getenv("LOOPY_ORGANIZATION_ID", "").strip()\
    token = os.getenv("LOOPY_AGENT_REGISTRY_TOKEN", "").strip()\
\
    if not webhook_url:\
        raise ValueError("LOOPY_WEBHOOK_URL missing")\
    if not organization_id:\
        raise ValueError("LOOPY_ORGANIZATION_ID missing")\
    if not token:\
        raise ValueError("LOOPY_AGENT_REGISTRY_TOKEN missing")\
\
    return LoopyConfig(webhook_url=webhook_url, organization_id=organization_id, token=token)\
\
\
def hour_bucket(dt: Optional[datetime] = None) -> str:\
    if dt is None:\
        dt = datetime.now(timezone.utc)\
    dt = dt.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)\
    return dt.strftime("%Y-%m-%dT%H:00")\
\
\
def idempotency_key(agent_id: str, event_type: str, bucket: Optional[str] = None) -> str:\
    if bucket is None:\
        bucket = hour_bucket()\
    raw = f"\{agent_id\}\{event_type\}\{bucket\}".encode("utf-8")\
    return hashlib.sha256(raw).hexdigest()\
\
\
_PII_PATTERNS = [\
    re.compile(r"\\b[\\w\\.-]+@[\\w\\.-]+\\.\\w+\\b", re.IGNORECASE),  # emails\
    re.compile(r"\\b(\\+?\\d[\\d\\s\\-]\{7,\}\\d)\\b"),  # phone-like\
]\
\
\
def looks_like_pii(text: str) -> bool:\
    if not text:\
        return False\
    for p in _PII_PATTERNS:\
        if p.search(text):\
            return True\
    return False\
\
\
def safe_json_dumps(obj: Any) -> str:\
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)}