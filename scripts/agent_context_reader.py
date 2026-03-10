"""
agent_context_reader.py

Lee los archivos de contexto del agente OpenClaw:
- IDENTITY.md (nombre, emoji, avatar)
- SOUL.md (descripción, roles, personalidad)
- AGENTS.md (info del agente)
- MEMORY.md (última actualización, stats)

Retorna un dict con la información estructurada.
"""

import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_workspace_path() -> Path:
    """Obtiene la ruta del workspace de OpenClaw."""
    # Intentar desde variable de entorno
    if os.getenv('OPENCLAW_WORKSPACE'):
        return Path(os.getenv('OPENCLAW_WORKSPACE'))
    
    # Default
    return Path.home() / '.openclaw' / 'workspace'


def read_file_safely(filepath: Path) -> str:
    """Lee un archivo de forma segura."""
    try:
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
    except Exception:
        pass
    return ""


def extract_yaml_value(content: str, key: str) -> str:
    """Extrae un valor de contenido YAML-like."""
    pattern = rf'^{key}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def parse_identity_md(content: str) -> Dict[str, str]:
    """Parsea IDENTITY.md."""
    data = {
        'name': '',
        'creature': '',
        'vibe': '',
        'emoji': '🤖',
        'avatar': ''
    }
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('- **Name:**'):
            data['name'] = line.replace('- **Name:**', '').strip()
        elif line.startswith('- **Creature:**'):
            data['creature'] = line.replace('- **Creature:**', '').strip()
        elif line.startswith('- **Vibe:**'):
            data['vibe'] = line.replace('- **Vibe:**', '').strip()
        elif line.startswith('- **Emoji:**'):
            data['emoji'] = line.replace('- **Emoji:**', '').strip()
        elif line.startswith('- **Avatar:**'):
            data['avatar'] = line.replace('- **Avatar:**', '').strip()
    
    return data


def parse_soul_md(content: str) -> Dict[str, Any]:
    """Parsea SOUL.md para extraer descripción y roles."""
    data = {
        'description': '',
        'roles': []
    }
    
    # Limpiar líneas y buscar descripción real
    lines = content.split('\n')
    description_lines = []
    
    for line in lines:
        line = line.strip()
        # Saltar líneas vacías, headers markdown (# ##), y el nombre del archivo
        if not line or line.startswith('#') or line.startswith('---'):
            continue
        # Saltar líneas de metadata tipo "- **Name:**"
        if line.startswith('- **') or line.startswith('*'):
            continue
        # Acumular líneas de descripción
        if len(line) > 10:  # Solo líneas con contenido sustancial
            description_lines.append(line)
            if len(description_lines) >= 2:  # Tomar primeras 2 líneas de contenido
                break
    
    if description_lines:
        data['description'] = ' '.join(description_lines)[:250]
    else:
        # Fallback: buscar sección "Who You Are" o "Who I Am"
        match = re.search(r'##?\s*(?:Who You Are|Who I Am|Descripción|About)[^#]*\n+([^#\n]+)', content, re.IGNORECASE)
        if match:
            data['description'] = match.group(1).strip()[:250]
        else:
            data['description'] = 'Agente de OpenClaw especializado en automatización'
    
    # Buscar roles mencionados en secciones ##
    section_matches = re.findall(r'##\s*([^#\n]+)', content)
    for section in section_matches:
        section_clean = section.strip()
        if section_clean and len(section_clean) < 50:
            # Excluir secciones comunes que no son roles
            if section_clean.lower() not in ['rules', 'reglas', 'voice', 'voz', 'tools', 'work mode', 'growth']:
                data['roles'].append({
                    'role_key': section_clean.lower().replace(' ', '_').replace('-', '_'),
                    'role_name': section_clean
                })
    
    # Si no encontró roles, agregar uno default basado en el creature
    if not data['roles']:
        data['roles'].append({
            'role_key': 'meta_agent',
            'role_name': 'Meta-Agente'
        })
    
    return data


def parse_agents_md(content: str) -> Dict[str, Any]:
    """Parsea AGENTS.md para información del agente."""
    data = {
        'workspace': '',
        'notes': ''
    }
    
    # Extraer workspace path
    match = re.search(r'Workspace:\s*[`\']?([^\n`\']+)', content, re.IGNORECASE)
    if match:
        data['workspace'] = match.group(1).strip()
    
    return data


def get_memory_stats(workspace_path: Path) -> Dict[str, Any]:
    """Obtiene estadísticas de memory/."""
    memory_path = workspace_path / 'memory'
    
    stats = {
        'last_updated': '',
        'daily_notes_count': 0,
        'total_entries': 0
    }
    
    try:
        if memory_path.exists():
            files = list(memory_path.glob('*.md'))
            stats['total_entries'] = len(files)
            
            # Contar archivos del mes actual
            current_month = datetime.now().strftime('%Y-%m')
            month_files = [f for f in files if current_month in f.name]
            stats['daily_notes_count'] = len(month_files)
            
            # Última actualización
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                stats['last_updated'] = mtime.isoformat()
    except Exception:
        pass
    
    return stats


def get_openclaw_version() -> str:
    """Obtiene la versión de OpenClaw instalada."""
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parsear versión de output
            match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
            if match:
                return match.group(1)
    except Exception:
        pass
    return "2026.2.13"


def get_agent_uuid(workspace_path: Path) -> str:
    """Obtiene o genera un UUID estable para el agente."""
    uuid_file = workspace_path / '.agent_uuid'
    
    try:
        if uuid_file.exists():
            return uuid_file.read_text().strip()
    except Exception:
        pass
    
    # Generar nuevo UUID
    new_uuid = str(uuid.uuid4())
    try:
        uuid_file.write_text(new_uuid)
    except Exception:
        pass
    
    return new_uuid


def get_agent_context() -> Dict[str, Any]:
    """
    Función principal: Lee todo el contexto del agente OpenClaw.
    
    Retorna un dict con toda la información estructurada.
    """
    workspace_path = get_workspace_path()
    
    # Leer archivos
    identity_content = read_file_safely(workspace_path / 'IDENTITY.md')
    soul_content = read_file_safely(workspace_path / 'SOUL.md')
    agents_content = read_file_safely(workspace_path / 'AGENTS.md')
    memory_content = read_file_safely(workspace_path / 'MEMORY.md')
    
    # Parsear cada archivo
    identity = parse_identity_md(identity_content)
    soul = parse_soul_md(soul_content)
    agents_info = parse_agents_md(agents_content)
    memory_stats = get_memory_stats(workspace_path)
    
    # Construir respuesta
    context = {
        'agent_id': get_agent_uuid(workspace_path),
        'name': identity.get('name') or 'Agent',
        'creature': identity.get('creature') or 'AI Assistant',
        'emoji': identity.get('emoji') or '🤖',
        'avatar': identity.get('avatar') or '',
        'description': soul.get('description') or 'Agente de OpenClaw',
        'runtime_type': f"OpenClaw v{get_openclaw_version()}",
        'current_version': '1.0.0',
        'risk_level': 'medium',
        'risk_rationale': 'Acceso a servicios corporativos y datos de usuario',
        'roles': soul.get('roles', []),
        'workspace': str(workspace_path),
        'memory_summary': memory_stats
    }
    
    return context


if __name__ == '__main__':
    # Test
    ctx = get_agent_context()
    import json
    print(json.dumps(ctx, indent=2, ensure_ascii=False))