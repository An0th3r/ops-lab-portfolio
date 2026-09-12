"""Verified ZIP backups with safe restore."""

from .core import BackupError, create_backup, restore_backup, verify_backup

__all__ = ["BackupError", "create_backup", "restore_backup", "verify_backup"]

