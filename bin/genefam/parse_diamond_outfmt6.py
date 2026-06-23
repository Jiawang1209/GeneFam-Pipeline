#!/usr/bin/env python3
"""Parse DIAMOND/BLAST outfmt6 into normalized evidence rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["species_id", "gene_id", "reference_hit", "evalue", "bitscore"]


def _score_key(row: dict[str, str]) -> tuple[float, float]:
    return float(row["evalue"]), -float(row["bitscore"])


def parse_outfmt6(path: Path, species_id: str) -> list[dict[str, str]]:
    """Return the best reference hit per target gene from outfmt6 rows."""

    best_by_gene: dict[str, dict[str, str]] = {}
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if not fields or fields[0].startswith("#"):
                continue
            if len(fields) < 12:
                raise ValueError(f"Expected at least 12 outfmt6 columns in {path}: {fields}")
            reference_hit = fields[0]
            gene_id = fields[1]
            row = {
                "species_id": species_id,
                "gene_id": gene_id,
                "reference_hit": reference_hit,
                "evalue": fields[10],
                "bitscore": fields[11],
            }
            current = best_by_gene.get(gene_id)
            if current is None or _score_key(row) < _score_key(current):
                best_by_gene[gene_id] = row
    return [best_by_gene[gene_id] for gene_id in sorted(best_by_gene)]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outfmt6", required=True, type=Path)
    parser.add_argument("--species-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(parse_outfmt6(args.outfmt6, args.species_id), args.out)


if __name__ == "__main__":
    main()
