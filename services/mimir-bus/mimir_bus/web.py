import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from mimir_bus.alerts import infirmary_payload
from mimir_bus.client import MimirBus

STATIC = Path(__file__).resolve().parent / "static" / "index.html"


class Console:
    def __init__(self, bus: MimirBus) -> None:
        self.bus = bus

    def state(self) -> dict:
        return {
            "connected": self.bus.connected,
            "pending": len(self.bus.store.pending()),
            "events": self.bus.store.recent(),
        }

    def publish(self, alert: str) -> dict:
        payload = infirmary_payload(alert)
        sent = self.bus.publish_infirmary(payload)
        return {"sent": sent, "queued": not sent, "payload": payload}


def make_handler(console: Console):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            return

        def _json(self, code: int, body: dict) -> None:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path.split("?", 1)[0] == "/api/state":
                self._json(200, console.state())
                return
            if self.path.split("?", 1)[0] in {"/", "/index.html"}:
                page = STATIC.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
                return
            self._json(404, {"error": "Introuvable"})

        def do_POST(self) -> None:
            if self.path.split("?", 1)[0] != "/api/alerts":
                self._json(404, {"error": "Introuvable"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length > 2000:
                self._json(400, {"error": "Message trop long"})
                return
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                result = console.publish(str(body.get("alert") or ""))
            except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
                self._json(400, {"error": "Alerte inconnue"})
                return
            self._json(200, result)

    return Handler


def serve(bus: MimirBus, port: int) -> None:
    handler = make_handler(Console(bus))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    server.serve_forever()
