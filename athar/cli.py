
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .verifier import verify_task


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ATHAR AI local evidence verifier"
    )
    parser.add_argument("task_file", help="Path to task JSON")
    parser.add_argument("--out", help="Output report JSON file")
    args = parser.parse_args()

    try:
        task = json.loads(
            Path(args.task_file).read_text(encoding="utf-8")
        )
        report = verify_task(task)

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ATHAR ERROR: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(
        report, ensure_ascii=False, indent=2
    )

    if args.out:
        Path(args.out).write_text(
            rendered + "\n", encoding="utf-8"
        )

    print(rendered)

    return 0 if report["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
