#!/bin/bash
# Loopy Heartbeat Script para Matias
# Location: /root/.openclaw/workspace/skills/loopy-agent-registry/scripts/heartbeat.sh

# Cargar secrets desde archivo
if [ -f /root/.openclaw/secrets ]; then
    export $(grep -v '^#' /root/.openclaw/secrets | xargs)
fi

export LOOPY_WEBHOOK_URL="https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook"

# Generar idempotency_key (sha256 de agent_id + event_type + hora actual)
IDEM_KEY=$(echo -n "matias-apprecio-mainheartbeat$(date -u +%Y-%m-%dT%H:00)" | sha256sum | cut -d' ' -f1)

# Enviar heartbeat
curl -s -X POST "$LOOPY_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $LOOPY_AGENT_REGISTRY_TOKEN" \
  -d '{
    "event_type": "agent.heartbeat",
    "idempotency_key": "'$IDEM_KEY'",
    "organization_id": "'$LOOPY_ORGANIZATION_ID'",
    "agent": {
      "agent_id": "matias-apprecio-main",
      "name": "Matias",
      "status": "online",
      "sub_agents": [
        {"agent_id": "finexpertai", "name": "FinExpertAI", "status": "online"}
      ]
    },
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }' > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] Heartbeat enviado OK" >> /root/.openclaw/workspace/logs/loopy-heartbeat.log
else
    echo "[$(date)] ERROR: Heartbeat falló" >> /root/.openclaw/workspace/logs/loopy-heartbeat.log
fi
