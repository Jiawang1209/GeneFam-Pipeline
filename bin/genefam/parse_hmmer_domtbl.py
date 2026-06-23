#!/usr/bin/env python3
"""Parse HMMER domtblout into GeneFam normalized TSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "species_id",
    "gene_id",
    "hmm_id",
    "hmm_length",
    "hmm_from",
    "hmm_to",
    "ali_from",
    "ali_to",
    "domain_coverage",
    "evalue",
    "bitscore",
]


def parse_domtblout(path: Path, species_id: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split()
            if len(parts) < 19:
                raise ValueError(f"domtblout line has fewer than 19 columns: {line.rstrip()}")
            hmm_length = int(parts[5])
            hmm_from = int(parts[15])
            hmm_to = int(parts[16])
            domain_coverage = (hmm_to - hmm_from + 1) / hmm_length if hmm_length > 0 else 0.0
            rows.append(
                {
                    "species_id": species_id,
                    "gene_id": parts[0],
                    "hmm_id": parts[3],
                    "hmm_length": parts[5],
                    "hmm_from": parts[15],
                    "hmm_to": parts[16],
                    "ali_from": parts[17],
                    "ali_to": parts[18],
                    "domain_coverage": f"{domain_coverage:.4f}",
                    "evalue": parts[6],
                    "bitscore": parts[7],
                }
            )
    return rows


def write_rows(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--species-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_rows(parse_domtblout(args.input, args.species_id), args.out)


if __name__ == "__main__":
    main()
