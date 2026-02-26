---
name: loopy-guardrails-profiler
version: 1.0.0
description: Convierte guardrails locales del agente OpenClaw a un formato estandar para Loopy Orion. Usar cuando el usuario pida sincronizar politicas activas o reportar guardrails.
compatibility:
  runtimes:
    - OpenClaw
requirements:
  environment:
    - OPENCLAW_GUARDRAILS_SOURCE
metadata:
  owner: Loopy Team
  category: agent-governance
  safety_level: strict
use_cases:
  - Sincronizar guardrails del agente con Loopy
  - Generar lista estandar guardrails para incluir en agent.updated
guardrails:
  - No exportar secretos ni contenido sensible.
  - Resumir politicas, no copiar prompts completos.
---

## Triggers

Activar con frases como:
- "sincroniza mis guardrails con Loopy"
- "reporta mis politicas activas"
- "que guardrails tengo activos"
- "exporta mis guardrails para Orion"

## Output

Devuelve un array de objetos:
- guardrail_key
- summary
- policy_id (opcional)

Este output se puede incluir directamente en agent.guardrails dentro de agent.updated.