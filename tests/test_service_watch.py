from __future__ import annotations

import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from service_watch.core import render_markdown, report_payload, run_checks


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"healthy")

    def log_message(self, format: str, *args) -> None:
        return


class ServiceWatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_http_tcp_and_disk_checks_pass(self) -> None:
        port = self.server.server_address[1]
        with tempfile.TemporaryDirectory() as temp:
            results = run_checks(
                {
                    "checks": [
                        {"name": "Demo HTTP", "type": "http", "url": f"http://127.0.0.1:{port}/health"},
                        {"name": "Demo TCP", "type": "tcp", "host": "127.0.0.1", "port": port},
                        {"name": "Demo disk", "type": "disk", "path": temp, "minimum_free_percent": 0},
                    ]
                }
            )
        self.assertTrue(all(item.ok for item in results))
        self.assertTrue(report_payload(results)["ok"])
        self.assertIn("3 passed", render_markdown(results))

    def test_wrong_status_and_unknown_type_are_reported(self) -> None:
        port = self.server.server_address[1]
        results = run_checks(
            {
                "checks": [
                    {"name": "Wrong expectation", "type": "http", "url": f"http://127.0.0.1:{port}/", "expected_status": 204},
                    {"name": "Unknown", "type": "magic"},
                ]
            }
        )
        self.assertFalse(results[0].ok)
        self.assertFalse(results[1].ok)
        self.assertEqual(report_payload(results)["summary"]["failed"], 2)


if __name__ == "__main__":
    unittest.main()

