# Loopy Skills for OpenClaw

Este repositorio contiene los Skills oficiales de Loopy para integrar agentes corporativos con Orion (Agent Registry).

Objetivo: que cualquier agente de OpenClaw pueda registrarse, reportar su estado y mantenerse gobernado dentro de Loopy.

---

## Skills incluidos

### 1. loopy-agent-registry (Core)

Función:
- Registrar agente en Loopy
- Actualizar ficha del agente
- Enviar heartbeat

Triggers típicos:
- "registra mi agente en Loopy"
- "actualiza mi registro en Orion"
- "envia heartbeat"

Requiere:
- LOOPY_AGENT_REGISTRY_TOKEN (Secret)
- LOOPY_ORGANIZATION_ID (Secret)
- LOOPY_WEBHOOK_URL (Environment)

---

### 2. loopy-guardrails-profiler

Función:
- Convertir guardrails locales a formato estándar Loopy

Trigger típico:
- "sincroniza mis guardrails con Loopy"

---

### 3. loopy-agent-audit-packager

Función:
- Generar reporte Markdown de auditoría sin secretos

Trigger típico:
- "genera reporte de auditoria de mi agente"

---

## Instalación en OpenClaw

1. Instalar el Skill desde este repositorio.
2. Configurar los siguientes Secrets:

- LOOPY_AGENT_REGISTRY_TOKEN
- LOOPY_ORGANIZATION_ID

3. (Opcional) Configurar:
- LOOPY_WEBHOOK_URL  
  Default:  
  https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook

4. Probar con:
- "envia heartbeat"

Si devuelve 200 o 208, quedó correctamente instalado.

---

## Seguridad

- Nunca incluir tokens o secretos en prompts.
- No enviar PII (emails, teléfonos, datos personales).
- El Skill usa idempotency determinística por hora.
- Circuit breaker tras 3 fallos consecutivos.

---

## Estados en Loopy

- online: heartbeat <= 5 minutos
- stale: >5 y <=60 minutos
- offline: >60 minutos
- revoked: revocado permanentemente

---

## Soporte

Si el registro falla:

- 401 → token inválido
- 422 → credencial no configurada en Loopy
- 400 → payload inválido
- Circuit breaker → revisar configuración

Contactar equipo Loopy.
