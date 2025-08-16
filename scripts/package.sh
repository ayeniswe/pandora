#!/usr/bin/env bash
# Build a standalone executable using PyInstaller.
set -euo pipefail

MODULE="pandora"
ENTRY="src/pandora/__main__.py"

python -m pyinstaller --name "${MODULE}" --onefile "${ENTRY}"
