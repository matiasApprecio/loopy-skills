"""
tasks_extractor.py

Extrae tareas y pendientes de:
- MEMORY.md (sección de Proyectos Pendientes)
- Archivos memory/YYYY-MM-DD.md
- Archivos TASKS.md en workspaces de agentes
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def get_workspace_path() -> Path:
    """Obtiene la ruta del workspace."""
    if os.getenv('OPENCLAW_WORKSPACE'):
        return Path(os.getenv('OPENCLAW_WORKSPACE'))
    return Path.home() / '.openclaw' / 'workspace'


def read_file_safely(filepath: Path) -> str:
    """Lee un archivo de forma segura."""
    try:
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
    except Exception:
        pass
    return ""


def parse_memory_tasks(content: str) -> List[Dict[str, Any]]:
    """
    Extrae tareas de la sección 'Proyectos Pendientes' en MEMORY.md.
    
    Formato esperado:
    ## Proyectos Pendientes
    - [ ] Tarea pendiente
    - [x] Tarea completada
    """
    tasks = []
    
    # Buscar sección de proyectos pendientes
    section_match = re.search(
        r'##?\s*(?:Proyectos Pendientes|TODO|Tasks|Pending)[^#]*'
        r'([^#]+)',
        content,
        re.IGNORECASE
    )
    
    if section_match:
        section_content = section_match.group(1)
        lines = section_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Buscar tareas en formato markdown checkbox
            task_match = re.match(r'^(?:\s*-\s*)?\[([ xX])\]\s*(.+)$', line)
            if task_match:
                is_done = task_match.group(1).lower() == 'x'
                title = task_match.group(2).strip()
                
                # Ignorar líneas vacías o que no son tareas
                if title and not title.startswith('#'):
                    tasks.append({
                        'task_ref': f'memory_{len(tasks)}',
                        'title': title[:150],
                        'status': 'completed' if is_done else 'pending',
                        'source': 'MEMORY.md',
                        'assigned_to': 'main'
                    })
    
    return tasks


def parse_daily_note_tasks(filepath: Path) -> List[Dict[str, Any]]:
    """
    Extrae tareas de un archivo de nota diaria.
    """
    tasks = []
    content = read_file_safely(filepath)
    
    if not content:
        return tasks
    
    lines = content.split('\n')
    date_str = filepath.stem  # YYYY-MM-DD
    
    for line in lines:
        line = line.strip()
        # Buscar TODO o tareas
        patterns = [
            r'(?:\s*-\s*)?\[([ xX])\]\s*(.+)',  # Checkbox
            r'(?:TODO|FIXME|BUG):\s*(.+)',       # Tags especiales
            r'(?:\s*-\s*)?(?:\[\d+\])?\s*(.+)'   # Lista numerada
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    is_done = match.group(1).lower() == 'x'
                    title = match.group(2).strip()
                else:
                    is_done = False
                    title = match.group(1).strip()
                
                if title and len(title) > 5:
                    tasks.append({
                        'task_ref': f'daily_{date_str}_{len(tasks)}',
                        'title': title[:150],
                        'status': 'completed' if is_done else 'pending',
                        'source': f'memory/{date_str}.md',
                        'assigned_to': 'main',
                        'date': date_str
                    })
                break
    
    return tasks


def get_recent_daily_tasks(days: int = 7) -> List[Dict[str, Any]]:
    """
    Extrae tareas de los últimos N días de notas diarias.
    """
    tasks = []
    memory_path = get_workspace_path() / 'memory'
    
    try:
        if not memory_path.exists():
            return tasks
        
        # Obtener archivos .md recientes
        md_files = list(memory_path.glob('*.md'))
        md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Tomar los más recientes
        recent_files = md_files[:days]
        
        for filepath in recent_files:
            file_tasks = parse_daily_note_tasks(filepath)
            tasks.extend(file_tasks)
    
    except Exception as e:
        print(f"Error reading daily notes: {e}")
    
    return tasks


def get_all_tasks() -> List[Dict[str, Any]]:
    """
    Obtiene todas las tareas de todas las fuentes.
    
    Returns:
        Lista de tareas con metadatos.
    """
    all_tasks = []
    
    # 1. Tareas de MEMORY.md
    memory_path = get_workspace_path() / 'MEMORY.md'
    memory_content = read_file_safely(memory_path)
    memory_tasks = parse_memory_tasks(memory_content)
    all_tasks.extend(memory_tasks)
    
    # 2. Tareas de notas diarias recientes
    daily_tasks = get_recent_daily_tasks(days=14)
    all_tasks.extend(daily_tasks)
    
    # Eliminar duplicados (mismo título)
    seen_titles = set()
    unique_tasks = []
    for task in all_tasks:
        title_normalized = task['title'].lower().strip()
        if title_normalized not in seen_titles:
            seen_titles.add(title_normalized)
            unique_tasks.append(task)
    
    return unique_tasks


def get_tasks_by_status() -> Dict[str, List[Dict[str, Any]]]:
    """
    Agrupa tareas por estado.
    """
    tasks = get_all_tasks()
    result = {
        'pending': [],
        'completed': [],
        'in_progress': []
    }
    
    for task in tasks:
        status = task.get('status', 'pending')
        if status in result:
            result[status].append(task)
        else:
            result['pending'].append(task)
    
    return result


def get_tasks_summary() -> Dict[str, Any]:
    """
    Retorna un resumen de tareas.
    """
    by_status = get_tasks_by_status()
    return {
        'total': sum(len(v) for v in by_status.values()),
        'pending': len(by_status['pending']),
        'completed': len(by_status['completed']),
        'in_progress': len(by_status.get('in_progress', [])),
        'recent': by_status['pending'][:5]  # Top 5 pendientes
    }


if __name__ == '__main__':
    # Test
    tasks = get_all_tasks()
    import json
    print(json.dumps(tasks, indent=2, ensure_ascii=False))
    
    print("\n--- Resumen ---")
    summary = get_tasks_summary()
    print(f"Total: {summary['total']}")
    print(f"Pendientes: {summary['pending']}")
    print(f"Completadas: {summary['completed']}")
    
    print("\n--- Top 5 pendientes ---")
    for t in summary['recent']:
        print(f"  - {t['title']}")