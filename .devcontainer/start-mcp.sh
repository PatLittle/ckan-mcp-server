#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-3000}"
TRANSPORT="${TRANSPORT:-http}"
ENDPOINT_LOCAL="http://localhost:${PORT}/mcp"

# Try to discover the public Codespaces URL for this port.
# In Codespaces, forwarded ports usually map to:
# https://<CODESPACE_NAME>-<PORT>.app.github.dev
PUBLIC_HOST=""
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  PUBLIC_HOST="https://${CODESPACE_NAME}-${PORT}.app.github.dev"
fi
ENDPOINT_PUBLIC=""
if [[ -n "${PUBLIC_HOST}" ]]; then
  ENDPOINT_PUBLIC="${PUBLIC_HOST}/mcp"
fi

# Start the server if not already running
if pgrep -f "ckan-mcp-server" >/dev/null 2>&1; then
  RUN_STATE="RUNNING"
else
  RUN_STATE="STARTING"
  nohup env TRANSPORT="${TRANSPORT}" PORT="${PORT}" ckan-mcp-server \
    > /tmp/ckan-mcp-server.log 2>&1 &
  RUN_STATE="RUNNING"
fi

clear || true

cat <<'BANNER'
┌──────────────────────────────────────────────────────────────┐
│                 CKAN MCP SERVER — CODESPACES                 │
└──────────────────────────────────────────────────────────────┘
BANNER

echo "Status: ${RUN_STATE}"
echo "Logs:   /tmp/ckan-mcp-server.log"
echo

echo "Local MCP endpoint (inside the Codespace):"
echo "  ${ENDPOINT_LOCAL}"
echo

if [[ -n "${ENDPOINT_PUBLIC}" ]]; then
  echo "Public MCP endpoint (for ChatGPT / remote clients):"
  echo "  ${ENDPOINT_PUBLIC}"
  echo
else
  echo "Public MCP endpoint:"
  echo "  (Could not auto-derive. Use the Ports tab URL + '/mcp')"
  echo
fi

cat <<'GUIDE'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1) Make the port reachable (Codespaces)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• In VS Code (web): open the "Ports" tab
• Find port 3000 → set Visibility to "Public"
• Copy the forwarded URL (it looks like: https://…app.github.dev)
• Your MCP URL is: <forwarded-url>/mcp

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2) Add to ChatGPT (Custom MCP connector)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• ChatGPT → Settings → Connectors / Tools → Add MCP server
• Paste the MCP URL (must be https://…/mcp)
• Save → enable it in your chat/tool picker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3) Add to GitHub Copilot (VS Code)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Option A — npx (runs locally in the devcontainer):
  In .vscode/settings.json:
  {
    "mcpServers": {
      "ckan": { "command": "npx", "args": ["@aborruso/ckan-mcp-server@latest"] }
    }
  }

Option B — point Copilot at the HTTP endpoint (if your Copilot MCP UI supports URLs):
  Use the same https://…/mcp endpoint shown above.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Quick test (inside Codespace):
  curl -X POST http://localhost:3000/mcp \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUIDE
