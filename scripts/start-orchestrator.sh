#!/usr/bin/env bash
set -euo pipefail

workspace=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
cd -- "$workspace"

if command -v orca >/dev/null; then
    orca_cli=orca
else
    orca_cli=orca-ide
fi

# Serialize launches for this workspace and check the live Orca terminal list.
exec 9<"$workspace"
flock 9
terminals=$("$orca_cli" terminal list --worktree "path:$workspace" --include-visual-layouts --json)
existing=$(python3 -c '
import json, sys

def orchestrator_tabs(node):
    if isinstance(node, dict):
        if "panes" in node and node.get("title") == "Orchestrator":
            yield node["tabId"]
        for value in node.values():
            yield from orchestrator_tabs(value)
    elif isinstance(node, list):
        for value in node:
            yield from orchestrator_tabs(value)

result = json.load(sys.stdin)["result"]
tab_ids = set(orchestrator_tabs(result["visualLayouts"]))
for terminal in result["terminals"]:
    if terminal["connected"] and terminal["tabId"] in tab_ids:
        print(terminal["handle"])
        break
' <<< "$terminals")

if [[ -n "$existing" ]]; then
    printf 'Orchestrator is already open in %s.\n' "$existing"
    exit 0
fi

"$orca_cli" terminal create --worktree "path:$workspace" --title Orchestrator \
    --command 'if [ -f ./.env ]; then set -a; . ./.env; set +a; fi; codex "You are the LocalSber Orchestrator. Set this thread title to Orchestrator if the title tool is available. Read AGENTS.md and the Orchestrator workflow in setup.md. Use the task-tracker skill and the shared tracker as the source of truth and verify access before creating or claiming tasks. Confirm readiness and wait for the next instruction."'
