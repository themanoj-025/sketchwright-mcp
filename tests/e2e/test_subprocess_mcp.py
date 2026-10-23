"""End-to-end test verifying MCP server execution in a subprocess over stdio transport."""

import json
import subprocess
import sys


def test_mcp_subprocess_stdio_exchange() -> None:
    """Verify that launching 'sketchwright mcp' in a subprocess communicates via JSON-RPC

    and does not corrupt stdout with logging or diagnostic banners.
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", "sketchwright", "mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Standard MCP initialize request
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "e2e-tester", "version": "1.0"},
            },
        }

        request_line = json.dumps(init_req) + "\n"
        assert proc.stdin is not None
        proc.stdin.write(request_line)
        proc.stdin.flush()

        # Read line from stdout
        assert proc.stdout is not None
        response_line = proc.stdout.readline()

        # Verify response is strictly JSON and not corrupted by logging
        assert response_line.strip(), "Expected non-empty response from MCP server stdout"
        resp = json.loads(response_line)

        assert resp.get("jsonrpc") == "2.0"
        assert resp.get("id") == 1
        result = resp.get("result", {})
        assert result.get("serverInfo", {}).get("name") == "sketchwright"

        # Notify initialized and request tools/list
        init_notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        proc.stdin.write(json.dumps(init_notif) + "\n")

        tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        proc.stdin.write(json.dumps(tools_req) + "\n")
        proc.stdin.flush()

        tools_line = proc.stdout.readline()
        assert tools_line.strip(), "Expected response to tools/list"
        tools_resp = json.loads(tools_line)
        assert tools_resp.get("id") == 2
        tools_list = [t["name"] for t in tools_resp.get("result", {}).get("tools", [])]
        assert "sketchwright_create_diagram" in tools_list
        assert "sketchwright_validate_diagram" in tools_list
        assert "sketchwright_layout_diagram" in tools_list
        assert "sketchwright_export_diagram" in tools_list
        assert "sketchwright_get_capabilities" in tools_list
        assert "sketchwright_update_diagram" in tools_list

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
