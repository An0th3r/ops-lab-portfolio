from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable


MANIFEST_NAME = "backup-manifest.json"


class BackupError(RuntimeError):
    """Raised when a backup cannot be trusted or safely restored."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive_entries(sources: Iterable[Path]) -> list[tuple[Path, str]]:
    entries: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for raw_source in sources:
        source = raw_source.resolve()
        if not source.exists():
            raise BackupError(f"Source does not exist: {source}")
        base = source.name
        files = [source] if source.is_file() else sorted(p for p in source.rglob("*") if p.is_file())
        for file_path in files:
            relative = file_path.name if source.is_file() else file_path.relative_to(source).as_posix()
            archive_name = PurePosixPath(base, relative).as_posix()
            if archive_name in seen:
                raise BackupError(f"Duplicate archive path: {archive_name}")
            seen.add(archive_name)
            entries.append((file_path, archive_name))
    return entries


def create_backup(
    sources: Iterable[str | Path],
    destination: str | Path,
    *,
    keep: int = 7,
    prefix: str = "backup",
) -> Path:
    if keep < 1:
        raise BackupError("Retention must be at least 1")
    destination_path = Path(destination).resolve()
    destination_path.mkdir(parents=True, exist_ok=True)
    source_paths = [Path(item) for item in sources]
    entries = _archive_entries(source_paths)
    if not entries:
        raise BackupError("Backup source contains no files")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    final_path = destination_path / f"{prefix}-{stamp}.zip"
    manifest_files: list[dict[str, object]] = []

    with tempfile.NamedTemporaryFile(
        prefix=f".{prefix}-", suffix=".tmp", dir=destination_path, delete=False
    ) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path, archive_name in entries:
                data = file_path.read_bytes()
                archive.writestr(archive_name, data)
                manifest_files.append(
                    {"path": archive_name, "size": len(data), "sha256": _sha256_bytes(data)}
                )
            manifest = {
                "format": 1,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "files": manifest_files,
            }
            archive.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True))
        temp_path.replace(final_path)
    finally:
        temp_path.unlink(missing_ok=True)

    verify_backup(final_path)
    archives = sorted(destination_path.glob(f"{prefix}-*.zip"), key=lambda item: item.stat().st_mtime, reverse=True)
    for expired in archives[keep:]:
        expired.unlink()
    return final_path


def _load_manifest(archive: zipfile.ZipFile) -> dict[str, object]:
    try:
        raw = archive.read(MANIFEST_NAME)
        manifest = json.loads(raw.decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackupError("Missing or invalid backup manifest") from exc
    if manifest.get("format") != 1 or not isinstance(manifest.get("files"), list):
        raise BackupError("Unsupported backup manifest")
    return manifest


def _safe_relative_path(name: str) -> Path:
    pure = PurePosixPath(name)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts:
        raise BackupError(f"Unsafe archive path: {name}")
    if pure.parts[0].endswith(":") or "\\" in name:
        raise BackupError(f"Unsafe archive path: {name}")
    return Path(*pure.parts)


def verify_backup(archive_path: str | Path) -> dict[str, object]:
    path = Path(archive_path).resolve()
    if not path.is_file():
        raise BackupError(f"Backup does not exist: {path}")
    try:
        with zipfile.ZipFile(path, "r") as archive:
            manifest = _load_manifest(archive)
            archive_names = set(archive.namelist())
            expected_names: set[str] = set()
            for record in manifest["files"]:
                if not isinstance(record, dict):
                    raise BackupError("Invalid file record in manifest")
                name = str(record.get("path", ""))
                _safe_relative_path(name)
                if name in expected_names:
                    raise BackupError(f"Duplicate manifest path: {name}")
                expected_names.add(name)
                if name not in archive_names:
                    raise BackupError(f"File missing from archive: {name}")
                data = archive.read(name)
                if len(data) != record.get("size") or _sha256_bytes(data) != record.get("sha256"):
                    raise BackupError(f"Checksum mismatch: {name}")
            unexpected = archive_names - expected_names - {MANIFEST_NAME}
            if unexpected:
                raise BackupError(f"Untracked files in archive: {', '.join(sorted(unexpected))}")
            return {"ok": True, "archive": str(path), "files": len(expected_names)}
    except zipfile.BadZipFile as exc:
        raise BackupError("Invalid ZIP archive") from exc


def restore_backup(
    archive_path: str | Path,
    target: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, object]:
    verification = verify_backup(archive_path)
    target_path = Path(target).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    restored = 0

    with zipfile.ZipFile(Path(archive_path).resolve(), "r") as archive:
        manifest = _load_manifest(archive)
        for record in manifest["files"]:
            name = str(record["path"])
            output = (target_path / _safe_relative_path(name)).resolve()
            if target_path != output and target_path not in output.parents:
                raise BackupError(f"Restore path escapes target: {name}")
            if output.exists() and not overwrite:
                raise BackupError(f"Restore target already exists: {output}")
            output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name, "r") as source, output.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            restored += 1
    return {"ok": True, "target": str(target_path), "files": restored, "verified": verification["ok"]}

