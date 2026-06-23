#!/usr/bin/env python3
"""Annotate family members with WGD layer and named event pair evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "species_id",
    "gene_id",
    "duplicate_type",
    "wgd_layer",
    "event_name",
    "partner_gene",
    "ks",
    "confidence",
]


def annotate_family_wgd_events(
    family_duplicates: list[dict[str, str]],
    classified_pairs: list[dict[str, str]],
) -> list[dict[str, str]]:
    family_by_gene = {row["gene_id"]: row for row in family_duplicates}
    rows: list[dict[str, str]] = []
    for pair in classified_pairs:
        for gene_key, partner_key in (("gene_a", "gene_b"), ("gene_b", "gene_a")):
            gene_id = pair[gene_key]
            family_row = family_by_gene.get(gene_id)
            if family_row is None:
                continue
            rows.append(
                {
                    "species_id": family_row.get("species_id", ""),
                    "gene_id": gene_id,
                    "duplicate_type": family_row["duplicate_type"],
                    "wgd_layer": pair["wgd_layer"],
                    "event_name": pair.get("event_name", "unannotated") or "unannotated",
                    "partner_gene": pair[partner_key],
                    "ks": pair["ks"],
                    "confidence": pair.get("confidence", ""),
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
    parser.add_argument("--classified-pairs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(annotate_family_wgd_events(read_tsv(args.family_duplicates), read_tsv(args.classified_pairs)), args.out)


if __name__ == "__main__":
    main()
