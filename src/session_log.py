"""A shared, readable log with explicit USER, MODEL, HARNESS, and TOOL roles."""

from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path


LOG_DIRECTORY = Path(__file__).resolve().parent.parent / "logs"
LOG_ENVIRONMENT_VARIABLE = "BANK_DEMO_LOG_FILE"


class SessionLog:
    def __init__(self, new_session=False):
        LOG_DIRECTORY.mkdir(mode=0o700, exist_ok=True)
        inherited = None if new_session else os.environ.get(LOG_ENVIRONMENT_VARIABLE)
        if inherited:
            self.path = Path(inherited).resolve()
            if self.path.parent != LOG_DIRECTORY.resolve():
                raise ValueError("The session log must be inside this repository's logs folder")
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            self.path = LOG_DIRECTORY / f"session-{timestamp}-{os.getpid()}.log"
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        os.close(descriptor)

    def write(self, event, **fields):
        labels = {
            "user_message": ("USER -> HARNESS", "Prompt"),
            "prompt_forwarded": ("HARNESS -> MODEL", "Forward prompt"),
            "model_tool_call": ("MODEL -> HARNESS", "Call"),
            "harness_result": ("HARNESS -> MODEL", "Result"),
            "tool_call": ("HARNESS -> TOOL", "Call"),
            "tool_result": ("TOOL -> HARNESS", "Result"),
            "tool_error": ("TOOL -> HARNESS", "Error"),
            "model_response": ("MODEL -> HARNESS", "Response"),
            "response_displayed": ("HARNESS -> USER", "Display response"),
            "model_error": ("HARNESS", "Model request failed"),
        }
        roles, title = labels.get(event, ("SYSTEM", event))
        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        details = []
        if fields.get("tool"):
            details.append(fields["tool"])
        if fields.get("request_id") is not None:
            details.append(f"request {fields['request_id']}")
        if fields.get("call_id") is not None:
            details.append(f"call {fields['call_id']}")
        heading = f"[{timestamp}] [{roles}] {title}"
        if details:
            heading += " | " + " | ".join(map(str, details))
        body = []
        for key, value in fields.items():
            if key in ("tool", "request_id", "call_id") or value is None:
                continue
            if key in ("text", "error") and isinstance(value, str):
                body.append(value)
            elif key == "model":
                body.append(f"Model: {value}")
            else:
                formatted = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)
                body.append(f"{key.replace('_', ' ').title()}:\n{formatted}")
        entry = heading + "\n"
        if body:
            entry += "\n".join("  " + line for line in "\n".join(body).splitlines()) + "\n"
        entry += "\n"
        try:
            descriptor = os.open(self.path, os.O_WRONLY | os.O_APPEND)
            with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
                # Model and MCP processes may write concurrently. Keep records intact.
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                stream.write(entry)
                stream.flush()
        except OSError as exc:
            import sys
            print(f"Session logging failed: {exc}", file=sys.stderr)
