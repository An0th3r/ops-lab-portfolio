from __future__ import annotations

import json
import shutil
import socket
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CheckResult:
    name: str
    kind: str
    ok: bool
    message: str
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).resolve()
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read configuration: {config_path}") from exc
    if not isinstance(config, dict) or not isinstance(config.get("checks"), list):
        raise ValueError("Configuration must contain a checks array")
    return config


def _timed(name: str, kind: str, operation) -> CheckResult:
    started = time.perf_counter()
    try:
        ok, message = operation()
    except Exception as exc:  # A failed check becomes a result, not a program crash.
        ok, message = False, f"{type(exc).__name__}: {exc}"
    duration = round((time.perf_counter() - started) * 1000)
    return CheckResult(name=name, kind=kind, ok=bool(ok), message=str(message), duration_ms=duration)


def _http_check(check: dict[str, Any]) -> tuple[bool, str]:
    url = str(check["url"])
    timeout = float(check.get("timeout", 5))
    expected = int(check.get("expected_status", 200))
    request = urllib.request.Request(url, headers={"User-Agent": "OPS-LAB-Service-Watch/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
    return status == expected, f"HTTP {status}; expected {expected}"


def _tcp_check(check: dict[str, Any]) -> tuple[bool, str]:
    host = str(check["host"])
    port = int(check["port"])
    timeout = float(check.get("timeout", 5))
    with socket.create_connection((host, port), timeout=timeout):
        return True, f"Connection to {host}:{port} succeeded"


def _tls_check(check: dict[str, Any]) -> tuple[bool, str]:
    host = str(check["host"])
    port = int(check.get("port", 443))
    timeout = float(check.get("timeout", 5))
    minimum_days = float(check.get("minimum_days", 14))
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
            certificate = tls_socket.getpeercert()
    expires_raw = certificate.get("notAfter")
    if not expires_raw:
        return False, "Certificate has no expiration date"
    seconds_left = ssl.cert_time_to_seconds(expires_raw) - time.time()
    days_left = seconds_left / 86400
    return days_left >= minimum_days, f"Certificate valid for {days_left:.1f} days; minimum {minimum_days:g}"


def _disk_check(check: dict[str, Any]) -> tuple[bool, str]:
    path = Path(str(check.get("path", "."))).resolve()
    minimum = float(check.get("minimum_free_percent", 10))
    usage = shutil.disk_usage(path)
    free_percent = usage.free / usage.total * 100
    return free_percent >= minimum, f"Free space {free_percent:.1f}%; minimum {minimum:g}%"


OPERATIONS = {
    "http": _http_check,
    "tcp": _tcp_check,
    "tls": _tls_check,
    "disk": _disk_check,
}


def run_checks(config: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    for index, raw_check in enumerate(config.get("checks", []), start=1):
        if not isinstance(raw_check, dict):
            results.append(CheckResult(f"check-{index}", "invalid", False, "Check must be an object", 0))
            continue
        kind = str(raw_check.get("type", ""))
        name = str(raw_check.get("name") or f"{kind or 'check'}-{index}")
        operation = OPERATIONS.get(kind)
        if operation is None:
            results.append(CheckResult(name, kind or "invalid", False, f"Unsupported check type: {kind}", 0))
            continue
        results.append(_timed(name, kind, lambda item=raw_check, op=operation: op(item)))
    return results


def report_payload(results: list[CheckResult]) -> dict[str, Any]:
    passed = sum(1 for result in results if result.ok)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ok": passed == len(results) and bool(results),
        "summary": {"passed": passed, "failed": len(results) - passed, "total": len(results)},
        "checks": [result.to_dict() for result in results],
    }


def render_markdown(results: list[CheckResult]) -> str:
    payload = report_payload(results)
    summary = payload["summary"]
    lines = [
        "# Service Watch report",
        "",
        f"Status: **{'OK' if payload['ok'] else 'FAIL'}**  ",
        f"Checks: {summary['passed']} passed, {summary['failed']} failed, {summary['total']} total.",
        "",
        "| Status | Check | Type | Result | Time |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        message = result.message.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {status} | {result.name} | {result.kind} | {message} | {result.duration_ms} ms |")
    lines.append("")
    return "\n".join(lines)

