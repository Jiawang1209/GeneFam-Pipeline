#!/usr/bin/env python3
"""Compute duplicate-type retention enrichment for a gene family."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path


FIELDNAMES = [
    "duplicate_type",
    "family_count",
    "family_total",
    "background_count",
    "background_total",
    "fold_enrichment",
    "p_value",
]


def _hypergeom_right_tail(successes: int, population_successes: int, draws: int, population_size: int) -> float:
    max_successes = min(population_successes, draws)
    denominator = math.comb(population_size, draws)
    probability = 0.0
    for observed in range(successes, max_successes + 1):
        failures_drawn = draws - observed
        population_failures = population_size - population_successes
        if failures_drawn < 0 or failures_drawn > population_failures:
            continue
        probability += math.comb(population_successes, observed) * math.comb(population_failures, failures_drawn) / denominator
    return min(probability, 1.0)


def compute_enrichment(
    family_rows: list[dict[str, str]],
    background_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    family_counts = Counter(row["duplicate_type"] for row in family_rows)
    background_counts = Counter(row["duplicate_type"] for row in background_rows)
    family_total = len(family_rows)
    background_total = len(background_rows)

    rows: list[dict[str, str]] = []
    for duplicate_type in sorted(background_counts):
        family_count = family_counts.get(duplicate_type, 0)
        background_count = background_counts[duplicate_type]
        family_rate = family_count / family_total if family_total else 0.0
        background_rate = background_count / background_total if background_total else 0.0
        fold_enrichment = family_rate / background_rate if background_rate else 0.0
        p_value = (
            _hypergeom_right_tail(family_count, background_count, family_total, background_total)
            if family_total and background_total
            else 1.0
        )
        rows.append(
            {
                "duplicate_type": duplicate_type,
                "family_count": str(family_count),
                "family_total": str(family_total),
                "background_count": str(background_count),
                "background_total": str(background_total),
                "fold_enrichment": f"{fold_enrichment:.4f}",
                "p_value": f"{p_value:.6g}",
            }
        )
    return rows


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
    parser.add_argument("--family-duplicates", required=True, type=Path)
    parser.add_argument("--background-duplicates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(compute_enrichment(read_tsv(args.family_duplicates), read_tsv(args.background_duplicates)), args.out)


if __name__ == "__main__":
    main()
