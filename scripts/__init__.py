"""
Loopy Agent Registry - Scripts Package

Módulos para registrar agentes OpenClaw en Loopy Orion.
"""

from .agent_context_reader import get_agent_context
from .subagent_scanner import get_all_subagents, get_subagent_tasks
from .skills_scanner import get_all_skills
from .tasks_extractor import get_all_tasks, get_tasks_summary
from .build_descriptor import build_payload, build_minimal_payload

__all__ = [
    'get_agent_context',
    'get_all_subagents',
    'get_subagent_tasks',
    'get_all_skills',
    'get_all_tasks',
    'get_tasks_summary',
    'build_payload',
    'build_minimal_payload',
]