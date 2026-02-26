# Loopy Agent Registry Contract

Endpoint receptor (Edge Function):
- POST https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook

Headers:
- Authorization: Bearer TOKEN
- Content-Type: application/json

Payload aceptado:

- idempotency_key: string (sha256(agent_id + event_type + YYYY-MM-DDTHH:00))
- organization_id: UUID
- event_type: agent.registered | agent.updated | agent.heartbeat | agent.revoked
- agent: object

Eventos:
- agent.registered: crea agente. Si agent_id ya existe: 208
- agent.updated: actualiza campos. Cambios sensibles quedan pendientes de aprobacion: risk_level, tools, data_access, guardrails
- agent.heartbeat: actualiza last_seen_at y status online. Payload minimo: agent.agent_id
- agent.revoked: revoca permanentemente

Estados calculados por Loopy:
- online: last_seen_at <= 5 min
- stale: > 5 min y <= 60 min
- offline: > 60 min
- revoked: fijo