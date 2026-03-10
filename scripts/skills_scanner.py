"""
skills_scanner.py

Escanee y lee información de todas las skills instaladas en OpenClaw.
Ubicación típica: ~/.openclaw/workspace/skills/
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List


def get_skills_path() -> Path:
    """Obtiene la ruta de skills instaladas."""
    if os.getenv('OPENCLAW_WORKSPACE'):
        return Path(os.getenv('OPENCLAW_WORKSPACE')) / 'skills'
    return Path.home() / '.openclaw' / 'workspace' / 'skills'


def read_file_safely(filepath: Path) -> str:
    """Lee un archivo de forma segura."""
    try:
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
    except Exception:
        pass
    return ""


def parse_skill_md(content: str) -> Dict[str, Any]:
    """Parsea SKILL.md para extraer metadata."""
    data = {
        'name': '',
        'version': '1.0.0',
        'description': '',
        'category': 'general'
    }
    
    # Extraer name
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        data['name'] = name_match.group(1).strip()
    
    # Extraer version
    version_match = re.search(r'^version:\s*(.+)$', content, re.MULTILINE)
    if version_match:
        data['version'] = version_match.group(1).strip()
    
    # Extraer description
    desc_match = re.search(r'^description:\s*["\']?(.+?)["\']?$', content, re.MULTILINE)
    if desc_match:
        data['description'] = desc_match.group(1).strip()[:200]
    
    # Extraer categoría del metadata
    category_match = re.search(r'category:\s*["\']?(.+?)["\']?', content)
    if category_match:
        data['category'] = category_match.group(1).strip()
    else:
        # Inferir de la descripción
        desc_lower = data['description'].lower()
        if 'google' in desc_lower or 'gmail' in desc_lower or 'drive' in desc_lower:
            data['category'] = 'google-workspace'
        elif 'n8n' in desc_lower or 'workflow' in desc_lower:
            data['category'] = 'automation'
        elif 'loopy' in desc_lower:
            data['category'] = 'agent-governance'
        elif 'calendar' in desc_lower:
            data['category'] = 'productivity'
        else:
            data['category'] = 'general'
    
    return data


def scan_skill(skill_path: Path) -> Dict[str, Any]:
    """
    Escanea una skill y extrae su información.
    
    Busca:
    - SKILL.md o SKILL.MD
    - README.md (fallback para descripción)
    """
    skill_name = skill_path.name
    
    # Intentar leer SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        skill_md = skill_path / 'SKILL.MD'
    
    content = read_file_safely(skill_md)
    
    if content:
        data = parse_skill_md(content)
        # Si no tiene nombre, usar nombre del directorio
        if not data['name']:
            data['name'] = skill_name
    else:
        # Fallback: leer README.md
        readme = skill_path / 'README.md'
        readme_content = read_file_safely(readme)
        
        data = {
            'name': skill_name,
            'version': '1.0.0',
            'description': readme_content[:150] if readme_content else f'Skill {skill_name}',
            'category': 'general'
        }
    
    return data


def get_all_skills() -> List[Dict[str, Any]]:
    """
    Escanea y retorna información de todas las skills instaladas.
    
    Returns:
        Lista de dicts con información de cada skill.
    """
    skills_path = get_skills_path()
    skills = []
    
    try:
        if not skills_path.exists():
            return []
        
        for item in skills_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                try:
                    skill = scan_skill(item)
                    skills.append(skill)
                except Exception as e:
                    print(f"Error scanning skill {item.name}: {e}")
    
    except Exception as e:
        print(f"Error scanning skills: {e}")
    
    return skills


def get_skills_by_category() -> Dict[str, List[Dict[str, Any]]]:
    """
    Agrupa skills por categoría.
    """
    skills = get_all_skills()
    categories = {}
    
    for skill in skills:
        cat = skill.get('category', 'general')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(skill)
    
    return categories


def count_skills() -> Dict[str, int]:
    """
    Retorna conteo de skills por categoría.
    """
    by_category = get_skills_by_category()
    return {
        'total': sum(len(v) for v in by_category.values()),
        'by_category': {k: len(v) for k, v in by_category.items()}
    }


if __name__ == '__main__':
    # Test
    skills = get_all_skills()
    import json
    print(json.dumps(skills, indent=2, ensure_ascii=False))
    
    print("\n--- Por categoría ---")
    by_cat = get_skills_by_category()
    for cat, sks in by_cat.items():
        print(f"\n{cat}: {len(sks)} skills")
        for s in sks:
            print(f"  - {s['name']} (v{s['version']})")