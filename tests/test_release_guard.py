from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from release_guard import ReleaseError, deploy, rollback, status


class ReleaseGuardTests(unittest.TestCase):
    def test_deploy_switch_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            target = root / "production"
            source.mkdir()
            (source / "index.html").write_text("version one", encoding="utf-8")

            first = deploy(source, target, health_file="index.html")
            (source / "index.html").write_text("version two", encoding="utf-8")
            second = deploy(source, target, health_file="index.html")

            self.assertEqual(status(target)["current"], second["release"])
            rolled_back = rollback(target)
            self.assertEqual(rolled_back["release"], first["release"])
            self.assertEqual(status(target)["current"], first["release"])

    def test_failed_healthcheck_does_not_switch_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            target = root / "production"
            source.mkdir()
            (source / "index.html").write_text("working", encoding="utf-8")
            first = deploy(source, target, health_file="index.html")
            (source / "index.html").unlink()
            (source / "broken.txt").write_text("broken", encoding="utf-8")

            with self.assertRaises(ReleaseError):
                deploy(source, target, health_file="index.html")
            self.assertEqual(status(target)["current"], first["release"])

    def test_rollback_requires_previous_release(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ReleaseError):
                rollback(Path(temp))


if __name__ == "__main__":
    unittest.main()

