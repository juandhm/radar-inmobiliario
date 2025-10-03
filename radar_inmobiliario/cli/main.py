"""Command Line Interface for Radar Inmobiliario ETL.

Example:
    python -m radar_inmobiliario.cli run --platform ciencuadras \
        --input ./ciencuadras/ciencuadras.json \
        --output ./outputs/ciencuadras
"""

from __future__ import annotations

import argparse
import logging
from typing import List, Sequence

from ..core.logging_config import configure_logging
from ..core.pipeline import Pipeline
from ..core.registry import create_default_registry
from ..loaders.csv_loader import CsvLoader
from ..loaders.json_loader import JsonLoader


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Radar Inmobiliario ETL")

    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run ETL for a platform")
    run.add_argument("--platform", required=True, help="Platform name (e.g., ciencuadras)")
    run.add_argument("--input", required=True, help="Input path to raw JSON")
    run.add_argument(
        "--output",
        required=True,
        help="Output path stem without extension (e.g., ./outputs/ciencuadras)",
    )
    run.add_argument(
        "--outputs",
        nargs="+",
        choices=["csv", "json"],
        default=["csv", "json"],
        help="Output artifacts to generate",
    )
    run.add_argument("--log-level", default="INFO", help="Logging level")

    run_multi = sub.add_parser("run-multi", help="Run ETL for multiple platforms and consolidate outputs")
    run_multi.add_argument(
        "--job",
        action="append",
        required=True,
        help="Job spec in the form platform=input_path (e.g., ciencuadras=./ciencuadras/ciencuadras.json)",
    )
    run_multi.add_argument(
        "--output",
        required=True,
        help="Output path stem without extension (consolidated)",
    )
    run_multi.add_argument(
        "--outputs",
        nargs="+",
        choices=["csv", "json"],
        default=["csv", "json"],
        help="Output artifacts to generate (consolidated)",
    )
    run_multi.add_argument("--log-level", default="INFO", help="Logging level")
    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO))

    registry = create_default_registry()
    extractor, transformer = registry.resolve(args.platform)

    loaders = []  # type: List
    if "json" in args.outputs:
        loaders.append(JsonLoader())
    if "csv" in args.outputs:
        loaders.append(CsvLoader())

    pipeline = Pipeline(extractor, transformer, loaders)
    artifacts = pipeline.run(args.input, args.output)
    logging.getLogger(__name__).info("Artifacts generated: %s", ", ".join(artifacts))
    return 0


def _cmd_run_multi(args: argparse.Namespace) -> int:
    configure_logging(getattr(logging, args.log_level.upper(), logging.INFO))
    log = logging.getLogger(__name__)

    registry = create_default_registry()

    # Parse jobs platform=input_path
    jobs: List[tuple[str, str]] = []
    for spec in args.job:
        if "=" not in spec:
            raise SystemExit(f"Invalid job spec: {spec}. Expected platform=input_path")
        platform, input_path = spec.split("=", 1)
        platform = platform.strip()
        input_path = input_path.strip()
        jobs.append((platform, input_path))

    # Collect standardized items
    all_items = []  # type: List
    for platform, input_path in jobs:
        extractor, transformer = registry.resolve(platform)
        pipeline = Pipeline(extractor, transformer, loaders=[])
        items = pipeline.process_only(input_path)
        all_items.extend(items)
        log.info("Processed %s items for platform %s", len(items), platform)

    # Write consolidated outputs
    artifacts: List[str] = []
    if "json" in args.outputs:
        from ..core.io import write_json
        from ..core.schema import project_listing_to_row
        artifacts.append(
            write_json(
                f"{args.output}_consolidated.json",
                [project_listing_to_row(i) for i in all_items],
            )
        )
    if "csv" in args.outputs:
        import csv
        from ..core.schema import HEADERS, project_listing_to_row
        fieldnames = list(HEADERS)
        path = f"{args.output}_consolidated.csv"
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, item in enumerate(all_items, 1):
                projected = project_listing_to_row(item)
                row = {k: ("" if v is None else v) for k, v in projected.items()}
                if "#" in fieldnames:
                    row["#"] = idx
                writer.writerow(row)
        artifacts.append(path)

    logging.getLogger(__name__).info("Consolidated artifacts generated: %s", ", ".join(artifacts))
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "run":
        return _cmd_run(args)
    if args.command == "run-multi":
        return _cmd_run_multi(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


