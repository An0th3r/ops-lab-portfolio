from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import BackupError, create_backup, restore_backup, verify_backup


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create, verify and safely restore ZIP backups")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create and verify a backup")
    create.add_argument("sources", nargs="+")
    create.add_argument("--destination", required=True)
    create.add_argument("--keep", type=int, default=7)
    create.add_argument("--prefix", default="backup")

    verify = sub.add_parser("verify", help="Verify manifest and SHA-256 checksums")
    verify.add_argument("archive")

    restore = sub.add_parser("restore", help="Verify and restore an archive")
    restore.add_argument("archive")
    restore.add_argument("--target", required=True)
    restore.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "create":
            archive = create_backup(args.sources, args.destination, keep=args.keep, prefix=args.prefix)
            result = {"ok": True, "archive": str(Path(archive))}
        elif args.command == "verify":
            result = verify_backup(args.archive)
        else:
            result = restore_backup(args.archive, args.target, overwrite=args.overwrite)
    except BackupError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

