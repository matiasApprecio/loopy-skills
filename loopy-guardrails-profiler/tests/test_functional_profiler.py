{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from loopy_guardrails_profiler.scripts.guardrails_profiler import profile_guardrails\
\
\
def test_profiles_guardrails_to_loopy_format():\
    local = [\
        \{"id": "NO_PII", "description": "No incluir PII", "policy_id": "GR-001"\},\
        \{"name": "Require Approval", "summary": "Cambios sensibles requieren aprobacion"\},\
    ]\
    out = profile_guardrails(local)\
    assert isinstance(out, list)\
    assert out[0]["guardrail_key"] == "no_pii"\
    assert out[0]["policy_id"] == "GR-001"\
    assert "summary" in out[1]}