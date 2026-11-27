"""A tiny in-memory inventory REST API (standard library only).

It exists to give the test suite something real to test. Run it directly with
`python -m app.server` and it listens on http://127.0.0.1:8000.
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Store:
    def __init__(self):
        self._items: dict[int, dict] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def list(self):
        with self._lock:
            return list(self._items.values())

    def get(self, item_id):
        with self._lock:
            return self._items.get(item_id)

    def create(self, name, quantity):
        with self._lock:
            item = {"id": self._next_id, "name": name, "quantity": quantity}
            self._items[self._next_id] = item
            self._next_id += 1
            return item

    def delete(self, item_id):
        with self._lock:
            return self._items.pop(item_id, None)


def validate_item(payload):
    """Return an error message, or None if the payload is valid."""
    if not isinstance(payload, dict):
        return "body must be a JSON object"
    name, quantity = payload.get("name"), payload.get("quantity")
    if not isinstance(name, str) or not name.strip():
        return "name must be a non-empty string"
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return "quantity must be an integer"
    if quantity < 0:
        return "quantity must be >= 0"
    return None


def make_handler(store: Store):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep test output quiet
            pass

        def _send(self, status, body=None):
            data = json.dumps(body).encode() if body is not None else b""
            self.send_response(status)
            if body is not None:
                self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _item_id(self):
            parts = self.path.strip("/").split("/")
            if len(parts) == 2 and parts[0] == "items" and parts[1].isdigit():
                return int(parts[1])
            return None

        def do_GET(self):
            if self.path.rstrip("/") == "/items":
                return self._send(200, store.list())
            item_id = self._item_id()
            if item_id is not None:
                item = store.get(item_id)
                return self._send(200, item) if item else self._send(404, {"error": "not found"})
            self._send(404, {"error": "unknown route"})

        def do_POST(self):
            if self.path.rstrip("/") != "/items":
                return self._send(404, {"error": "unknown route"})
            length = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"")
            except json.JSONDecodeError:
                return self._send(400, {"error": "invalid JSON"})
            error = validate_item(payload)
            if error:
                return self._send(400, {"error": error})
            self._send(201, store.create(payload["name"].strip(), payload["quantity"]))

        def do_DELETE(self):
            item_id = self._item_id()
            if item_id is None:
                return self._send(404, {"error": "unknown route"})
            if store.delete(item_id):
                return self._send(204)
            self._send(404, {"error": "not found"})

    return Handler


def create_server(host="127.0.0.1", port=0):
    """Create (but do not start) a server. port=0 picks a free port."""
    return ThreadingHTTPServer((host, port), make_handler(Store()))


if __name__ == "__main__":
    server = create_server(port=8000)
    print("Listening on http://127.0.0.1:8000")
    server.serve_forever()
