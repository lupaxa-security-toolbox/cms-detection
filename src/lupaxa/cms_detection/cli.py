"""Command-line interface for CMS detection."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .api import detect_many
from .exceptions import CmsDetectionError
from .models import DetectResult
from .version import get_version


def _load_urls(value: str) -> list[str]:
    path = Path(value)
    if path.is_file():
        return [
            line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
        ]
    return [value]


def _text_line(result: DetectResult, verbose: bool) -> str:
    cms = result.cms or "unknown"
    version = result.version or ""
    confidence = f"({result.confidence})" if result.confidence else ""
    line = f"{result.url} => {cms} {version} {confidence}".rstrip()
    if result.error:
        line += f" (Error: {result.error})"
    if verbose and result.evidence:
        bits = ", ".join(f"{item.kind}={item.value}" for item in result.evidence)
        line += f" evidence: {bits}"
    return line


def _evidence_csv(result: DetectResult) -> str:
    return ";".join(f"{item.kind}:{item.value}@{item.cms}" for item in result.evidence)


def _write_output(path: str, fmt: str, results: list[DetectResult]) -> None:
    if fmt == "json":
        Path(path).write_text(
            json.dumps([asdict(item) for item in results], indent=2) + "\n",
            encoding="utf-8",
        )
        return
    if fmt == "csv":
        with Path(path).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["url", "cms", "version", "confidence", "evidence", "candidates", "error"]
            )
            for item in results:
                writer.writerow(
                    [
                        item.url,
                        item.cms or "",
                        item.version or "",
                        item.confidence or "",
                        _evidence_csv(item),
                        ";".join(item.candidates),
                        item.error,
                    ]
                )
        return
    Path(path).write_text(
        "\n".join(_text_line(item, verbose=False) for item in results) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect which CMS a website is using.")
    parser.add_argument("input", help="URL or file of URLs (one per line)")
    parser.add_argument("--active", action="store_true", help="Run broader path probes")
    parser.add_argument(
        "--format",
        "-f",
        choices=("text", "json", "csv"),
        default="text",
        help="Stdout / file format",
    )
    parser.add_argument("--output", "-o", help="Write results to this file")
    parser.add_argument("--workers", "-w", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code in (0, None):
            return 0
        if isinstance(code, int):
            return code
        return 2
    try:
        urls = _load_urls(args.input)
        if not urls:
            raise CmsDetectionError("empty input")
        results = detect_many(
            urls,
            workers=args.workers,
            active=args.active,
            delay=args.delay,
            retries=args.retries,
        )
        if args.output:
            try:
                _write_output(args.output, args.format, results)
            except OSError as exc:
                print(f"Failed to write output file: {exc}", file=sys.stderr)
                return 2
        elif args.format == "json":
            print(json.dumps([asdict(item) for item in results], indent=2))
        elif args.format == "csv":
            writer = csv.writer(sys.stdout)
            writer.writerow(
                ["url", "cms", "version", "confidence", "evidence", "candidates", "error"]
            )
            for item in results:
                writer.writerow(
                    [
                        item.url,
                        item.cms or "",
                        item.version or "",
                        item.confidence or "",
                        _evidence_csv(item),
                        ";".join(item.candidates),
                        item.error,
                    ]
                )
        else:
            for item in results:
                print(_text_line(item, verbose=args.verbose))
    except CmsDetectionError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0
