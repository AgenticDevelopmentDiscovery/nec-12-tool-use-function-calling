"""Run Codex through a localhost proxy with a readable conversation log.

Use ./codex to keep the normal interactive terminal UI while
writing a concise model/tool conversation to one logs/session-*.log file.
The proxy uses HTTP streaming with the saved ChatGPT login. The MCP server
inherits the same file, so model output and actual tool execution stay together.
"""

import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.session_log import LOG_ENVIRONMENT_VARIABLE, SessionLog
UPSTREAM_HOST = "chatgpt.com"
UPSTREAM_PATH = "/backend-api/codex"
HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade", "host", "content-length"}


def readable_output(value):
    """Unwrap code-mode text blocks and nested JSON for the session log."""
    if isinstance(value, str):
        if value.lstrip().startswith(("{", "[")):
            try:
                return readable_output(json.loads(value))
            except json.JSONDecodeError:
                pass
        return value
    if isinstance(value, list):
        if value and all(isinstance(item, dict) and item.get("type") in ("text", "input_text") for item in value):
            parts = [readable_output(item.get("text", "")) for item in value if not item.get("text", "").startswith("Script completed\n")]
            return parts[0] if len(parts) == 1 else parts
        return [readable_output(item) for item in value]
    if isinstance(value, dict):
        if "content" in value and "isError" in value:
            content = readable_output(value["content"])
            return {"error": content} if value["isError"] else content
        if "chunk_id" in value and "output" in value:
            return {key: readable_output(value[key]) for key in ("exit_code", "output") if key in value}
        return {key: readable_output(item) for key, item in value.items()}
    return value


class ModelTrace:
    def __init__(self):
        self.logger = SessionLog(new_session=True)
        self.path = self.logger.path
        os.environ[LOG_ENVIRONMENT_VARIABLE] = str(self.path)
        self.lock = threading.Lock()
        self.next_id = 0
        self.previous_input = []

    def request_id(self):
        with self.lock:
            self.next_id += 1
            return self.next_id

    def write(self, direction, request_id, message, **metadata):
        if direction == "model_request":
            self.log_request(request_id, message)
        elif direction == "proxy_error":
            self.logger.write("model_error", request_id=request_id, error=message.get("error"))
        elif direction == "model_response":
            self.log_response(request_id, message)

    def log_request(self, request_id, message):
        relevant = []
        for item in message.get("input", []):
            if item.get("type") == "message" and item.get("role") == "user":
                text = "\n".join(part.get("text", "") for part in item.get("content", []))
                if text and not text.lstrip().startswith("<environment_context>"):
                    relevant.append({"role": "user", "text": text})
            elif item.get("type") in ("function_call_output", "custom_tool_call_output"):
                relevant.append({"call_id": item.get("call_id"), "output": item.get("output")})
        # Repeated context is already visible earlier in this session log.
        common = 0
        for old, new in zip(self.previous_input, relevant):
            if old != new:
                break
            common += 1
        for item in relevant[common:]:
            if item.get("role") == "user":
                self.logger.write("user_message", request_id=request_id, text=item["text"])
                self.logger.write("prompt_forwarded", request_id=request_id)
            else:
                self.logger.write("harness_result", call_id=item.get("call_id"), result=readable_output(item.get("output")))
        self.previous_input = relevant

    def log_response(self, request_id, message):
        kind = message.get("type")
        if kind == "response.output_item.done":
            item = message.get("item", {})
            if item.get("type") in ("function_call", "custom_tool_call"):
                fields = {"request_id": request_id, "call_id": item.get("call_id"), "tool": item.get("name")}
                if item.get("type") == "function_call":
                    arguments = item.get("arguments", "{}")
                    try:
                        arguments = json.loads(arguments)
                    except (json.JSONDecodeError, TypeError):
                        pass
                    fields["arguments"] = arguments
                else:
                    fields["input"] = item.get("input")
                self.logger.write("model_tool_call", **fields)
            elif item.get("type") == "message":
                text = "\n".join(part.get("text", "") for part in item.get("content", []) if part.get("type") == "output_text")
                if text:
                    self.logger.write("model_response", request_id=request_id, text=text)
                    self.logger.write("response_displayed", request_id=request_id)
        elif kind in ("error", "response.failed") or "error" in message:
            details = message.get("error") or message.get("response", {}).get("error")
            self.logger.write("model_error", request_id=request_id, error=details)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.split("?", 1)[0] != "/v1/models":
            self.send_error(404, "Only model discovery is supported")
            return
        headers = {key: value for key, value in self.headers.items() if key.lower() not in HOP_HEADERS}
        headers["Accept-Encoding"] = "identity"
        upstream = http.client.HTTPSConnection(UPSTREAM_HOST, timeout=60)
        try:
            upstream.request("GET", UPSTREAM_PATH + self.path.removeprefix("/v1"), headers=headers)
            response = upstream.getresponse()
            content = response.read()
            self.send_response(response.status)
            self.send_header("Content-Type", response.getheader("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (OSError, http.client.HTTPException):
            self.send_error(502, "Model discovery connection failed")
        finally:
            upstream.close()

    def do_POST(self):
        if self.path not in ("/v1/responses", "/v1/responses/compact"):
            self.send_error(404, "Only Responses API requests are supported")
            return
        trace = self.server.trace
        request_id = trace.request_id()
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        try:
            message = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Expected uncompressed JSON")
            return
        trace.write("model_request", request_id, message, path=self.path)
        headers = {key: value for key, value in self.headers.items() if key.lower() not in HOP_HEADERS}
        # Auth headers are forwarded to the existing service but never logged.
        headers["Accept-Encoding"] = "identity"
        upstream = http.client.HTTPSConnection(UPSTREAM_HOST, timeout=300)
        try:
            upstream.request("POST", UPSTREAM_PATH + self.path.removeprefix("/v1"), body=body, headers=headers)
            response = upstream.getresponse()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in HOP_HEADERS:
                    self.send_header(key, value)
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            # The ChatGPT endpoint can return SSE with an application/json header.
            if response.status == 200 and message.get("stream") is True:
                self.forward_events(response, trace, request_id)
            else:
                content = response.read()
                try:
                    message = json.loads(content)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    message = {"raw": content.decode("utf-8", errors="replace")}
                trace.write("model_response", request_id, message, status=response.status)
                self.wfile.write(content)
                self.wfile.flush()
        except (OSError, http.client.HTTPException) as exc:
            trace.write("proxy_error", request_id, {"error": str(exc)})
            self.close_connection = True
        finally:
            upstream.close()

    def forward_events(self, response, trace, request_id):
        data = []
        event = None
        while line := response.readline():
            self.wfile.write(line)
            self.wfile.flush()
            text = line.decode("utf-8").rstrip("\r\n")
            if text.startswith("event:"):
                event = text[6:].lstrip()
            elif text.startswith("data:"):
                data.append(text[5:].lstrip())
            elif not text and data:
                self.log_event(trace, request_id, data, event)
                data = []
                event = None
        if data:
            self.log_event(trace, request_id, data, event)

    def log_event(self, trace, request_id, data, event):
        raw = "\n".join(data)
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            message = {"raw": raw}
        trace.write("model_response", request_id, message, event=event)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 src/model_trace.py CODEX_BINARY [CODEX_ARGS...]")
    arguments = sys.argv[2:]
    if any(argument in ("--sandbox", "-s", "--dangerously-bypass-approvals-and-sandbox") or argument.startswith("--sandbox=") for argument in arguments):
        raise SystemExit("This launcher uses a source-hiding permission profile; --sandbox would replace it.")
    workspace = ROOT / ".codex-home/agent-workspace"
    workspace.mkdir(mode=0o700, parents=True, exist_ok=True)
    filesystem = "{" + ", ".join(
        f"{json.dumps(path)}={json.dumps(access)}"
        for path, access in {
            ":root": "deny",
            ":minimal": "read",
            str(workspace): "read",
            str(ROOT / "vendor"): "read",
            str(ROOT / "src"): "deny",
            str(ROOT / "tools.py"): "deny",
            str(ROOT / "__pycache__"): "deny",
            str(ROOT / "logs"): "deny",
            str(ROOT / ".codex-home/auth.json"): "deny",
        }.items()
    ) + "}"
    trace = ModelTrace()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.trace = trace
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Session log: {trace.path}", file=sys.stderr)
    command = [
        sys.argv[1],
        "--no-daemon",
        "--cd", str(workspace),
        "-c", 'project_root_markers=[]',
        "-c", 'default_permissions="bank-demo"',
        "-c", f'permissions.bank-demo.filesystem={filesystem}',
        "-c", 'permissions.bank-demo.network.enabled=false',
        "-c", 'approval_policy="never"',
        "-c", 'mcp_servers.bank.default_tools_approval_mode="approve"',
        "-c", 'model_provider="model_trace"',
        "-c", 'model_providers.model_trace.name="ChatGPT model trace"',
        "-c", f'model_providers.model_trace.base_url="http://127.0.0.1:{server.server_port}/v1"',
        "-c", 'model_providers.model_trace.wire_api="responses"',
        "-c", 'model_providers.model_trace.requires_openai_auth=true',
        "-c", 'model_providers.model_trace.supports_websockets=false',
        "-c", 'features.enable_request_compression=false',
        "-c", f'mcp_servers.bank.env_vars=["{LOG_ENVIRONMENT_VARIABLE}"]',
        *arguments,
    ]
    try:
        result = subprocess.run(command, cwd=workspace)
        return result.returncode
    except KeyboardInterrupt:
        return 130
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
