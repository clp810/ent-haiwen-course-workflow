#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON:-python3}"

cd "$repo_root"
"$python_bin" -m unittest discover -s tests -v
"$python_bin" scripts/audit_repository.py
