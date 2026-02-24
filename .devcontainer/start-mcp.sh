#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-3000}"
TRANSPORT="${TRANSPORT:-http}"
LOCAL_ENDPOINT="http://localhost:${PORT}/mcp"

PUBLIC_ENDPOINT=""
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  PUBLIC_ENDPOINT="https://${CODESPACE_NAME}-${PORT}.app.github.dev/mcp"
fi

# Start server from the fork (npm start) if not running
if pgrep -f "node.*ckan" >/dev/null 2>&1; then
  STATUS="RUNNING"
else
  STATUS="STARTING"
  nohup env TRANSPORT="$TRANSPORT" PORT="$PORT" npm start \
    > /tmp/ckan-mcp-server.log 2>&1 &
  STATUS="RUNNING"
fi

clear || true

cat <<'BANNER'
┌──────────────────────────────────────────────────────────────┐
│                 CKAN MCP SERVER — CODESPACES                 │
└──────────────────────────────────────────────────────────────┘
BANNER

echo "Status: ${STATUS}"
echo "Logs:   /tmp/ckan-mcp-server.log"
echo
echo "Local MCP endpoint:"
echo "  ${LOCAL_ENDPOINT}"
echo

if [[ -n "${PUBLIC_ENDPOINT}" ]]; then
  echo "Public MCP endpoint:"
  echo "  ${PUBLIC_ENDPOINT}"
else
  echo "Public MCP endpoint:"
  echo "  (Check Ports tab URL and add /mcp)"
fi

cat <<'GUIDE'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1) Make port public (Codespaces)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ports tab → Port 3000 → Visibility: Public
Forwarded URL + "/mcp"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2) Add to ChatGPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Settings → Connectors/Tools → Add MCP server
Paste: https://…/mcp

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3) Add to GitHub Copilot (VS Code)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
.vscode/settings.json

{
  "mcpServers": {
    "ckan": {
      "url": "https://…/mcp"
    }
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test (inside Codespace):
curl -X POST http://localhost:3000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUIDE
