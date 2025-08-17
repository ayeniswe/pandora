#!/usr/bin/env bash
# Build a standalone executable using PyInstaller.
set -euo pipefail

MODULE="pandora"
ENTRY="src/pandora_cli/__main__.py"

pyinstaller --name "${MODULE}" --onefile "${ENTRY}"
