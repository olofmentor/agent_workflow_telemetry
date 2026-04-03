"""Run: ``python -m init`` from the repo root (loads ``.env``, then UC + experiment + OTEL headers)."""

import argparse
import logging

from init.databricks import init_and_connect, load_env_from_project_root


def main() -> int:
    parser = argparse.ArgumentParser(description="Databricks MLflow + UC trace bootstrap")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run MLflow ensure steps but only print planned os.environ updates (no apply).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Warnings/errors only (uses logging).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    load_env_from_project_root()
    try:
        init_and_connect(verbose=not args.quiet, dry_run=args.dry_run)
        return 0
    except Exception as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
