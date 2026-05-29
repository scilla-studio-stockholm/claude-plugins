#!/usr/bin/env python3
"""Dual-mount HTTP server for OST viewer.

Serves /_viewer/* from the viewer templates directory and /* from the
workspace discovery directory. Directory listings return JSON arrays
of *.json filenames only.

Usage:
    python3 serve.py --templates path/to/viewer --data path/to/discovery [--port 3000]
"""

import argparse
import json
import os
import posixpath
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


def make_handler(templates_dir: Path, data_dir: Path):
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path: str) -> str:
            path = posixpath.normpath(path)
            if path.startswith("/_viewer"):
                rel = path[len("/_viewer"):].lstrip("/")
                return str(templates_dir / rel)
            rel = path.lstrip("/")
            return str(data_dir / rel)

        def do_GET(self):
            path = posixpath.normpath(self.path.split("?")[0].split("#")[0])

            if path.startswith("/_viewer") and (path == "/_viewer" or path == "/_viewer/"):
                self.path = "/_viewer/index.html"
                return super().do_GET()

            fs_path = Path(self.translate_path(path))
            if fs_path.is_dir():
                if path.startswith("/_viewer"):
                    self.send_error(403)
                    return
                json_files = sorted(
                    f.name for f in fs_path.iterdir()
                    if f.is_file() and f.suffix == ".json"
                )
                body = json.dumps(json_files).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
                return

            return super().do_GET()

        def guess_type(self, path):
            ext = os.path.splitext(path)[1].lower()
            return MIME_TYPES.get(ext, "application/octet-stream")

        def end_headers(self):
            self.send_header("Cache-Control", "no-cache")
            super().end_headers()

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description="OST Viewer server")
    parser.add_argument("--templates", required=True, help="Path to viewer/ directory")
    parser.add_argument("--data", required=True, help="Path to workspace OST-discovery/ directory")
    parser.add_argument("--port", type=int, default=3000, help="Port (default: 3000)")
    args = parser.parse_args()

    templates_dir = Path(args.templates).resolve()
    data_dir = Path(args.data).resolve()

    if not templates_dir.is_dir():
        parser.error(f"Templates directory not found: {templates_dir}")
    if not data_dir.is_dir():
        parser.error(f"Data directory not found: {data_dir}")

    handler = make_handler(templates_dir, data_dir)
    server = HTTPServer(("localhost", args.port), handler)
    print(f"Serving at http://localhost:{args.port}")
    print(f"  Viewer:  /_viewer/* -> {templates_dir}")
    print(f"  Data:    /*        -> {data_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
