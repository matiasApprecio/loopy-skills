#!/usr/bin/env python3
"""
register_agent.py - Script temporal para registrar el agente en Loopy
"""

import sys
import os
import json

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports absolutos
from scripts.agent_context_reader import get_agent_context
from scripts.subagent_scanner import get_all_subagents
from scripts.skills_scanner import get_all_skills
from scripts.tasks_extractor import get_all_tasks

# Configuración
WEBHOOK_URL = "https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook"
ORG_ID = os.getenv('LOOPY_ORGANIZATION_ID', 'matias-apprecio-org')
TOKEN = os.getenv('LOOPY_AGENT_REGISTRY_TOKEN', '')
USER_EMAIL = os.getenv('LOOPY_USER_EMAIL', '')  # NUEVO: Email del usuario

print("🔧 Loopy Agent Registry v2.0 - Registro de Agente")
print("=" * 50)

# 1. Obtener datos
print("\n📊 Recolectando datos del agente...")
ctx = get_agent_context()
subagents = get_all_subagents()
skills = get_all_skills()
tasks = get_all_tasks()

print(f"   ✓ Agente principal: {ctx.get('name', 'Unknown')}")
print(f"   ✓ Sub-agentes: {len(subagents)}")
print(f"   ✓ Skills: {len(skills)}")
print(f"   ✓ Tareas: {len(tasks)}")

# 2. Construir payload
print("\n📦 Construyendo payload...")

agent_payload = {
    "agent_id": ctx.get("agent_id", "unknown"),
    "name": ctx.get("name", "Agent"),
    "email": USER_EMAIL,  # NUEVO: Email para registro en Loopy
    "description": ctx.get("description", "")[:300],
    "runtime_type": ctx.get("runtime_type", "OpenClaw"),
    "current_version": "1.0.0",
    "emoji": ctx.get("emoji", "🤖"),
    "risk_level": "medium",
    "risk_rationale": "Acceso a servicios corporativos y datos de usuario",
    "roles": ctx.get("roles", []),
    "sub_agents": subagents,
    "skills": skills[:15],
    "tasks": tasks[:20],
    "memory_summary": ctx.get("memory_summary", {})
}

payload = {
    "idempotency_key": f"{ctx.get('agent_id', 'unknown')}_registered_{os.getenv('HOUR_BUCKET', 'current')}",
    "organization_id": ORG_ID,
    "event_type": "agent.registered",
    "agent": agent_payload
}

print(f"   ✓ Payload listo ({len(json.dumps(payload))} bytes)")

# 3. Guardar payload para review
output_file = "/tmp/loopy_payload.json"
with open(output_file, 'w') as f:
    json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
print(f"   ✓ Payload guardado en: {output_file}")

# 4. Intentar enviar (si hay token)
if TOKEN and TOKEN != 'token-pending-config':
    print("\n📡 Enviando a Loopy Orion...")
    try:
        import requests
        import hashlib
        from datetime import datetime
        
        # Generar idempotency key
        hour_bucket = datetime.utcnow().strftime("%Y-%m-%dT%H:00")
        idem_key = hashlib.sha256(
            f"{agent_payload['agent_id']}_registered_{hour_bucket}".encode()
        ).hexdigest()[:32]
        payload["idempotency_key"] = idem_key
        
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        print(f"   ✅ Respuesta: HTTP {response.status_code}")
        print(f"   📝 Body: {response.text[:200]}")
        
        if response.status_code in [200, 208]:
            print("\n🎉 ¡Agente registrado exitosamente en Loopy Orion!")
        else:
            print(f"\n⚠️  Respuesta inesperada: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error enviando: {e}")
        print("   El payload está guardado en /tmp/loopy_payload.json")
        print("   Puedes revisarlo y enviarlo manualmente")
else:
    print("\n⚠️  TOKEN no configurado")
    print("   Para enviar, configura: export LOOPY_AGENT_REGISTRY_TOKEN='tu-token'")
    print("   El payload está guardado en /tmp/loopy_payload.json")

print("\n" + "=" * 50)
print("✅ Proceso completado")

# Mostrar preview del payload
print("\n📋 Preview del payload (primeros 1000 chars):")
preview = json.dumps(payload, indent=2, ensure_ascii=False, default=str)[:1000]
print(preview)
if len(json.dumps(payload)) > 1000:
    print("... (truncado)")