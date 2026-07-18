#!/usr/bin/env bash
# Block likely secrets from being written via tool use.
set -euo pipefail

input=$(cat)

if echo "$input" | grep -qE 'sk-ant-|ANTHROPIC_API_KEY=[a-zA-Z0-9]|ghp_[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}'; then
  cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Potential secret detected. Use .env or settings.local.json instead."
  }
}
EOF
  exit 0
fi

exit 0
