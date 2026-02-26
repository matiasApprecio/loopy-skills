"""
guardrails_profiler.py

Traduce guardrails locales a formato Loopy:
[{guardrail_key, summary, policy_id}]

OPENCLAW_GUARDRAILS_SOURCE puede ser:
- "inline_json": lee variable OPENCLAW_GUARDRAILS_INLINE_JSON
- "file": lee OPENCLAW_GUARDRAILS_FILE_PATH
En runtime real, reemplazar por API nativa de OpenClaw.
"""

import json
import os
from typing import Any, Dict, List, Optional


def _load_local_guardrails() -> List[Dict[str, Any]]:
    source = os.getenv("OPENCLAW_GUARDRAILS_SOURCE", "inline_json").strip()

    if source == "inline_json":
        raw = os.getenv("OPENCLAW_GUARDRAILS_INLINE_JSON", "[]")
        return json.loads(raw)

    if source == "file":
        path = os.getenv("OPENCLAW_GUARDRAILS_FILE_PATH", "")
        if not path:
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Unknown source -> empty
    return []


def profile_guardrails(local_guardrails: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, str]]:
    lg = local_guardrails if local_guardrails is not None else _load_local_guardrails()

    out: List[Dict[str, str]] = []
    for g in lg:
        # Heuristica: map keys comunes
        key = str(g.get("key") or g.get("id") or g.get("name") or "guardrail").strip().lower().replace(" ", "_")
        summary = str(g.get("summary") or g.get("description") or g.get("rule") or "").strip()
        policy_id = g.get("policy_id")
        policy_id = str(policy_id).strip() if policy_id is not None else ""

        if not key:
            continue
        if not summary:
            summary = "Guardrail activo (resumen no disponible)"

        item = {"guardrail_key": key, "summary": summary}
        if policy_id:
            item["policy_id"] = policy_id
        out.append(item)

    return out


if __name__ == "__main__":
    print(json.dumps(profile_guardrails(), ensure_ascii=False, indent=2))