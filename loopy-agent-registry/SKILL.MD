---
name: loopy-agent-registry
version: 2.1.1
description: "Registro automático de agentes OpenClaw en Loopy Orion. Detecta sub-agentes, skills y cron jobs automáticamente. Envía heartbeat periódico con datos reales del sistema."
compatibility:
  runtimes:
    - OpenClaw 2026.2+
requirements:
  secrets:
    - LOOPY_AGENT_REGISTRY_TOKEN
    - LOOPY_ORGANIZATION_ID
    - LOOPY_USER_EMAIL
  python_packages:
    - pyyaml
    - requests
metadata:
  owner: Apprecio
  category: agent-governance
  safety_level: strict
use_cases:
  - Registrar agente principal y sub-agentes automáticamente
  - Inventario completo de agentes corporativos
  - Monitoreo de estado (online/offline)
  - Cumplimiento y auditoría de agentes IA
guardrails:
  - Nunca incluir tokens, secretos ni credenciales en el payload
  - No incluir PII (emails, teléfonos, datos personales)
  - Sanitizar rutas de archivos (usar paths relativos)
  - Limitar payload a < 500KB
  - Circuit breaker: pausar tras 3 fallos consecutivos
---

# Loopy Agent Registry v2.1

Skill para registrar y monitorear agentes OpenClaw en **Loopy Orion**. Diseñado para equipos y organizaciones que necesitan visibilidad centralizada de sus agentes IA.

## ✨ Características

- **🤖 Detección Automática**: Escanea y registra sub-agentes sin configuración manual
- **📊 Inventario Completo**: Skills, cron jobs, métricas y estado del sistema
- **🔄 Heartbeat**: Señal de vida automática para monitoreo de disponibilidad
- **🔒 Seguro**: No expone secretos ni datos sensibles
- **⚡ Fácil de usar**: Una sola variable de entorno para empezar

## 📋 Requisitos

```bash
# Python 3.8+
pip install pyyaml requests

# O si prefieres:
pip install -r requirements.txt
```

## 🚀 Instalación Rápida

### 1. Copiar el skill

```bash
cp -r loopy-agent-registry ~/.openclaw/workspace/skills/
```

### 2. Configurar secrets (una sola vez)

```bash
# Opción A: Variables de entorno
export LOOPY_AGENT_REGISTRY_TOKEN="tu-token-de-loopy"
export LOOPY_ORGANIZATION_ID="tu-org-id"
export LOOPY_USER_EMAIL="tu-email@empresa.com"  # Email para registro en Loopy

# Opción B: Archivo secrets (recomendado)
echo "LOOPY_AGENT_REGISTRY_TOKEN=tu-token" > ~/.openclaw/secrets
echo "LOOPY_ORGANIZATION_ID=tu-org-id" >> ~/.openclaw/secrets
echo "LOOPY_USER_EMAIL=tu-email@empresa.com" >> ~/.openclaw/secrets
chmod 600 ~/.openclaw/secrets
```

### 3. Probar

```bash
# Ver qué detecta (sin enviar)
cd ~/.openclaw/workspace/skills/loopy-agent-registry
python3 scripts/heartbeat.py --dry-run

# Enviar heartbeat real
python3 scripts/heartbeat.py
```

## 📖 Uso

### Heartbeat Manual

```bash
# Enviar heartbeat ahora
openclaw agent --message "enviar heartbeat a Loopy"

# O directamente:
python3 ~/.openclaw/workspace/skills/loopy-agent-registry/scripts/heartbeat.py
```

### Ver qué detecta el sistema

```bash
python3 scripts/heartbeat.py --dry-run --verbose
```

Esto muestra:
- Sub-agentes encontrados
- Skills instaladas
- Cron jobs configurados
- Métricas del sistema

### Automatizar con Cron

Agregar a OpenClaw cron para heartbeat diario:

```bash
openclaw cron add \
  --name "loopy-heartbeat" \
  --schedule "0 6 * * *" \
  --command "python3 ~/.openclaw/workspace/skills/loopy-agent-registry/scripts/heartbeat.py" \
  --tz "America/Santiago"
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Requerida | Descripción | Default |
|----------|-----------|-------------|---------|
| `LOOPY_AGENT_REGISTRY_TOKEN` | ✅ | Token de autenticación en Loopy | - |
| `LOOPY_ORGANIZATION_ID` | ✅ | ID de tu organización en Loopy | - |
| `LOOPY_USER_EMAIL` | ✅ | Email del propietario del agente (para registro en Loopy) | - |
| `LOOPY_AGENT_ID` | ❌ | ID único de este agente | `hostname-main` |
| `LOOPY_AGENT_NAME` | ❌ | Nombre descriptivo | `Agente` |
| `LOOPY_LOG_FILE` | ❌ | Ruta del archivo de log | `~/.openclaw/workspace/logs/loopy-heartbeat.log` |

### Configuración por Archivo

Crear `~/.openclaw/workspace/skills/loopy-agent-registry/config.yaml`:

```yaml
# Configuración del agente principal
agent:
  id: "mi-agente-unico"
  name: "Mi Agente"
  description: "Agente especializado para..."

# Sub-agentes adicionales (opcional)
# Normalmente se detectan automáticamente
sub_agents:
  - id: "agente-personalizado"
    name: "Agente Personalizado"
    description: "Creado manualmente"
    status: "online"

# Webhook (normalmente no necesario cambiar)
webhook_url: "https://tu-endpoint.com/webhook"
```

## 📊 Qué se envía a Loopy

### Agente Principal
- ID único
- Nombre y emoji
- Estado (online/offline)
- Timestamp

### Sub-Agentes (Detectados Automáticamente)
El skill escanea `~/.openclaw/agents/` y registra:
- Nombre y descripción
- Modelo utilizado
- Estado (active/disabled)
- Workspace asociado

**Ejemplo:** Si creas un agente llamado "FinExpertAI", aparecerá automáticamente en el próximo heartbeat.

### Skills (Detectadas Automáticamente)
Escanea `~/.openclaw/workspace/skills/` y registra:
- Nombre de la skill
- Categoría (google-workspace, automation, etc.)
- Versión (si está disponible)

### Cron Jobs
Lista los jobs configurados en OpenClaw:
- Nombre
- Schedule (expresión cron)
- Estado (active/disabled)

### Métricas del Sistema
- Archivos de memoria
- Total de skills
- Timestamp de actualización

## 🐛 Troubleshooting

### "LOOPY_AGENT_REGISTRY_TOKEN no configurado"

```bash
# Verificar que esté configurado
echo $LOOPY_AGENT_REGISTRY_TOKEN

# Configurar:
export LOOPY_AGENT_REGISTRY_TOKEN="tu-token"
```

### No detecta mis sub-agentes

Verificar estructura:
```
~/.openclaw/agents/
├── mi-agente-1/
│   ├── agent/
│   │   └── agent.yaml
│   └── SOUL.md
└── mi-agente-2/
    └── ...
```

El agente debe tener al menos `agent/agent.yaml` o `SOUL.md`.

### Error 401 (Unauthorized)

- Token inválido o expirado
- Verificar en Loopy Orion que el token esté activo

### Error 422 (Unprocessable)

- Credencial no configurada en Loopy
- Contactar admin de Loopy para registrar el agente

### Payload muy grande

El skill limita automáticamente:
- Máximo 10 sub-agentes
- Máximo 10 skills
- Máximo 10 cron jobs

Si necesitas más, modifica las constantes en `heartbeat.py`.

## 📁 Estructura del Skill

```
loopy-agent-registry/
├── SKILL.MD                    # Esta documentación
├── register_agent.py           # Registro completo (ejecución única)
├── requirements.txt            # Dependencias Python
└── scripts/
    ├── heartbeat.py           # ⭐ Heartbeat automático
    ├── heartbeat.sh           # Wrapper bash
    ├── subagent_scanner.py    # Detecta sub-agentes
    ├── skills_scanner.py      # Detecta skills
    └── common.py              # Utilidades
```

## 🔄 Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│  OpenClaw                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ IDENTITY.md │  │ Sub-agentes │  │ Skills instaladas   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         └─────────────────┼────────────────────┘            │
│                           ▼                                 │
│              ┌─────────────────────────┐                   │
│              │   heartbeat.py          │                   │
│              │   - Lee contexto        │                   │
│              │   - Escanea agentes     │                   │
│              │   - Arma payload        │                   │
│              └───────────┬─────────────┘                   │
│                          │ POST                            │
└──────────────────────────┼─────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Loopy Orion                                                │
│  - Registra agente                                          │
│  - Actualiza inventario                                     │
│  - Monitorea disponibilidad                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📈 Estados en Loopy Orion

| Estado | Significado | Timeout |
|--------|-------------|---------|
| 🟢 online | Heartbeat reciente | ≤ 5 min |
| 🟡 stale | Heartbeat atrasado | 5-60 min |
| 🔴 offline | Sin heartbeat | > 60 min |
| ⚫ revoked | Revocado manualmente | - |

## 🏢 Uso en Organizaciones

### Para Administradores

1. **Crear token de organización** en Loopy Orion
2. **Distribuir configuración** a los equipos:
   ```bash
   # Archivo de configuración compartido
   export LOOPY_ORGANIZATION_ID="org-apprecio"
   export LOOPY_AGENT_REGISTRY_TOKEN="tkn-xxxxx"
   ```
3. **Monitorear dashboard** de Loopy para ver todos los agentes

### Para Usuarios Finales

Simplemente instalar el skill y ejecutar:
```bash
python3 scripts/heartbeat.py --dry-run  # Verificar
python3 scripts/heartbeat.py            # Enviar
```

El sistema detectará automáticamente sus agentes y skills.

## 📝 Changelog

### v2.1.1 (2026-03-11)
- ✨ **Campo `email` agregado al payload**: Usado por Loopy para vincular agentes con usuarios
- ✨ Nueva variable de entorno `LOOPY_USER_EMAIL` (requerida)
- 📝 Documentación actualizada con instrucciones de email

### v2.1.0 (2026-03-11)
- ✨ **Heartbeat automatizado**: `heartbeat.py` detecta todo automáticamente
- ✨ **Documentación completa** para uso organizacional
- ✨ **Dry-run mode**: Verificar sin enviar
- ✨ **Logging mejorado** con timestamps
- 🐛 **Fix**: Script bash ahora es wrapper de Python

### v2.0.0 (2026-03-09)
- ✨ Lectura de IDENTITY.md, SOUL.md
- ✨ Soporte para sub-agentes
- ✨ Lista automática de skills
- ✨ Extracción de tareas

### v1.0.0
- Registro básico de agentes

## 🤝 Soporte

- **Issues**: Crear ticket en el repositorio
- **Email**: matias@apprecio.com
- **Documentación Loopy**: https://docs.loopy.orion

---

**Nota de Seguridad**: Este skill nunca envía contraseñas, tokens, ni contenido de archivos del usuario. Solo envía metadatos (nombres, descripciones, conteos) necesarios para el inventario de agentes.
