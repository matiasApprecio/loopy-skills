---
name: loopy-agent-registry
version: 2.1.1
description: "Registra agentes OpenClaw en Loopy Orion. Envía heartbeat con datos del agente, sub-agentes, skills y cron jobs."
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
---

# Loopy Agent Registry v2.1.1

Skill para registrar agentes OpenClaw en **Loopy Orion**.

## Requisitos

```bash
pip install pyyaml requests
```

## Instalación

```bash
cp -r loopy-agent-registry ~/.openclaw/workspace/skills/
```

## Configuración

Crear `~/.openclaw/secrets`:

```bash
LOOPY_AGENT_REGISTRY_TOKEN=tu-token
LOOPY_ORGANIZATION_ID=tu-org-id
LOOPY_USER_EMAIL=tu-email@empresa.com
```

## Uso

### Registrar agente (una vez)

```bash
cd ~/.openclaw/workspace/skills/loopy-agent-registry
export $(grep -v '^#' ~/.openclaw/secrets | xargs)
python3 register_agent.py
```

### Heartbeat (automático)

```bash
python3 scripts/heartbeat.py
```

## Estructura

```
loopy-agent-registry/
├── SKILL.MD              # Este archivo
├── register_agent.py     # Registro inicial del agente
├── requirements.txt      # Dependencias
└── scripts/
    ├── heartbeat.py      # Heartbeat automático
    ├── heartbeat.sh      # Wrapper bash
    ├── subagent_scanner.py
    ├── skills_scanner.py
    ├── tasks_extractor.py
    ├── agent_context_reader.py
    ├── build_descriptor.py
    ├── validate_descriptor.py
    ├── send_registry_event.py
    └── common.py
```

## Changelog

### v2.1.1
- Agrega campo `email` al payload para registro en Loopy
- Nueva variable `LOOPY_USER_EMAIL` requerida

### v2.1.0
- Heartbeat automatizado con detección de sub-agentes

### v2.0.0
- Registro completo con datos de IDENTITY.md, SOUL.md

## Soporte

matias@apprecio.com
