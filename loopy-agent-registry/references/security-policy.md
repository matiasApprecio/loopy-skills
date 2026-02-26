# Security Policy - loopy-agent-registry

Objetivo: reportar metadata de agentes sin exponer informacion sensible.

No permitido en payload:
- Tokens, API keys, secretos, cookies, headers de auth
- Prompt completo, conversaciones completas, logs con contenido de usuarios
- PII: emails, telefonos, direcciones, nombres de clientes, identificadores personales directos

Permitido:
- Identificadores tecnicos (agent_id UUID)
- Resumenes de guardrails y policy_id
- Scopes declarativos de herramientas (texto general)
- Clasificacion de acceso a datos (public/internal/confidential/restricted) y scope general

Controles:
- Validacion previa al envio
- Heuristicas anti-PII en campos de texto
- Secret manager para LOOPY_AGENT_REGISTRY_TOKEN
- Circuit breaker: pausar despues de 3 fallos consecutivos