"""
subagent_scanner.py

Escanee y lee información de todos los sub-agentes en OpenClaw.
Ubicación típica: ~/.openclaw/agents/
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def get_agents_path() -> Path:
    """Obtiene la ruta base de agentes."""
    if os.getenv('OPENCLAW_HOME'):
        return Path(os.getenv('OPENCLAW_HOME')) / 'agents'
    return Path.home() / '.openclaw' / 'agents'


def read_yaml_safely(filepath: Path) -> Dict[str, Any]:
    """Lee un archivo YAML de forma segura."""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def read_file_safely(filepath: Path) -> str:
    """Lee un archivo de texto de forma segura."""
    try:
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
    except Exception:
        pass
    return ""


def parse_soul_md_simple(content: str) -> str:
    """Extrae una descripción simple de SOUL.md."""
    lines = content.split('\n')
    for line in lines[:10]:  # Primeras 10 líneas
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('-'):
            return line[:150]
    return "Agente especializado"


def scan_subagent(agent_path: Path) -> Optional[Dict[str, Any]]:
    """
    Escanea un sub-agente y extrae su información.
    
    Estructura esperada:
    ~/.openclaw/agents/{agent_name}/
      ├── agent/
      │   └── agent.yaml
      ├── SOUL.md
      └── workspace/
    """
    agent_name = agent_path.name
    
    # Ignorar el agente principal 'main'
    if agent_name == 'main':
        return None
    
    # Leer agent.yaml
    agent_yaml_path = agent_path / 'agent' / 'agent.yaml'
    agent_config = read_yaml_safely(agent_yaml_path)
    
    # Leer SOUL.md
    soul_path = agent_path / 'SOUL.md'
    soul_content = read_file_safely(soul_path)
    description = parse_soul_md_simple(soul_content) if soul_content else ""
    
    # Si no hay descripción, usar la del YAML
    if not description:
        description = agent_config.get('description', f'Agente {agent_name}')
    
    # Determinar estado (simple heurística)
    status = 'configured'  # Default
    if agent_config.get('disabled'):
        status = 'disabled'
    
    subagent = {
        'agent_id': agent_name,
        'name': agent_config.get('name', agent_name),
        'description': description[:200],
        'model': agent_config.get('model', 'unknown'),
        'status': status,
        'workspace': str(agent_path / 'workspace')
    }
    
    return subagent


def get_all_subagents() -> List[Dict[str, Any]]:
    """
    Escanea y retorna información de todos los sub-agentes.
    
    Returns:
        Lista de dicts con información de cada sub-agente.
    """
    agents_path = get_agents_path()
    subagents = []
    
    try:
        if not agents_path.exists():
            return []
        
        # Listar directorios en agents/
        for item in agents_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                subagent = scan_subagent(item)
                if subagent:
                    subagents.append(subagent)
    
    except Exception as e:
        print(f"Error scanning subagents: {e}")
    
    return subagents


def get_subagent_tasks(subagent_name: str) -> List[Dict[str, Any]]:
    """
    Extrae tareas asociadas a un sub-agente específico.
    Busca en el workspace del sub-agente.
    """
    tasks = []
    
    try:
        agent_path = get_agents_path() / subagent_name
        tasks_file = agent_path / 'workspace' / 'TASKS.md'
        
        if tasks_file.exists():
            content = tasks_file.read_text(encoding='utf-8')
            # Parse simple de tareas
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- [ ]') or line.startswith('- [x]'):
                    status = 'completed' if '[x]' in line else 'pending'
                    title = line.replace('- [ ]', '').replace('- [x]', '').strip()
                    tasks.append({
                        'task_ref': f'{subagent_name}_{len(tasks)}',
                        'title': title[:100],
                        'status': status,
                        'assigned_to': subagent_name
                    })
    except Exception:
        pass
    
    return tasks


if __name__ == '__main__':
    # Test
    subagents = get_all_subagents()
    import json
    print(json.dumps(subagents, indent=2, ensure_ascii=False))
    
    print("\n--- Tareas por sub-agente ---")
    for sa in subagents:
        tasks = get_subagent_tasks(sa['agent_id'])
        if tasks:
            print(f"\n{sa['name']}:")
            for t in tasks:
                print(f"  - {t['title']} ({t['status']})")