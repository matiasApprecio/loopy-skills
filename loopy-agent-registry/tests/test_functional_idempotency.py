from loopy_agent_registry.scripts.common import idempotency_key


def test_idempotency_key_deterministic():
    agent_id = "22222222-2222-2222-2222-222222222222"
    ev = "agent.updated"
    bucket = "2026-02-23T10:00"
    k1 = idempotency_key(agent_id, ev, bucket)
    k2 = idempotency_key(agent_id, ev, bucket)
    assert k1 == k2
    assert len(k1) == 64