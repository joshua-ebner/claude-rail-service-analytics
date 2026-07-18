#!/usr/bin/env bash
# Lint Python files after edit.
set -euo pipefail

input=$(cat)
file_path=$(echo "$input" | python3 -c "
import sys, json
d = json.load(sys.stdin)
tool_input = d.get('tool_input') or {}
print(tool_input.get('file_path') or tool_input.get('path') or '')
" 2>/dev/null || echo "")

if [[ -z "$file_path" || ! "$file_path" == *.py ]]; then
  exit 0
fi

if [[ ! -f "$file_path" ]]; then
  exit 0
fi

if command -v ruff >/dev/null 2>&1; then
  ruff check "$file_path" 2>&1 || true
else
  python3 -m py_compile "$file_path" 2>&1 || true
fi

exit 0
