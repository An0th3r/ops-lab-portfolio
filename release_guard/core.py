from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_FILE = ".release-guard.json"
RELEASES_DIR = "releases"


class ReleaseError(RuntimeError):
    """Raised when a release cannot be switched safely."""


def _read_state(target: Path) -> dict[str, Any]:
    state_path = target / STATE_FILE
    if not state_path.exists():
        return {"format": 1, "current": None, "history": []}
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("Invalid release state") from exc
    if state.get("format") != 1 or not isinstance(state.get("history"), list):
        raise ReleaseError("Unsupported release state")
    return state


def _write_state(target: Path, state: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target, delete=False) as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(target / STATE_FILE)


def _manifest(release_path: Path) -> dict[str, Any]:
    files = []
    for path in sorted(item for item in release_path.rglob("*") if item.is_file()):
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(release_path).as_posix(),
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return {"format": 1, "files": files}


def _healthy(release_path: Path, health_file: str | None) -> tuple[bool, str]:
    if not health_file:
        return True, "No health file required"
    candidate = (release_path / health_file).resolve()
    if release_path != candidate and release_path not in candidate.parents:
        return False, "Health file escapes release directory"
    if not candidate.is_file():
        return False, f"Health file missing: {health_file}"
    if candidate.stat().st_size == 0:
        return False, f"Health file is empty: {health_file}"
    return True, f"Health file present: {health_file}"


def deploy(
    source: str | Path,
    target: str | Path,
    *,
    health_file: str | None = None,
    keep: int = 5,
) -> dict[str, Any]:
    if keep < 1:
        raise ReleaseError("Retention must be at least 1")
    source_path = Path(source).resolve()
    target_path = Path(target).resolve()
    if not source_path.is_dir():
        raise ReleaseError(f"Source directory does not exist: {source_path}")
    target_path.mkdir(parents=True, exist_ok=True)
    releases_path = target_path / RELEASES_DIR
    releases_path.mkdir(exist_ok=True)

    release_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    release_path = releases_path / release_id
    shutil.copytree(source_path, release_path)
    (release_path / "release-manifest.json").write_text(
        json.dumps(_manifest(release_path), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    ok, health_message = _healthy(release_path, health_file)
    if not ok:
        shutil.rmtree(release_path)
        raise ReleaseError(health_message)

    state = _read_state(target_path)
    old_current = state.get("current")
    history = [item for item in state.get("history", []) if isinstance(item, str)]
    if isinstance(old_current, str):
        history.append(old_current)
    state = {
        "format": 1,
        "current": release_id,
        "history": history,
        "switched_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_state(target_path, state)

    protected = {release_id, *history[-(keep - 1):]} if keep > 1 else {release_id}
    for candidate in releases_path.iterdir():
        if candidate.is_dir() and candidate.name not in protected:
            shutil.rmtree(candidate)
    state["history"] = [item for item in history if (releases_path / item).is_dir()]
    _write_state(target_path, state)
    return {"ok": True, "release": release_id, "previous": old_current, "health": health_message}


def rollback(target: str | Path) -> dict[str, Any]:
    target_path = Path(target).resolve()
    state = _read_state(target_path)
    current = state.get("current")
    history = [item for item in state.get("history", []) if isinstance(item, str)]
    releases_path = target_path / RELEASES_DIR
    while history and not (releases_path / history[-1]).is_dir():
        history.pop()
    if not history:
        raise ReleaseError("No previous release available")
    previous = history.pop()
    state.update(
        {
            "current": previous,
            "history": history,
            "switched_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    _write_state(target_path, state)
    return {"ok": True, "release": previous, "rolled_back_from": current}


def status(target: str | Path) -> dict[str, Any]:
    target_path = Path(target).resolve()
    state = _read_state(target_path)
    current = state.get("current")
    release_path = target_path / RELEASES_DIR / str(current) if current else None
    return {
        "ok": bool(current and release_path and release_path.is_dir()),
        "current": current,
        "release_path": str(release_path) if release_path else None,
        "rollback_available": bool(state.get("history")),
    }

