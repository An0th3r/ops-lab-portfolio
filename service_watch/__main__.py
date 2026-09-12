from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import load_config, render_markdown, report_payload, run_checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check HTTP, TCP, TLS and disk health")
    parser.add_argument("--config", required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        results = run_checks(load_config(args.config))
        rendered = (
            render_markdown(results)
            if args.format == "markdown"
            else json.dumps(report_payload(results), ensure_ascii=False, indent=2)
        )
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
    print(rendered)
    return 0 if results and all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

