---
name: loopy-agent-registry
version: 2.0.0
description: "Registra y actualiza agentes OpenClaw en Loopy Orion con datos reales. Lee IDENTITY.md, SOUL.md, sub-agentes, skills instaladas y tareas pendientes. Envía heartbeat periódico."
compatibility:
  runtimes:
    - OpenClaw 2026.2+
requirements:
  secrets:
    - LOOPY_AGENT_REGISTRY_TOKEN
    - LOOPY_ORGANIZATION_ID
  environment:
    - LOOPY_WEBHOOK_URL
  python_packages:
    - pyyaml
metadata:
  owner: Apprecio / Matias
  category: agent-governance
  safety_level: strict
use_cases:
  - Registrar agente principal y sub-agentes en Loopy Orion
  - Sincronizar ficha completa del agente (roles, tareas, skills, sub-agentes)
  - Enviar heartbeat con métricas reales del sistema
  - Mantener inventario actualizado de agentes corporativos
guardrails:
  - Nunca incluir tokens, secretos ni contenido sensible en el payload.
  - No incluir PII (emails, teléfonos, datos personales reales).
  - Sanitizar rutas de archivos (usar paths relativos).
  - Validar schema antes de enviar.
  - Idempotency key determinística por hora.
  - Circuit breaker: si hay 3 fallos consecutivos, pausar envíos.
  - Limitar tamaño de payload a < 500KB (truncar listas largas).
---

## Novedades v2.0

Esta versión major incluye:

### ✅ Datos Reales del Agente
- Lee automáticamente `IDENTITY.md` (nombre, emoji, avatar)
- Parsea `SOUL.md` (descripción, roles, personalidad)
- Extrae información de `AGENTS.md`

### ✅ Sub-Agentes
- Escanea `/root/.openclaw/agents/` automáticamente
- Lee configuración de cada sub-agente (`agent.yaml`, `SOUL.md`)
- Incluye: nombre, modelo, descripción, workspace, estado

### ✅ Skills Instaladas  
- Lista todas las skills en `/root/.openclaw/workspace/skills/`
- Extrae: nombre, versión, descripción, categoría
- Categoriza automáticamente (google-workspace, automation, etc.)

### ✅ Tareas y Proyectos
- Extrae tareas de `MEMORY.md` (sección Proyectos Pendientes)
- Lee tareas de archivos `memory/YYYY-MM-DD.md` (últimos 14 días)
- Parsea checkboxes markdown: `- [ ] Tarea pendiente`

### ✅ Métricas del Sistema
- Conteo de notas diarias
- Lista de cron jobs activos
- Resumen de memoria (última actualización, entradas totales)

## Estructura del Payload

```json
{
  "idempotency_key": "sha256-hash",
  "organization_id": "uuid",
  "event_type": "agent.registered",
  "agent": {
    "agent_id": "uuid-real-del-agente",
    "name": "Matías",
    "description": "Meta-Agente de Apprecio...",
    "runtime_type": "OpenClaw v2026.2.13",
    "emoji": "🤖",
    "risk_level": "medium",
    
    "roles": [{"role_key": "meta_agent", "role_name": "Meta-Agente"}],
    "tasks": [{"task_ref": "...", "title": "...", "status": "pending"}],
    "tools": [{"tool_key": "gws-gmail", "tool_name": "Google Gmail"}],
    "guardrails": [{"guardrail_key": "no_pii", "summary": "..."}],
    "data_access": [{"system_key": "openclaw", "system_name": "OpenClaw"}],
    "dependencies": [{"dep_type": "service", "dep_ref": "orion"}],
    
    "sub_agents": [
      {
        "agent_id": "karpesky",
        "name": "Karpesky",
        "description": "Especialista en n8n workflows",
        "model": "kimi-coding/k2p5",
        "status": "active"
      }
    ],
    
    "skills": [
      {"name": "gws-gmail", "version": "1.0.0", "category": "google-workspace"}
    ],
    
    "cron_jobs": [
      {"name": "daily-memory", "schedule": "0 9 * * *", "status": "active"}
    ],
    
    "memory_summary": {
      "last_updated": "2026-03-09T10:00:00",
      "daily_notes_count": 12,
      "total_entries": 156
    }
  }
}
```

## Archivos del Skill

```
loopy-agent-registry/
├── SKILL.MD                           # Este archivo
├── scripts/
│   ├── __init__.py
│   ├── common.py                      # Config y utilidades
│   ├── agent_context_reader.py        # Lee IDENTITY.md, SOUL.md, AGENTS.md
│   ├── subagent_scanner.py            # Escanee sub-agentes
│   ├── skills_scanner.py              # Lista skills instaladas
│   ├── tasks_extractor.py             # Extrae tareas de memory
│   ├── build_descriptor.py            # Construye payload final
│   ├── validate_descriptor.py         # Valida contra schema
│   ├── send_registry_event.py         # Envía a Loopy
│   └── heartbeat.sh                   # Script de heartbeat
├── references/
│   └── agent-schema.json              # Schema de validación
└── tests/
    └── test_build_descriptor.py       # Tests unitarios
```

## Workflow

1. **build_descriptor.py** llama a:
   - `agent_context_reader.get_agent_context()` → Datos del agente principal
   - `subagent_scanner.get_all_subagents()` → Lista de sub-agentes
   - `skills_scanner.get_all_skills()` → Skills instaladas
   - `tasks_extractor.get_all_tasks()` → Tareas pendientes

2. **Arma el payload** con toda la información

3. **validate_descriptor.py** valida contra schema

4. **send_registry_event.py** hace POST al webhook de Loopy

## Instalación

```bash
# 1. Clonar o copiar el skill a tu workspace
cp -r loopy-agent-registry ~/.openclaw/workspace/skills/

# 2. Configurar secrets
openclaw secrets set LOOPY_AGENT_REGISTRY_TOKEN "tu-token-aqui"
openclaw secrets set LOOPY_ORGANIZATION_ID "tu-org-uuid-aqui"

# 3. (Opcional) Configurar webhook URL
export LOOPY_WEBHOOK_URL="https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook"

# 4. Probar
openclaw agent --message "registra mi agente en Loopy"
```

## Uso

### Registrar agente completo
```
"registra mi agente en Loopy"
"actualiza mi registro en Orion"
"envía mi ficha a Loopy"
```

### Heartbeat
```
"envía heartbeat"
"manda heartbeat a Loopy"
```

## Estados en Loopy

- **online**: heartbeat <= 5 minutos
- **stale**: >5 y <=60 minutos  
- **offline**: >60 minutos
- **revoked**: revocado permanentemente

## Troubleshooting

| Código | Problema | Solución |
|--------|----------|----------|
| 401 | Token inválido | Revisar `LOOPY_AGENT_REGISTRY_TOKEN` |
| 422 | Credencial no configurada | Registrar credencial en Loopy Orion |
| 400 | Payload inválido | Ejecutar `validate_descriptor.py` para detalles |
| 413 | Payload muy grande | Revisar que listas no excedan límites (20 tareas, 10 skills) |
| 0 | Circuit breaker | Esperar 1 hora o revisar configuración |

## Dependencias

```bash
pip install pyyaml requests
```

## Limitaciones

- **No envía**: Contenido completo de MEMORY.md (solo metadatos)
- **No envía**: Credenciales, tokens, contraseñas
- **No envía**: Contenido de archivos del usuario
- **Límites**: Máximo 20 tareas, 10 skills, 10 sub-agentes, 10 cron jobs

## Changelog

### v2.0.0 (2026-03-09)
- ✨ Lee datos reales de IDENTITY.md, SOUL.md
- ✨ Soporte para sub-agentes
- ✨ Lista automática de skills instaladas
- ✨ Extracción de tareas de memory
- ✨ Métricas del sistema (cron jobs, memory stats)

### v1.0.0
- Registro básico de agentes
- Heartbeat periódico

## Soporte

Contactar: matias@apprecio.com