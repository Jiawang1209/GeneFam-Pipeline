#!/usr/bin/env python3
"""Normalize duplicate type labels for retention enrichment."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["gene_id", "duplicate_type", "raw_duplicate_type"]
TYPE_ALIASES = {
    "wgd": "WGD/segmental",
    "segmental": "WGD/segmental",
    "wgd/segmental": "WGD/segmental",
    "whole_genome": "WGD/segmental",
    "whole-genome": "WGD/segmental",
    "tandem": "tandem",
    "proximal": "proximal",
    "dispersed": "dispersed",
    "singleton": "singleton",
    "single": "singleton",
}


def _normalize_type(value: str) -> str | None:
    return TYPE_ALIASES.get(value.strip().lower())


def normalize_duplicate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        gene_id = row.get("gene_id") or row.get("gene") or row.get("id")
        raw_type = row.get("duplicate_type") or row.get("type") or row.get("duplication_type")
        if not gene_id:
            raise ValueError(f"Missing gene_id column in row: {row}")
        if raw_type is None:
            raise ValueError(f"Missing duplicate type for gene {gene_id}")
        duplicate_type = _normalize_type(raw_type)
        if duplicate_type is None:
            raise ValueError(f"Unknown duplicate type for gene {gene_id}: {raw_type}")
        normalized.append({"gene_id": gene_id, "duplicate_type": duplicate_type, "raw_duplicate_type": raw_type})
    return normalized


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duplicates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(normalize_duplicate_rows(read_tsv(args.duplicates)), args.out)


if __name__ == "__main__":
    main()
