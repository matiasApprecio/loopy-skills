{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 """\
send_registry_event.py\
\
Envia eventos al webhook Loopy:\
POST https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook\
\
- Retries: 3 intentos con backoff exponencial\
- Circuit breaker: si 3 fallos consecutivos, se pausa el envio y se alerta\
- Idempotency key: sha256(agent_id + event_type + YYYY-MM-DDTHH:00)\
"""\
\
import json\
import os\
import time\
from dataclasses import dataclass\
from typing import Any, Dict, Optional, Tuple\
\
import requests\
\
from .common import get_config, idempotency_key, hour_bucket, safe_json_dumps\
from .validate_descriptor import ValidationError, validate\
\
STATE_PATH_DEFAULT = os.getenv("LOOPY_REGISTRY_STATE_PATH", ".loopy_registry_state.json")\
\
\
@dataclass\
class CircuitState:\
    consecutive_failures: int = 0\
    paused: bool = False\
    last_error: str = ""\
\
\
def _load_state(path: str) -> CircuitState:\
    try:\
        with open(path, "r", encoding="utf-8") as f:\
            data = json.load(f)\
        return CircuitState(\
            consecutive_failures=int(data.get("consecutive_failures", 0)),\
            paused=bool(data.get("paused", False)),\
            last_error=str(data.get("last_error", "")),\
        )\
    except FileNotFoundError:\
        return CircuitState()\
    except Exception:\
        # If state corrupt, fail open but reset\
        return CircuitState()\
\
\
def _save_state(path: str, state: CircuitState) -> None:\
    data = \{\
        "consecutive_failures": state.consecutive_failures,\
        "paused": state.paused,\
        "last_error": state.last_error,\
    \}\
    with open(path, "w", encoding="utf-8") as f:\
        json.dump(data, f, ensure_ascii=False, indent=2)\
\
\
def _should_pause(state: CircuitState) -> bool:\
    return state.paused or state.consecutive_failures >= 3\
\
\
def _backoff_seconds(attempt: int) -> float:\
    # attempt 1..3\
    return min(8.0, 1.0 * (2 ** (attempt - 1)))\
\
\
def send_event(payload: Dict[str, Any], state_path: str = STATE_PATH_DEFAULT) -> Tuple[int, str]:\
    cfg = get_config()\
    state = _load_state(state_path)\
\
    if _should_pause(state):\
        msg = "Circuit breaker activo: envios pausados por fallos consecutivos. Reintenta mas tarde o revisa configuracion."\
        return 0, msg\
\
    # Fill idempotency key deterministically by hour\
    agent_id = payload.get("agent", \{\}).get("agent_id", "")\
    event_type = payload.get("event_type", "")\
    bucket = hour_bucket()\
    payload["idempotency_key"] = idempotency_key(agent_id=agent_id, event_type=event_type, bucket=bucket)\
\
    # Validate before sending\
    try:\
        validate(payload)\
    except ValidationError as e:\
        return 0, f"Payload invalido: \{e\}"\
\
    headers = \{\
        "Authorization": f"Bearer \{cfg.token\}",\
        "Content-Type": "application/json",\
    \}\
\
    body = safe_json_dumps(payload)\
\
    last_err = ""\
    for attempt in range(1, 4):\
        try:\
            r = requests.post(cfg.webhook_url, data=body.encode("utf-8"), headers=headers, timeout=10)\
            status = r.status_code\
            text = r.text or ""\
\
            if status in (200, 208):\
                # success, reset breaker\
                state.consecutive_failures = 0\
                state.paused = False\
                state.last_error = ""\
                _save_state(state_path, state)\
                return status, text\
\
            # Non-success response counts as failure\
            last_err = f"HTTP \{status\}: \{text[:500]\}"\
        except Exception as ex:\
            last_err = f"exception: \{type(ex).__name__\}: \{str(ex)[:300]\}"\
\
        # failure path\
        state.consecutive_failures += 1\
        state.last_error = last_err\
        if state.consecutive_failures >= 3:\
            state.paused = True\
            _save_state(state_path, state)\
            return 0, f"Circuit breaker activado tras 3 fallos. Ultimo error: \{last_err\}"\
\
        _save_state(state_path, state)\
        time.sleep(_backoff_seconds(attempt))\
\
    return 0, f"Fallo enviando evento tras retries. Ultimo error: \{last_err\}"\
\
\
if __name__ == "__main__":\
    # Ejemplo CLI minimal:\
    # export LOOPY_AGENT_REGISTRY_TOKEN=...\
    # export LOOPY_ORGANIZATION_ID=...\
    # python -m scripts.send_registry_event\
    from .build_descriptor import build_payload\
\
    cfg = get_config()\
    payload = build_payload(cfg.organization_id, "agent.registered")\
    status, msg = send_event(payload)\
    print(status, msg)}