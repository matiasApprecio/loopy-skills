---
name: loopy-agent-registry
version: 1.0.0
description: Registra y actualiza un agente corporativo en Loopy Orion, y envia heartbeats de estado. Usar cuando el usuario pida registrar un agente en Loopy, actualizar su ficha en Orion o enviar heartbeat.
compatibility:
  runtimes:
    - OpenClaw
requirements:
  secrets:
    - LOOPY_AGENT_REGISTRY_TOKEN
    - LOOPY_ORGANIZATION_ID
  environment:
    - LOOPY_WEBHOOK_URL
metadata:
  owner: Loopy Team
  category: agent-governance
  safety_level: strict
use_cases:
  - Registrar mi agente en Loopy Orion
  - Actualizar roles, tareas, tools, guardrails y data_access del agente
  - Enviar heartbeat para marcar el agente como online
guardrails:
  - Nunca incluir tokens, secretos ni contenido sensible en el payload.
  - No incluir PII (nombres reales de clientes, emails, telefonos, direcciones).
  - Validar schema antes de enviar.
  - Idempotency key deterministica por hora.
  - Circuit breaker: si hay 3 fallos consecutivos, pausar envios y alertar.
---

## Cuándo usar este Skill

Activar cuando el usuario diga cosas como:
- "registra mi agente en Loopy"
- "registra mi agente en Orion"
- "actualiza mi registro en Orion"
- "actualiza mi ficha en Loopy"
- "envia heartbeat"
- "manda heartbeat a Loopy"

No activar para:
- tareas generales sin intencion de registro
- consultas sobre Loopy sin pedir registrar o actualizar

## Workflow

1. Construir descriptor:
   - scripts/build_descriptor.py obtiene metadata del agente desde el contexto OpenClaw y genera el payload JSON de Loopy.

2. Validar:
   - scripts/validate_descriptor.py valida el payload contra el schema aceptado por Loopy.
   - Reglas: risk_level=high requiere risk_rationale.

3. Enviar evento:
   - scripts/send_registry_event.py hace HTTP POST al Edge Function agent-registry-webhook.
   - Retries: 3 intentos con backoff exponencial.
   - Idempotency: sha256(agent_id + event_type + YYYY-MM-DDTHH:00)
   - Circuit breaker: 3 fallos consecutivos pausan envios.

## Configuracion

Variables requeridas:
- LOOPY_WEBHOOK_URL (default recomendado: https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook)
- LOOPY_AGENT_REGISTRY_TOKEN (secret manager)
- LOOPY_ORGANIZATION_ID (UUID, secret manager o config segura)

## Ejemplos de uso

- Registrar agente:
  - event_type: agent.registered
  - payload incluye toda la ficha agent

- Actualizar agente:
  - event_type: agent.updated
  - payload incluye agent completo actualizado

- Heartbeat:
  - event_type: agent.heartbeat
  - payload minimo: agent.agent_id (otros campos opcionales)

## Troubleshooting

- 401: token ausente o invalido. Revisar secret LOOPY_AGENT_REGISTRY_TOKEN.
- 422: credencial no configurada en Loopy. Registrar credencial agent_registry y asignar organization_id.
- 400: payload invalido. Ejecutar validate_descriptor.py para ver detalles.
- 208: ya procesado. Idempotency key duplicado; no es error.