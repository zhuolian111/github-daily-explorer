from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from github_daily_explorer.app import run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Discover and email today's GitHub recommendations")
    parser.add_argument("--dry-run", action="store_true", help="generate files without sending email or changing history")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run(dry_run=args.dry_run, root=Path(__file__).resolve().parent)
    except Exception as exc:  # concise CLI boundary; internal exceptions preserve their cause
        logging.error("执行失败：%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

