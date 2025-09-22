"""Utility script to copy a CSV file with robust error handling."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


MAX_WARNINGS_TO_SHOW = 20


class CSVFormatError(RuntimeError):
    """Raised when the source file does not conform to a tabular CSV layout."""


def parse_arguments(cli_args: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a CSV file to a new location while handling common file-system "
            "and data issues."
        )
    )
    parser.add_argument(
        "--source",
        default="source_data.csv",
        help="Path to the input CSV file (default: %(default)s)",
    )
    parser.add_argument(
        "--destination",
        default="source_data_copy.csv",
        help="Where to write the copied CSV (default: %(default)s)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing destination file.",
    )
    return parser.parse_args(list(cli_args) if cli_args is not None else None)


def _detect_csv_dialect(sample: str) -> type[csv.Dialect]:
    try:
        dialect = csv.Sniffer().sniff(sample)
        delimiter = getattr(dialect, "delimiter", ",")
        if not delimiter or delimiter in {"\n", "\r"}:
            raise csv.Error("Sniffer produced an invalid delimiter")
        return dialect
    except csv.Error:
        return type(csv.excel())


def _normalize_row(
    row: List[str],
    column_count: int,
    row_number: int,
) -> Tuple[List[str], str | None]:
    """Normalize a CSV row to the expected column count.

    Returns the adjusted row and a warning message if a correction was applied.
    """
    if len(row) == column_count:
        return row, None
    if len(row) > column_count:
        candidate = list(row)
        removed = 0
        while len(candidate) > column_count and "" in candidate:
            candidate.remove("")
            removed += 1
        if len(candidate) == column_count:
            return candidate, (
                f"Line {row_number}: removed {removed} empty placeholder column(s) to "
                f"match header layout."
            )
        extras = candidate[column_count:]
        raise CSVFormatError(
            f"Inconsistent column count at line {row_number}: expected {column_count} "
            f"but found {len(row)}. Extra data: {extras}"
        )
    # len(row) < column_count
    padded_row = row + [""] * (column_count - len(row))
    return padded_row, (
        f"Line {row_number}: padded missing values with empty strings to match the "
        f"expected {column_count} columns."
    )


def read_csv_rows(source_path: Path) -> Tuple[List[List[str]], List[str], int]:
    if not source_path.exists():
        raise FileNotFoundError(source_path)
    warnings: List[str] = []
    suppressed = 0
    try:
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            dialect = _detect_csv_dialect(sample)
            try:
                reader = csv.reader(handle, dialect=dialect)
                rows = [row for row in reader]
            except ValueError:
                handle.seek(0)
                reader = csv.reader(handle, dialect=csv.excel)
                rows = [row for row in reader]
    except UnicodeDecodeError as exc:
        raise CSVFormatError("Unable to decode file as UTF-8 encoded CSV.") from exc
    if not rows:
        return [], warnings, suppressed
    column_count = len(rows[0])
    if column_count == 0:
        raise CSVFormatError("The CSV file appears to have no columns.")
    normalized_rows = [rows[0]]
    for index, row in enumerate(rows[1:], start=2):
        normalized_row, warning = _normalize_row(row, column_count, index)
        normalized_rows.append(normalized_row)
        if warning:
            if len(warnings) < MAX_WARNINGS_TO_SHOW:
                warnings.append(warning)
            else:
                suppressed += 1
    return normalized_rows, warnings, suppressed


def write_csv_rows(
    destination_path: Path, rows: List[List[str]], overwrite: bool
) -> None:
    if destination_path.exists() and not overwrite:
        raise FileExistsError(
            f"Destination file '{destination_path}' already exists. "
            "Pass --overwrite to replace it."
        )
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow(row)


def main(cli_args: Iterable[str] | None = None) -> int:
    args = parse_arguments(cli_args)
    source_path = Path(args.source).expanduser().resolve()
    destination_path = Path(args.destination).expanduser().resolve()
    try:
        rows, warnings, suppressed = read_csv_rows(source_path)
        for message in warnings:
            print(f"Warning: {message}", file=sys.stderr)
        if suppressed:
            print(
                f"Warning: {suppressed} additional formatting issues were corrected "
                "(not shown).",
                file=sys.stderr,
            )
        write_csv_rows(destination_path, rows, args.overwrite)
    except FileNotFoundError:
        print(f"Error: Could not find source file '{source_path}'.", file=sys.stderr)
        return 1
    except CSVFormatError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except PermissionError as exc:
        print(
            "Error: Permission denied while accessing the file system. "
            "Check read/write rights and read-only attributes.",
            file=sys.stderr,
        )
        if exc.filename:
            print(f"Details: {exc.filename}", file=sys.stderr)
        return 3
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 4
    except OSError as exc:
        print(f"Unexpected OS error: {exc}", file=sys.stderr)
        return 5
    else:
        print(f"Successfully copied '{source_path}' to '{destination_path}'.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
