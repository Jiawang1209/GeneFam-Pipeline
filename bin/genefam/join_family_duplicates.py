#!/usr/bin/env python3
"""Join family members with normalized duplicate type classifications."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["species_id", "gene_id", "duplicate_type", "raw_duplicate_type"]


def join_family_duplicates(
    family_rows: list[dict[str, str]],
    duplicate_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    duplicate_by_gene: dict[str, dict[str, str]] = {}
    duplicate_gene_ids: set[str] = set()
    for row in duplicate_rows:
        gene_id = row.get("gene_id")
        if not gene_id:
            raise ValueError(f"Missing gene_id column in duplicate row: {row}")
        if gene_id in duplicate_by_gene:
            duplicate_gene_ids.add(gene_id)
        duplicate_by_gene[gene_id] = row

    if duplicate_gene_ids:
        genes = ", ".join(sorted(duplicate_gene_ids))
        raise ValueError(f"Duplicate duplicate-classification rows for genes: {genes}")

    joined: list[dict[str, str]] = []
    missing: list[str] = []
    for row in family_rows:
        species_id = row.get("species_id", "")
        gene_id = row.get("gene_id")
        if not gene_id:
            raise ValueError(f"Missing gene_id column in family row: {row}")
        duplicate_row = duplicate_by_gene.get(gene_id)
        if duplicate_row is None:
            missing.append(gene_id)
            continue
        joined.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "duplicate_type": duplicate_row["duplicate_type"],
                "raw_duplicate_type": duplicate_row.get("raw_duplicate_type", duplicate_row["duplicate_type"]),
            }
        )

    if missing:
        genes = ", ".join(sorted(missing))
        raise ValueError(f"Missing duplicate classification for family genes: {genes}")
    return joined


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
    parser.add_argument("--family-members", required=True, type=Path)
    parser.add_argument("--duplicates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(join_family_duplicates(read_tsv(args.family_members), read_tsv(args.duplicates)), args.out)


if __name__ == "__main__":
    main()
