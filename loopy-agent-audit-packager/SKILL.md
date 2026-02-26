---
name: loopy-agent-audit-packager
version: 1.0.0
description: Genera un reporte de auditoria en Markdown para compliance del agente, sin secretos. Usar cuando el usuario pida exportar ficha del agente o reporte de auditoria.
compatibility:
  runtimes:
    - OpenClaw
requirements:
  environment:
    - AGENT_DESCRIPTOR_SOURCE
metadata:
  owner: Loopy Team
  category: agent-governance
  safety_level: strict
use_cases:
  - Generar evidence bundle sin secretos
  - Exportar ficha del agente para revision
guardrails:
  - Nunca incluir tokens, secretos ni headers.
  - No incluir PII ni contenido de conversaciones.
  - Solo metadata: identidad, tools, guardrails, data_access, dependencias y timeline resumido.
---

## Triggers

Activar con frases como:
- "genera reporte de auditoria de mi agente"
- "exporta mi ficha de agente"
- "prepara evidence bundle para compliance"

## Output

Markdown listo para pegar en ticket o sistema de compliance.