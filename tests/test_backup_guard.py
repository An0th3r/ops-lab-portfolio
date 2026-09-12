from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from backup_guard import BackupError, create_backup, restore_backup, verify_backup


class BackupGuardTests(unittest.TestCase):
    def test_round_trip_preserves_files_and_verifies_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "customer-data"
            (source / "documents").mkdir(parents=True)
            (source / "database.sql").write_text("CREATE TABLE demo(id INTEGER);", encoding="utf-8")
            (source / "documents" / "invoice.txt").write_text("FV/2026/001", encoding="utf-8")

            archive = create_backup([source], root / "backups")
            result = verify_backup(archive)
            restored = restore_backup(archive, root / "restored")

            self.assertTrue(result["ok"])
            self.assertEqual(result["files"], 2)
            self.assertEqual(restored["files"], 2)
            self.assertEqual(
                (root / "restored" / "customer-data" / "documents" / "invoice.txt").read_text(encoding="utf-8"),
                "FV/2026/001",
            )

    def test_retention_keeps_only_requested_number(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "data.txt"
            source.write_text("one", encoding="utf-8")
            for value in ("one", "two", "three"):
                source.write_text(value, encoding="utf-8")
                create_backup([source], root / "backups", keep=2)
            self.assertEqual(len(list((root / "backups").glob("backup-*.zip"))), 2)

    def test_unsafe_archive_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "unsafe.zip"
            data = b"do not extract"
            import hashlib

            manifest = {
                "format": 1,
                "created_at": "2026-01-01T00:00:00+00:00",
                "files": [{"path": "../escape.txt", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}],
            }
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape.txt", data)
                archive.writestr("backup-manifest.json", json.dumps(manifest))
            with self.assertRaises(BackupError):
                verify_backup(archive_path)


if __name__ == "__main__":
    unittest.main()

