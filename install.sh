#!/bin/bash
# install.sh - Script de instalación para loopy-agent-registry v2.0

set -e

echo "🚀 Instalando Loopy Agent Registry v2.0"
echo "========================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detectar rutas
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
WORKSPACE="${OPENCLAW_WORKSPACE:-$OPENCLAW_HOME/workspace}"
SKILLS_DIR="$WORKSPACE/skills"
TARGET_DIR="$SKILLS_DIR/loopy-agent-registry"

echo ""
echo "📁 Directorios detectados:"
echo "  OPENCLAW_HOME: $OPENCLAW_HOME"
echo "  WORKSPACE: $WORKSPACE"
echo "  TARGET: $TARGET_DIR"

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ Error: pip3 no está instalado${NC}"
    exit 1
fi

echo ""
echo "📦 Instalando dependencias Python..."
pip3 install --user pyyaml 2>/dev/null || pip3 install pyyaml

# Crear directorios
echo ""
echo "📁 Creando directorios..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$OPENCLAW_HOME/secrets"

# Copiar archivos
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "📂 Copiando archivos del skill..."
if [ -d "$TARGET_DIR" ]; then
    echo -e "${YELLOW}⚠️  El directorio ya existe. ¿Sobrescribir? (s/N)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        echo "Instalación cancelada."
        exit 0
    fi
    rm -rf "$TARGET_DIR"
fi

cp -r "$SCRIPT_DIR/loopy-agent-registry" "$TARGET_DIR"

# Verificar archivos requeridos
echo ""
echo "🔍 Verificando archivos..."
required_files=(
    "scripts/build_descriptor.py"
    "scripts/agent_context_reader.py"
    "scripts/subagent_scanner.py"
    "scripts/skills_scanner.py"
    "scripts/tasks_extractor.py"
    "scripts/common.py"
    "scripts/validate_descriptor.py"
    "scripts/send_registry_event.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$TARGET_DIR/$file" ]; then
        echo -e "${RED}❌ Falta archivo requerido: $file${NC}"
        exit 1
    fi
done

# Configurar permisos
echo ""
echo "🔧 Configurando permisos..."
chmod +x "$TARGET_DIR/scripts/"*.py 2>/dev/null || true

# Test de importación
echo ""
echo "🧪 Probando importación de módulos..."
cd "$TARGET_DIR"
python3 -c "
from scripts.agent_context_reader import get_agent_context
from scripts.subagent_scanner import get_all_subagents
from scripts.skills_scanner import get_all_skills
from scripts.tasks_extractor import get_all_tasks
from scripts.build_descriptor import build_payload
print('✅ Todos los módulos importados correctamente')
" || {
    echo -e "${RED}❌ Error al importar módulos${NC}"
    exit 1
}

# Verificar configuración
echo ""
echo "⚙️  Verificando configuración..."

if [ ! -f "$OPENCLAW_HOME/secrets/loopy-agent-registry" ]; then
    echo -e "${YELLOW}⚠️  Secrets no configurados${NC}"
    echo ""
    echo "Por favor crea el archivo: $OPENCLAW_HOME/secrets/loopy-agent-registry"
    echo "con el siguiente contenido:"
    echo ""
    echo "LOOPY_AGENT_REGISTRY_TOKEN=tu_token_aqui"
    echo "LOOPY_ORGANIZATION_ID=tu_org_uuid"
    echo ""
    echo "O exporta como variables de entorno:"
    echo "export LOOPY_AGENT_REGISTRY_TOKEN=tu_token"
    echo "export LOOPY_ORGANIZATION_ID=tu_org"
else
    echo -e "${GREEN}✅ Secrets encontrados${NC}"
fi

# Test de lectura de contexto
echo ""
echo "🧪 Probando lectura de contexto del agente..."
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from agent_context_reader import get_agent_context
ctx = get_agent_context()
print(f\"✅ Agente: {ctx.get('name', 'Unknown')}\")
print(f\"✅ ID: {ctx.get('agent_id', 'Unknown')[:8]}...\")
print(f\"✅ Runtime: {ctx.get('runtime_type', 'Unknown')}\")
" || {
    echo -e "${YELLOW}⚠️  No se pudo leer contexto (puede ser normal si no hay IDENTITY.md)${NC}"
}

# Resumen
echo ""
echo "========================================"
echo -e "${GREEN}✅ Instalación completada!${NC}"
echo "========================================"
echo ""
echo "📍 Ubicación: $TARGET_DIR"
echo ""
echo "🚀 Prueba la instalación:"
echo "  openclaw agent --agent main -m \"registra mi agente en Loopy\""
echo ""
echo "📖 Documentación: $TARGET_DIR/SKILL.MD"
echo ""
echo "⚠️  Recuerda configurar los secrets antes de usar:"
echo "  ~/.openclaw/secrets/loopy-agent-registry"
echo ""