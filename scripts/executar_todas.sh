#!/usr/bin/env bash
# Atalho em shell para executar todas as instâncias
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$ROOT/scripts/executar_todas.py" "$@"
