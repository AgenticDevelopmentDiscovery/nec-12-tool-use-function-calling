"""Minimal stdio MCP server for the tutorial, with no external dependencies.

Codex sends one JSON-RPC message per stdin line. We send one response per
stdout line. Keep ordinary prints out of this process: stdout is the protocol.
This implements the handshake and tools subset used by our bundled Codex.
"""

import json
import sys
from pathlib import Path

# Import the tool definitions from the checkout root, regardless of working dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tools
from src.session_log import SessionLog


PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
TOOL_DEFINITIONS = tools.TOOL_DEFINITIONS
TOOL_HANDLERS = {
    definition["name"]: getattr(tools, definition["name"])
    for definition in TOOL_DEFINITIONS
}
SESSION_LOG = SessionLog()


def log_message(direction, message, request=None):
    """Keep tool calls, results, and errors; omit discovery and protocol chatter."""
    if direction == "request":
        if isinstance(message, dict) and message.get("method") == "tools/call":
            params = message.get("params", {})
            if isinstance(params, dict):
                SESSION_LOG.write("tool_call", call_id=message.get("id"), tool=params.get("name"), arguments=params.get("arguments", {}))
        return
    if request and request.get("method") == "tools/list":
        return
    if "error" in message:
        SESSION_LOG.write("tool_error", call_id=message.get("id"), error=message["error"]["message"])
    elif request and request.get("method") == "tools/call":
        result = message["result"]
        text = result["content"][0]["text"]
        tool_name = request["params"]["name"]
        if result.get("isError"):
            SESSION_LOG.write("tool_error", tool=tool_name, call_id=message["id"], error=text)
        else:
            try:
                output = json.loads(text)
            except json.JSONDecodeError:
                output = text
            SESSION_LOG.write("tool_result", tool=tool_name, call_id=message["id"], result=output)


def error(request_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def handle_request(request):
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return error(None, -32600, "Invalid request")
    method = request.get("method")
    if not isinstance(method, str):
        return error(request.get("id"), -32600, "Invalid request")
    # Notifications, including notifications/initialized, have no response.
    if "id" not in request:
        return None
    request_id = request["id"]
    params = request.get("params", {})
    if not isinstance(params, dict):
        return error(request_id, -32602, "Parameters must be an object")

    if method == "initialize":
        requested_version = params.get("protocolVersion")
        version = (
            requested_version
            if requested_version in PROTOCOL_VERSIONS
            else PROTOCOL_VERSIONS[0]
        )
        result = {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tutorial-bank", "version": "1.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOL_DEFINITIONS}
    elif method == "tools/call":
        name = params.get("name")
        if not isinstance(name, str) or name not in TOOL_HANDLERS:
            return error(request_id, -32602, "Unknown tool")
        arguments = params.get("arguments", {})
        try:
            if not isinstance(arguments, dict):
                raise ValueError("Arguments must be an object")
            # Match the argument names to the Python function's parameters.
            output = TOOL_HANDLERS[name](**arguments)
            text = output if isinstance(output, str) else json.dumps(output)
            result = {
                "content": [{"type": "text", "text": text}],
                "isError": False,
            }
        except (TypeError, ValueError, OSError) as exc:
            # Tool errors are returned to the model so it can correct its call.
            result = {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True,
            }
    else:
        return error(request_id, -32601, "Method not found")

    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main():
    for line in sys.stdin:
        request = None
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = error(None, -32700, "Invalid JSON")
        else:
            log_message("request", request)
            response = handle_request(request)
        if response is not None:
            log_message("response", response, request if isinstance(request, dict) else None)
            print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
