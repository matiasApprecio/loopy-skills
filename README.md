# Loopy Skills for OpenClaw v2.0

Skills oficiales de Loopy para integrar agentes corporativos con Orion (Agent Registry).

## 🎯 Objetivo

Que cualquier agente de OpenClaw pueda registrarse, reportar su estado completo y mantenerse gobernado dentro de Loopy Orion.

## ✨ Novedades v2.0

### Datos Reales del Agente
- Lee automáticamente `IDENTITY.md`, `SOUL.md`, `AGENTS.md`
- Extrae nombre, descripción, roles, personalidad

### Sub-Agentes
- Escanea y registra todos los sub-agentes en `~/.openclaw/agents/`
- Lee su configuración y estado

### Skills Instaladas
- Lista automáticamente todas las skills
- Extrae nombre, versión, descripción, categoría

### Tareas y Proyectos
- Extrae tareas de `MEMORY.md` y notas diarias
- Parsea checkboxes markdown

## 📦 Skills Incluidos

### 1. loopy-agent-registry (v2.0) ⭐

**Función:**
- Registrar agente principal + sub-agentes
- Actualizar ficha completa con datos reales
- Enviar heartbeat con métricas

**Triggers:**
- `"registra mi agente en Loopy"`
- `"actualiza mi registro en Orion"`
- `"envía heartbeat"`

**Requiere:**
```bash
# Secrets
LOOPY_AGENT_REGISTRY_TOKEN
LOOPY_ORGANIZATION_ID

# Environment (opcional)
LOOPY_WEBHOOK_URL
# Default: https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook
```

**Instalación:**
```bash
# 1. Copiar skill
mkdir -p ~/.openclaw/workspace/skills/loopy-agent-registry
cp -r loopy-agent-registry/* ~/.openclaw/workspace/skills/loopy-agent-registry/

# 2. Instalar dependencias Python
pip install pyyaml requests

# 3. Configurar secrets
openclaw secrets set LOOPY_AGENT_REGISTRY_TOKEN "tu-token"
openclaw secrets set LOOPY_ORGANIZATION_ID "tu-org-uuid"

# 4. Probar
openclaw agent --message "registra mi agente en Loopy"
```

### 2. loopy-guardrails-profiler

Convierte guardrails locales a formato estándar Loopy.

**Trigger:** `"sincroniza mis guardrails con Loopy"`

### 3. loopy-agent-audit-packager

Genera reporte Markdown de auditoría sin secretos.

**Trigger:** `"genera reporte de auditoria de mi agente"`

## 📁 Estructura del Repo

```
loopy-skills/
├── README.md
├── loopy-agent-registry/
│   ├── SKILL.MD
│   └── scripts/
│       ├── __init__.py
│       ├── agent_context_reader.py      # Lee IDENTITY.md, SOUL.md
│       ├── subagent_scanner.py          # Escanee sub-agentes
│       ├── skills_scanner.py            # Lista skills
│       ├── tasks_extractor.py           # Extrae tareas
│       ├── build_descriptor.py          # Arma payload
│       ├── validate_descriptor.py       # Valida schema
│       ├── send_registry_event.py       # Envía a Loopy
│       └── heartbeat.sh
├── loopy-guardrails-profiler/
│   └── ...
└── loopy-agent-audit-packager/
    └── ...
```

## 🔒 Seguridad

- ✅ Nunca incluir tokens o secretos en prompts
- ✅ No enviar PII (emails, teléfonos, datos personales)
- ✅ Sanitizar rutas de archivos (paths relativos)
- ✅ Payload validado antes de enviar
- ✅ Idempotency determinística por hora
- ✅ Circuit breaker tras 3 fallos consecutivos
- ✅ Límite de tamaño: < 500KB por payload

## 📊 Estados en Loopy

| Estado | Descripción |
|--------|-------------|
| `online` | Heartbeat <= 5 minutos |
| `stale` | >5 y <=60 minutos |
| `offline` | >60 minutos |
| `revoked` | Revocado permanentemente |

## 🐛 Troubleshooting

| Código | Problema | Solución |
|--------|----------|----------|
| 401 | Token inválido | Revisar `LOOPY_AGENT_REGISTRY_TOKEN` |
| 422 | Credencial no configurada | Registrar en Loopy Orion |
| 400 | Payload inválido | Ejecutar `validate_descriptor.py` |
| 413 | Payload muy grande | Revisar límites (20 tareas, 10 skills) |
| 0 | Circuit breaker | Esperar 1 hora |

## 📞 Soporte

Contactar: matias@apprecio.com

## 📄 Licencia

MIT License - Ver archivo LICENSE

---

*Para Apprecio y la comunidad Loopy*