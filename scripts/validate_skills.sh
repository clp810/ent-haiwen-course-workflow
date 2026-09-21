#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
codex_root="${CODEX_HOME:-$HOME/.codex}"
validator="$codex_root/skills/.system/skill-creator/scripts/quick_validate.py"
python_bin="${PYTHON:-python3}"

if [[ ! -f "$validator" ]]; then
  printf 'Skill validator not found: %s\n' "$validator" >&2
  printf 'Install or update the Codex skill-creator system skill, then retry.\n' >&2
  exit 1
fi

"$python_bin" "$validator" "$repo_root/.agents/skills/course-pm-companion"
"$python_bin" "$validator" "$repo_root/.agents/skills/course-weekly-delivery"
