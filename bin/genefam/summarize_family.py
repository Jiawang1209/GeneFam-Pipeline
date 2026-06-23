#!/usr/bin/env python3
"""Summarize final gene family candidate rows."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


FIELDNAMES = ["species_id", "member_count", "hmmer_count", "diamond_count", "intersection_count"]


def summarize_candidates(rows: list[dict[str, str]]) -> list[dict[str, int | str]]:
    by_species: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_species[row["species_id"]].append(row)

    summary: list[dict[str, int | str]] = []
    for species_id in sorted(by_species):
        species_rows = by_species[species_id]
        hmmer_count = 0
        diamond_count = 0
        intersection_count = 0
        for row in species_rows:
            sources = set(filter(None, row.get("evidence_sources", "").split(",")))
            if "hmmer" in sources:
                hmmer_count += 1
            if "diamond" in sources:
                diamond_count += 1
            if {"hmmer", "diamond"}.issubset(sources):
                intersection_count += 1
        summary.append(
            {
                "species_id": species_id,
                "member_count": len(species_rows),
                "hmmer_count": hmmer_count,
                "diamond_count": diamond_count,
                "intersection_count": intersection_count,
            }
        )
    return summary


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, int | str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(summarize_candidates(read_tsv(args.candidates)), args.out)


if __name__ == "__main__":
    main()
