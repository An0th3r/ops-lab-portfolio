from __future__ import annotations

import argparse
import json

from .core import ReleaseError, deploy, rollback, status


def main() -> int:
    parser = argparse.ArgumentParser(description="Versioned releases with healthcheck and rollback")
    sub = parser.add_subparsers(dest="command", required=True)
    deploy_parser = sub.add_parser("deploy")
    deploy_parser.add_argument("source")
    deploy_parser.add_argument("--target", required=True)
    deploy_parser.add_argument("--health-file")
    deploy_parser.add_argument("--keep", type=int, default=5)
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--target", required=True)
    rollback_parser = sub.add_parser("rollback")
    rollback_parser.add_argument("--target", required=True)
    args = parser.parse_args()

    try:
        if args.command == "deploy":
            result = deploy(args.source, args.target, health_file=args.health_file, keep=args.keep)
        elif args.command == "rollback":
            result = rollback(args.target)
        else:
            result = status(args.target)
    except ReleaseError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

