"""Read-only local dashboard bridge for the Battle Arena agent.

This server only serves the static dashboard and reads local checkpoint/log files.
It never calls the Arena API and exposes no endpoint that can spend credits or make offers.
Default bind is loopback only (127.0.0.1).
"""
from __future__ import annotations
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
STATE_DIR = Path(os.environ.get("STATE_DIR", str(ROOT / "state"))).expanduser().resolve()
HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
PORT = int(os.environ.get("DASHBOARD_PORT", "8765"))


def read_state():
    path = STATE_DIR / "state.json"
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}, False, None
        return data, True, path
    except (OSError, ValueError):
        return {}, False, path


def read_logs(limit=40):
    path = STATE_DIR / "decisions.jsonl"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-max(1, min(limit, 200)):]
        out = []
        for line in lines:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    out.append(item)
            except ValueError:
                out.append({"msg": line.strip(), "parse_error": True})
        return out, len(lines)
    except OSError:
        return [], 0


class Handler(BaseHTTPRequestHandler):
    server_version = "BattleArenaDashboard/1.0"

    def log_message(self, fmt, *args):
        print("[dashboard] " + fmt % args)

    def send_bytes(self, body: bytes, content_type: str, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_bytes(body, "application/json; charset=utf-8", status)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/status":
            state, exists, path = read_state()
            logs, log_count = read_logs(200)
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds") if exists and path else None
            except OSError:
                mtime = None
            cands = state.get("cands", {})
            signed = state.get("signed", {})
            self.send_json({
                "bridge": "connected", "read_only": True,
                "state_available": exists,
                "state_file_exists": bool(path and path.exists()),
                "state_file": str(path) if path else None,
                "state_mtime": mtime,
                "candidate_count": len(cands) if isinstance(cands, (dict, list)) else 0,
                "signed_count": len(signed) if isinstance(signed, (dict, list)) else 0,
                "log_lines": log_count,
                "key_configured": bool(os.environ.get("ARENA_KEY")),
            })
            return
        if url.path == "/api/state":
            state, exists, path = read_state()
            self.send_json({"available": exists, "state": state})
            return
        if url.path == "/api/logs":
            try:
                limit = int(parse_qs(url.query).get("limit", ["40"])[0])
            except (TypeError, ValueError):
                limit = 40
            entries, total = read_logs(limit)
            self.send_json({"entries": entries, "returned": len(entries), "log_lines_read": total})
            return
        if url.path in ("/", "/index.html"):
            file = FRONTEND / "index.html"
            try:
                self.send_bytes(file.read_bytes(), "text/html; charset=utf-8")
            except OSError:
                self.send_bytes(b"Dashboard frontend/index.html was not found.", "text/plain; charset=utf-8", 404)
            return
        if url.path == "/favicon.ico":
            self.send_bytes(b"", "image/x-icon", 204)
            return
        self.send_json({"error": "not_found"}, 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Battle Arena Command Center: http://{HOST}:{PORT}")
    print(f"Dashboard state directory: {STATE_DIR}")
    print("Read-only local bridge. Stop with Ctrl+C.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
