#!/usr/bin/env python3
"""Build circlize chromosome and link tables from MCScanX syntenic pairs."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


CHROMOSOME_FIELDNAMES = ["chr_id", "species_id", "seqid", "start", "end", "gene_count"]
LINK_FIELDNAMES = [
    "block_id",
    "gene_a",
    "gene_a_chr",
    "gene_a_start",
    "gene_a_end",
    "gene_b",
    "gene_b_chr",
    "gene_b_start",
    "gene_b_end",
    "pair_evalue",
]
SKIPPED_FIELDNAMES = ["block_id", "gene_a", "gene_b", "reason"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _chr_id(row: dict[str, str]) -> str:
    return f"{row['species_id']}|{row['seqid']}"


def _coordinate_by_gene(locations: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["gene_id"]: row for row in locations}


def _chromosome_rows(locations: list[dict[str, str]]) -> list[dict[str, str]]:
    max_end_by_chr: dict[str, int] = defaultdict(int)
    gene_count_by_chr: dict[str, int] = defaultdict(int)
    metadata_by_chr: dict[str, tuple[str, str]] = {}
    for row in locations:
        chr_id = _chr_id(row)
        max_end_by_chr[chr_id] = max(max_end_by_chr[chr_id], int(row["end"]))
        gene_count_by_chr[chr_id] += 1
        metadata_by_chr[chr_id] = (row["species_id"], row["seqid"])

    rows: list[dict[str, str]] = []
    for chr_id in sorted(max_end_by_chr):
        species_id, seqid = metadata_by_chr[chr_id]
        rows.append(
            {
                "chr_id": chr_id,
                "species_id": species_id,
                "seqid": seqid,
                "start": "1",
                "end": str(max_end_by_chr[chr_id]),
                "gene_count": str(gene_count_by_chr[chr_id]),
            }
        )
    return rows


def build_circlize_inputs(
    locations: list[dict[str, str]], syntenic_pairs: list[dict[str, str]]
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    coordinates = _coordinate_by_gene(locations)
    links: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for pair in syntenic_pairs:
        gene_a = pair["gene_a"]
        gene_b = pair["gene_b"]
        coord_a = coordinates.get(gene_a)
        coord_b = coordinates.get(gene_b)
        reason = ""
        if coord_a is None:
            reason = "missing_gene_a_coordinate"
        elif coord_b is None:
            reason = "missing_gene_b_coordinate"
        if reason:
            skipped.append(
                {
                    "block_id": pair.get("block_id", ""),
                    "gene_a": gene_a,
                    "gene_b": gene_b,
                    "reason": reason,
                }
            )
            continue
        links.append(
            {
                "block_id": pair.get("block_id", ""),
                "gene_a": gene_a,
                "gene_a_chr": _chr_id(coord_a),
                "gene_a_start": coord_a["start"],
                "gene_a_end": coord_a["end"],
                "gene_b": gene_b,
                "gene_b_chr": _chr_id(coord_b),
                "gene_b_start": coord_b["start"],
                "gene_b_end": coord_b["end"],
                "pair_evalue": pair.get("pair_evalue", ""),
            }
        )
    return _chromosome_rows(locations), links, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromosome-locations", required=True, type=Path)
    parser.add_argument("--syntenic-pairs", required=True, type=Path)
    parser.add_argument("--out-chromosomes", required=True, type=Path)
    parser.add_argument("--out-links", required=True, type=Path)
    parser.add_argument("--out-skipped", required=True, type=Path)
    args = parser.parse_args()
    chromosomes, links, skipped = build_circlize_inputs(
        read_tsv(args.chromosome_locations),
        read_tsv(args.syntenic_pairs),
    )
    write_tsv(chromosomes, args.out_chromosomes, CHROMOSOME_FIELDNAMES)
    write_tsv(links, args.out_links, LINK_FIELDNAMES)
    write_tsv(skipped, args.out_skipped, SKIPPED_FIELDNAMES)


if __name__ == "__main__":
    main()
