{\rtf1\ansi\ansicpg1252\cocoartf2821
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from loopy_agent_registry.scripts.common import idempotency_key\
\
\
def test_idempotency_key_deterministic():\
    agent_id = "22222222-2222-2222-2222-222222222222"\
    ev = "agent.updated"\
    bucket = "2026-02-23T10:00"\
    k1 = idempotency_key(agent_id, ev, bucket)\
    k2 = idempotency_key(agent_id, ev, bucket)\
    assert k1 == k2\
    assert len(k1) == 64}