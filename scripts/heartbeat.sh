#!/bin/bash
# Loopy Heartbeat Script - Wrapper para heartbeat.py
# Uso: ./heartbeat.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/heartbeat.py" "$@"
