"""
build_descriptor.py v2.0

Transforma el contexto REAL del agente OpenClaw al JSON que acepta Loopy.

NUEVO: Lee datos reales de:
- IDENTITY.md, SOUL.md, AGENTS.md (agente principal)
- Sub-agentes en ~/.openclaw/agents/
- Skills instaladas en ~/.openclaw/workspace/skills/
- Tareas de MEMORY.md y notas diarias
- Stats de sistema

Salida: dict listo para validate y send.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Importar los nuevos módulos
from .common import ALLOWED_EVENT_TYPES
from .agent_context_reader import get_agent_context
from .subagent_scanner import get_all_subagents, get_subagent_tasks
from .skills_scanner import get_all_skills
from .tasks_extractor import get_all_tasks


def get_cron_jobs_summary() -> List[Dict[str, str]]:
    """
    Obtiene resumen de cron jobs del sistema.
    Usa openclaw cron list.
    """
    jobs = []
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', 'cron', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                # Parsear líneas de cron
                if line.startswith(' ') and len(line.strip()) > 20:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        jobs.append({
                            'name': parts[1] if len(parts) > 1 else 'unknown',
                            'schedule': ' '.join(parts[2:4]) if len(parts) > 3 else 'daily',
                            'status': 'active'
                        })
    except Exception:
        pass
    
    return jobs[:10]  # Limitar a 10 jobs


def build_payload(
    organization_id: str,
    event_type: str,
    agent_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Construye el payload completo para enviar a Loopy.
    
    Args:
        organization_id: UUID de la organización en Loopy
        event_type: Tipo de evento (agent.registered, agent.updated, agent.heartbeat)
        agent_fields: Campos adicionales opcionales
    
    Returns:
        Dict con el payload completo
    """
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"event_type invalid: {event_type}")
    
    # 1. Obtener contexto del agente principal
    ctx = get_agent_context()
    
    # 2. Obtener sub-agentes
    subagents = get_all_subagents()
    
    # 3. Obtener skills
    skills = get_all_skills()
    
    # 4. Obtener tareas
    tasks = get_all_tasks()
    
    # 5. Obtener cron jobs
    cron_jobs = get_cron_jobs_summary()
    
    # Construir estructura de agente
    agent: Dict[str, Any] = {
        # Identidad básica
        "agent_id": ctx["agent_id"],
        "name": ctx["name"],
        "description": ctx["description"][:300],
        "runtime_type": ctx["runtime_type"],
        "current_version": ctx["current_version"],
        "emoji": ctx.get("emoji", "🤖"),
        
        # Riesgo
        "risk_level": ctx["risk_level"],
        "risk_rationale": ctx["risk_rationale"],
        
        # Roles desde SOUL.md
        "roles": ctx.get("roles", []),
        
        # Tareas del agente principal
        "tasks": tasks[:20],  # Limitar a 20 tareas
        
        # Tools inferidos de skills
        "tools": [
            {
                "tool_key": skill["name"],
                "tool_name": skill["name"],
                "scope": skill.get("category", "general"),
                "approval_required": False
            }
            for skill in skills[:10]  # Top 10 skills
        ],
        
        # Guardrails básicos
        "guardrails": [
            {
                "guardrail_key": "no_pii",
                "summary": "No exponer información personal identifiable (PII)",
                "policy_id": "GR-001"
            },
            {
                "guardrail_key": "confirm_writes",
                "summary": "Confirmar antes de ejecutar operaciones de escritura",
                "policy_id": "GR-002"
            }
        ],
        
        # Acceso a datos
        "data_access": [
            {
                "system_key": "openclaw_workspace",
                "system_name": "OpenClaw Workspace",
                "classification": "internal",
                "scope": "workspace"
            },
            {
                "system_key": "loopy_orion",
                "system_name": "Loopy Orion",
                "classification": "internal",
                "scope": "registry"
            }
        ],
        
        # Dependencias
        "dependencies": [
            {
                "dep_type": "service",
                "dep_ref": "openclaw",
                "dep_name": "OpenClaw Gateway"
            },
            {
                "dep_type": "service", 
                "dep_ref": "orion",
                "dep_name": "Loopy Orion"
            }
        ],
        
        # NUEVO: Sub-agentes
        "sub_agents": subagents,
        
        # NUEVO: Skills instaladas
        "skills": skills,
        
        # NUEVO: Cron jobs
        "cron_jobs": cron_jobs,
        
        # NUEVO: Memory summary (sin el contenido completo)
        "memory_summary": ctx.get("memory_summary", {})
    }
    
    # Si es heartbeat, enviar versión minimal
    if event_type == "agent.heartbeat":
        agent = {
            "agent_id": agent["agent_id"],
            "name": agent["name"],
            "status": "online",
            "sub_agents_count": len(subagents),
            "pending_tasks": len([t for t in tasks if t.get("status") == "pending"])
        }
    
    # Agregar campos adicionales si se proporcionan
    if agent_fields:
        agent.update(agent_fields)
    
    # Construir payload final
    payload: Dict[str, Any] = {
        "idempotency_key": "",  # Se completa en send_registry_event.py
        "organization_id": organization_id,
        "event_type": event_type,
        "agent": agent,
    }
    
    return payload


def build_minimal_payload(
    organization_id: str,
    agent_id: str
) -> Dict[str, Any]:
    """
    Construye un payload mínimo para heartbeat rápido.
    """
    return {
        "idempotency_key": "",
        "organization_id": organization_id,
        "event_type": "agent.heartbeat",
        "agent": {
            "agent_id": agent_id,
            "status": "online"
        }
    }


if __name__ == "__main__":
    # Test
    import json
    from .common import get_config
    
    cfg = get_config()
    
    print("=== Payload Completo ===")
    payload = build_payload(cfg.organization_id, "agent.registered")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print("\n=== Payload Heartbeat ===")
    hb_payload = build_minimal_payload(cfg.organization_id, payload["agent"]["agent_id"])
    print(json.dumps(hb_payload, indent=2, ensure_ascii=False))