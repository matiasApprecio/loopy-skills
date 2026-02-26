from loopy_guardrails_profiler.scripts.guardrails_profiler import profile_guardrails


def test_profiles_guardrails_to_loopy_format():
    local = [
        {"id": "NO_PII", "description": "No incluir PII", "policy_id": "GR-001"},
        {"name": "Require Approval", "summary": "Cambios sensibles requieren aprobacion"},
    ]
    out = profile_guardrails(local)
    assert isinstance(out, list)
    assert out[0]["guardrail_key"] == "no_pii"
    assert out[0]["policy_id"] == "GR-001"
    assert "summary" in out[1]