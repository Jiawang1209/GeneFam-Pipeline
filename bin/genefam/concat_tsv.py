#!/usr/bin/env python3
"""Concatenate TSV files with a shared header."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def concat_tsv(paths: list[Path]) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    fieldnames: list[str] | None = None
    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None:
                continue
            if fieldnames is None:
                fieldnames = list(reader.fieldnames)
            elif fieldnames != list(reader.fieldnames):
                raise ValueError(f"TSV header mismatch in {path}")
            rows.extend(dict(row) for row in reader)
    return rows, fieldnames or []


def write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", required=True, nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    rows, fieldnames = concat_tsv(args.inputs)
    write_tsv(rows, fieldnames, args.out)


if __name__ == "__main__":
    main()
