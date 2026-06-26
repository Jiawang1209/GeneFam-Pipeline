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
DENSITY_FIELDNAMES = ["chr_id", "window_start", "window_end", "linked_gene_count", "link_count"]
DUPLICATE_TRACK_FIELDNAMES = ["chr_id", "gene_id", "start", "end", "duplicate_type", "link_count"]


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


def _duplicate_type_by_gene(duplicate_types: list[dict[str, str]] | None) -> dict[str, str]:
    if not duplicate_types:
        return {}
    return {row["gene_id"]: row.get("duplicate_type", "unknown") or "unknown" for row in duplicate_types}


def _density_rows(
    chromosomes: list[dict[str, str]],
    linked_genes: dict[str, dict[str, str]],
    link_count_by_gene: dict[str, int],
    window_size: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for chromosome in chromosomes:
        chr_id = chromosome["chr_id"]
        chromosome_end = int(chromosome["end"])
        for window_start in range(1, chromosome_end + 1, window_size):
            window_end = min(window_start + window_size - 1, chromosome_end)
            genes_in_window = [
                gene_id
                for gene_id, coord in linked_genes.items()
                if _chr_id(coord) == chr_id
                and int(coord["start"]) <= window_end
                and int(coord["end"]) >= window_start
            ]
            if not genes_in_window:
                continue
            rows.append(
                {
                    "chr_id": chr_id,
                    "window_start": str(window_start),
                    "window_end": str(window_end),
                    "linked_gene_count": str(len(genes_in_window)),
                    "link_count": str(sum(link_count_by_gene[gene_id] for gene_id in genes_in_window)),
                }
            )
    return rows


def _duplicate_track_rows(
    linked_genes: dict[str, dict[str, str]],
    link_count_by_gene: dict[str, int],
    duplicate_types: dict[str, str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for gene_id in sorted(linked_genes, key=lambda value: (_chr_id(linked_genes[value]), int(linked_genes[value]["start"]), value)):
        coord = linked_genes[gene_id]
        rows.append(
            {
                "chr_id": _chr_id(coord),
                "gene_id": gene_id,
                "start": coord["start"],
                "end": coord["end"],
                "duplicate_type": duplicate_types.get(gene_id, "syntenic"),
                "link_count": str(link_count_by_gene[gene_id]),
            }
        )
    return rows


def build_circlize_inputs(
    locations: list[dict[str, str]],
    syntenic_pairs: list[dict[str, str]],
    duplicate_types: list[dict[str, str]] | None = None,
    density_window_size: int = 1_000_000,
    include_tracks: bool = False,
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]] | tuple[
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
    list[dict[str, str]],
]:
    coordinates = _coordinate_by_gene(locations)
    links: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    linked_genes: dict[str, dict[str, str]] = {}
    link_count_by_gene: dict[str, int] = defaultdict(int)
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
        linked_genes[gene_a] = coord_a
        linked_genes[gene_b] = coord_b
        link_count_by_gene[gene_a] += 1
        link_count_by_gene[gene_b] += 1
    chromosomes = _chromosome_rows(locations)
    if not include_tracks:
        return chromosomes, links, skipped
    density = _density_rows(chromosomes, linked_genes, link_count_by_gene, density_window_size)
    duplicate_tracks = _duplicate_track_rows(linked_genes, link_count_by_gene, _duplicate_type_by_gene(duplicate_types))
    return chromosomes, links, skipped, density, duplicate_tracks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromosome-locations", required=True, type=Path)
    parser.add_argument("--syntenic-pairs", required=True, type=Path)
    parser.add_argument("--out-chromosomes", required=True, type=Path)
    parser.add_argument("--out-links", required=True, type=Path)
    parser.add_argument("--out-skipped", required=True, type=Path)
    parser.add_argument("--duplicate-types", default=None, type=Path)
    parser.add_argument("--density-window-size", default=1_000_000, type=int)
    parser.add_argument("--out-density", default=None, type=Path)
    parser.add_argument("--out-duplicate-tracks", default=None, type=Path)
    args = parser.parse_args()
    include_tracks = args.out_density is not None or args.out_duplicate_tracks is not None
    result = build_circlize_inputs(
        read_tsv(args.chromosome_locations),
        read_tsv(args.syntenic_pairs),
        duplicate_types=read_tsv(args.duplicate_types) if args.duplicate_types else None,
        density_window_size=args.density_window_size,
        include_tracks=include_tracks,
    )
    if include_tracks:
        chromosomes, links, skipped, density, duplicate_tracks = result
    else:
        chromosomes, links, skipped = result
        density = []
        duplicate_tracks = []
    write_tsv(chromosomes, args.out_chromosomes, CHROMOSOME_FIELDNAMES)
    write_tsv(links, args.out_links, LINK_FIELDNAMES)
    write_tsv(skipped, args.out_skipped, SKIPPED_FIELDNAMES)
    if args.out_density:
        write_tsv(density, args.out_density, DENSITY_FIELDNAMES)
    if args.out_duplicate_tracks:
        write_tsv(duplicate_tracks, args.out_duplicate_tracks, DUPLICATE_TRACK_FIELDNAMES)


if __name__ == "__main__":
    main()
