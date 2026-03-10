#!/usr/bin/env python3
"""
heartbeat.py - Envío automático de heartbeat a Loopy Orion
Lee sub-agentes dinámicamente desde el filesystem.

Uso:
  python3 heartbeat.py              # Enviar heartbeat
  python3 heartbeat.py --dry-run    # Solo mostrar payload sin enviar
  python3 heartbeat.py --config /path/to/config.yaml  # Usar config personalizada
"""

import os
import sys
import json
import hashlib
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Agregar path para imports desde el directorio scripts
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from subagent_scanner import get_all_subagents
from skills_scanner import get_all_skills


# ============================================
# CONFIGURACIÓN
# ============================================

def get_config() -> Dict[str, Any]:
    """Obtiene configuración desde variables de entorno."""
    return {
        'webhook_url': os.getenv('LOOPY_WEBHOOK_URL', 
            'https://efsyebiumgieglwvxiss.supabase.co/functions/v1/agent-registry-webhook'),
        'org_id': os.getenv('LOOPY_ORGANIZATION_ID', ''),
        'token': os.getenv('LOOPY_AGENT_REGISTRY_TOKEN', ''),
        'agent_id': os.getenv('LOOPY_AGENT_ID', 'matias-apprecio-main'),
        'agent_name': os.getenv('LOOPY_AGENT_NAME', 'Matias'),
        'user_email': os.getenv('LOOPY_USER_EMAIL', ''),
        'log_file': os.getenv('LOOPY_LOG_FILE', 
            '/root/.openclaw/workspace/logs/loopy-heartbeat.log')
    }


# ============================================
# LECTURA DE CONTEXTO
# ============================================

def get_openclaw_root() -> Path:
    """Obtiene la ruta raíz de OpenClaw."""
    if os.getenv('OPENCLAW_HOME
        return Path(os.getenv('OPENCLAW_HOME'))
    return Path.home() / '.openclaw'


def read_identity_md() -> Dict[str, str]:
    """Lee IDENTITY.md del workspace (soporta formato multilinea con markdown)."""
    identity_path = get_openclaw_root() / 'workspace' / 'IDENTITY.md'
    result = {'name': 'Agente', 'emoji': '🤖'}
    
    try:
        if identity_path.exists():
            content = identity_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].rstrip()
                # Name: el valor está siempre en la siguiente línea
                if line.startswith('- **Name:**') or line.startswith('- **Name**'):
                    # Buscar valor en líneas siguientes
                    j = i + 1
                    while j < len(lines):
                        val = lines[j].strip()
                        if val:  # Primera línea no vacía
                            result['name'] = val
                            break
                        j += 1
                    i = j  # Saltar hasta donde encontramos el valor
                # Emoji: el valor está siempre en la siguiente línea
                elif line.startswith('- **Emoji:**') or line.startswith('- **Emoji**'):
                    j = i + 1
                    while j < len(lines):
                        val = lines[j].strip()
                        if val:
                            result['emoji'] = val
                            break
                        j += 1
                    i = j
                i += 1
    except Exception:
        pass
    
    return result


def get_cron_jobs() -> List[Dict[str, str]]:
    """Obtiene lista de cron jobs activos usando 'openclaw cron list'."""
    jobs = []
    try:
        result = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for job in data.get('jobs', []):
                jobs.append({
                    'name': job.get('name', 'unknown'),
                    'schedule': job.get('schedule', {}).get('expr', ''),
                    'status': 'active' if job.get('enabled') else 'disabled'
                })
    except Exception as e:
        print(f"  ⚠️  No se pudieron leer cron jobs: {e}")
    
    return jobs[:10]  # Limitar a 10


def get_system_metrics() -> Dict[str, Any]:
    """Obtiene métricas básicas del sistema."""
    workspace = get_openclaw_root() / 'workspace'
    
    metrics = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'memory_files': 0,
        'skills_count': 0
    }
    
    try:
        # Contar archivos de memoria
        memory_dir = workspace / 'memory'
        if memory_dir.exists():
            metrics['memory_files'] = len(list(memory_dir.glob('*.md')))
        
        # Contar skills
        skills_dir = workspace / 'skills'
        if skills_dir.exists():
            metrics['skills_count'] = len([d for d in skills_dir.iterdir() if d.is_dir()])
    except Exception:
        pass
    
    return metrics


# ============================================
# CONSTRUCCIÓN DE PAYLOAD
# ============================================

def build_heartbeat_payload(config: Dict[str, Any]) -> Dict[str, Any]:
    """Construye el payload completo del heartbeat."""
    
    # Leer identidad
    identity = read_identity_md()
    
    # Obtener sub-agentes automáticamente
    print("  📊 Escaneando sub-agentes...")
    subagents = get_all_subagents()
    print(f"     ✓ Encontrados: {len(subagents)}")
    for sa in subagents:
        print(f"       - {sa['name']} ({sa['agent_id']})")
    
    # Obtener skills
    print("  📊 Escaneando skills...")
    skills = get_all_skills()
    print(f"     ✓ Encontradas: {len(skills)}")
    
    # Obtener cron jobs
    print("  📊 Obteniendo cron jobs...")
    cron_jobs = get_cron_jobs()
    print(f"     ✓ Encontrados: {len(cron_jobs)}")
    
    # Métricas
    metrics = get_system_metrics()
    
    # Construir payload del agente
    agent_payload = {
        'agent_id': config['agent_id'],
        'name': identity.get('name', config['agent_name']),
        'email': config.get('user_email', ''),  # NUEVO: Email para registro en Loopy
        'status': 'online',
        'emoji': identity.get('emoji', '🤖'),
        'runtime_type': 'OpenClaw',
        'sub_agents': subagents[:10],  # Limitar a 10
        'skills': [{'name': s.get('name', 'unknown'), 
                    'category': s.get('category', 'general')} 
                   for s in skills[:10]],
        'cron_jobs': cron_jobs,
        'memory_summary': metrics,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    # Generar idempotency key (por hora)
    hour_bucket = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
    idem_key = hashlib.sha256(
        f"{config['agent_id']}_heartbeat_{hour_bucket}".encode()
    ).hexdigest()[:32]
    
    return {
        'event_type': 'agent.heartbeat',
        'idempotency_key': idem_key,
        'organization_id': config['org_id'],
        'agent': agent_payload
    }


# ============================================
# ENVÍO
# ============================================

def send_heartbeat(payload: Dict[str, Any], config: Dict[str, Any], 
                   dry_run: bool = False) -> bool:
    """Envía el heartbeat a Loopy Orion."""
    
    if dry_run:
        print("\n📋 PAYLOAD (dry-run, no se envía):")
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
        return True
    
    if not config['token']:
        print("\n❌ Error: LOOPY_AGENT_REGISTRY_TOKEN no configurado")
        print("   Configura: export LOOPY_AGENT_REGISTRY_TOKEN='tu-token'")
        return False
    
    if not config['org_id']:
        print("\n❌ Error: LOOPY_ORGANIZATION_ID no configurado")
        return False
    
    print(f"\n📡 Enviando a Loopy Orion...")
    
    try:
        import requests
        
        headers = {
            'Authorization': f"Bearer {config['token']}",
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            config['webhook_url'],
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Log resultado
        log_entry = f"[{datetime.now().strftime('%a %b %d %H:%M:%S %Z %Y')}] "
        
        if response.status_code in [200, 201, 208]:
            log_entry += "Heartbeat enviado OK\n"
            print(f"   ✅ HTTP {response.status_code} - OK")
            success = True
        else:
            log_entry += f"ERROR: HTTP {response.status_code} - {response.text[:100]}\n"
            print(f"   ❌ HTTP {response.status_code}")
            print(f"   📝 {response.text[:200]}")
            success = False
        
        # Escribir log
        try:
            log_path = Path(config['log_file'])
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"   ⚠️  No se pudo escribir log: {e}")
        
        return success
        
    except ImportError:
        print("   ❌ Error: requests no instalado")
        print("   Instala: pip install requests")
        return False
    except Exception as e:
        print(f"   ❌ Error enviando: {e}")
        return False


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description='Heartbeat automático para Loopy Orion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 heartbeat.py                    # Enviar heartbeat normal
  python3 heartbeat.py --dry-run          # Ver payload sin enviar
  python3 heartbeat.py --verbose          # Mostrar más detalles

Variables de entorno requeridas:
  LOOPY_AGENT_REGISTRY_TOKEN    Token de autenticación
  LOOPY_ORGANIZATION_ID         ID de organización en Loopy
  LOOPY_USER_EMAIL              Email del propietario (para registro en Loopy)
        """
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar payload sin enviar')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Mostrar información detallada')
    
    args = parser.parse_args()
    
    print("🔄 Loopy Agent Heartbeat")
    print("=" * 50)
    
    # Configuración
    config = get_config()
    
    if args.verbose:
        print(f"\n⚙️  Configuración:")
        print(f"   Agente: {config['agent_id']}")
        print(f"   Email: {config['user_email'] or '(no configurado)'}")
        print(f"   Org ID: {config['org_id'][:8]}..." if config['org_id'] else "   Org ID: (no configurado)")
        print(f"   Token: {'✓ Configurado' if config['token'] else '✗ No configurado'}")
    
    # Construir payload
    print(f"\n📦 Construyendo payload...")
    payload = build_heartbeat_payload(config)
    
    # Enviar
    success = send_heartbeat(payload, config, dry_run=args.dry_run)
    
    print("\n" + "=" * 50)
    if args.dry_run:
        print("🏁 Dry-run completado")
    elif success:
        print("✅ Heartbeat enviado correctamente")
    else:
        print("❌ Heartbeat falló")
    
    return 0 if success or args.dry_run else 1


if __name__ == '__main__':
    sys.exit(main())