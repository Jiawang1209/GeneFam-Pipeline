#!/usr/bin/env python3
"""Subset an expression matrix to selected gene IDs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def subset_expression(rows: list[dict[str, str]], gene_ids: set[str]) -> list[dict[str, str]]:
    found = {row["gene_id"] for row in rows if row.get("gene_id") in gene_ids}
    missing = sorted(gene_ids - found)
    if missing:
        raise ValueError(f"Missing expression gene IDs: {', '.join(missing)}")
    return [row for row in rows if row.get("gene_id") in gene_ids]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else ["gene_id"]
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression", required=True, type=Path)
    parser.add_argument("--ids", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    gene_ids = {line.strip() for line in args.ids.read_text(encoding="utf-8").splitlines() if line.strip()}
    write_tsv(subset_expression(read_tsv(args.expression), gene_ids), args.out)


if __name__ == "__main__":
    main()
