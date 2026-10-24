"""Authenticated localhost JSON bridge for independently implemented actors."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import socket
from threading import Lock

from personasciencebench.schema import Submission
from personasciencebench.session import EpisodeSession

TOOLS = {
    "ask_researcher": {"question": "string", "topic": "optional string"},
    "report_progress": {"message": "string"},
    "submit_plan": {"plan": "string"},
    "submit_result": {"episode_id": "string", "stage": "final", "answer": "string",
                      "payload": "object", "artifacts": "name to path mapping within the configured actor artifact root"},
}


def server_for(session: EpisodeSession, token: str, *, host="127.0.0.1", port=0):
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise ValueError("Use a localhost tunnel for remote actors; public binding is not enabled")
    if len(token) < 24:
        raise ValueError("Researcher endpoint token must have at least 24 characters")
    lock = Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # The default logger may include private question URLs; disable it.
            return

        def send(self, code, payload):
            data = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def authenticated(self):
            return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token)

        def do_GET(self):
            if not self.authenticated():
                return self.send(401, {"error": "Authentication required"})
            if self.path == "/context":
                return self.send(200, session.episode.actor_input())
            if self.path == "/tools":
                return self.send(200, TOOLS)
            return self.send(404, {"error": "Unknown endpoint"})

        def do_POST(self):
            if not self.authenticated():
                return self.send(401, {"error": "Authentication required"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2_000_000:
                    return self.send(413, {"error": "Invalid request size"})
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError("Request must be an object")
                with lock:
                    if self.path == "/ask_researcher":
                        result = session.ask_researcher(**body)
                    elif self.path == "/report_progress":
                        result = session.report_progress(**body)
                    elif self.path == "/submit_plan":
                        result = session.submit_plan(**body)
                    elif self.path == "/submit_result":
                        result = session.submit_result(Submission.model_validate(body))
                    else:
                        return self.send(404, {"error": "Unknown endpoint"})
                return self.send(200, result)
            except (ValueError, TypeError, KeyError):
                return self.send(400, {"error": "Invalid request or episode state"})
            except Exception:
                # Never expose controller paths, credentials or raw provider errors.
                with lock:
                    session.event("protocol_error", {"endpoint": self.path})
                return self.send(502, {"error": "Controller operation failed; consult private run records"})

    if host == "::1":
        class IPv6Server(ThreadingHTTPServer):
            address_family = socket.AF_INET6
        return IPv6Server((host, port), Handler)
    return ThreadingHTTPServer((host, port), Handler)
