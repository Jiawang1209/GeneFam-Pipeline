#!/usr/bin/env python3
"""Summarize feature tables into compact report-ready metrics."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


FIELDNAMES = ["feature", "metric", "group", "value"]


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _mean(values: list[float]) -> str:
    if not values:
        return "0.0000"
    return f"{sum(values) / len(values):.4f}"


def _row(feature: str, metric: str, group: str, value: str | int) -> dict[str, str]:
    return {"feature": feature, "metric": metric, "group": group, "value": str(value)}


def _domain_rows(domains: list[dict[str, str]]) -> list[dict[str, str]]:
    if not domains:
        return []
    rows = [
        _row("domain", "domain_hit_count", "all", len(domains)),
        _row("domain", "genes_with_domain", "all", len({row.get("gene_id", "") for row in domains if row.get("gene_id", "")})),
        _row(
            "domain",
            "mean_domain_coverage",
            "all",
            _mean([float(row["domain_coverage"]) for row in domains if row.get("domain_coverage", "")]),
        ),
    ]
    rows.extend(
        _row("domain", "domain_hit_count_by_species", species_id, count)
        for species_id, count in sorted(Counter(row.get("species_id", "") for row in domains).items())
        if species_id
    )
    return rows


def _motif_rows(motifs: list[dict[str, str]]) -> list[dict[str, str]]:
    if not motifs:
        return []
    return [
        _row("motif", "motif_count", "all", len(motifs)),
        _row("motif", "total_sites", "all", sum(int(row.get("sites", "0") or 0) for row in motifs)),
        _row("motif", "mean_width", "all", _mean([float(row["width"]) for row in motifs if row.get("width", "")])),
    ]


def _gene_structure_rows(gene_structures: list[dict[str, str]]) -> list[dict[str, str]]:
    if not gene_structures:
        return []
    rows = [
        _row("gene_structure", "gene_count", "all", len(gene_structures)),
        _row(
            "gene_structure",
            "mean_gene_length",
            "all",
            _mean([float(row["gene_length"]) for row in gene_structures if row.get("gene_length", "")]),
        ),
        _row(
            "gene_structure",
            "mean_exon_count",
            "all",
            _mean([float(row["exon_count"]) for row in gene_structures if row.get("exon_count", "")]),
        ),
    ]
    rows.extend(
        _row("gene_structure", "gene_count_by_species", species_id, count)
        for species_id, count in sorted(Counter(row.get("species_id", "") for row in gene_structures).items())
        if species_id
    )
    return rows


def _synteny_rows(synteny: list[dict[str, str]]) -> list[dict[str, str]]:
    if not synteny:
        return []
    return [
        _row("synteny", "syntenic_pair_count", "all", len(synteny)),
        _row("synteny", "block_count", "all", len({row.get("block_id", "") for row in synteny if row.get("block_id", "")})),
    ]


def _promoter_rows(promoters: list[dict[str, str]]) -> list[dict[str, str]]:
    if not promoters:
        return []
    return [
        _row("promoter", "promoter_count", "all", len(promoters)),
        _row(
            "promoter",
            "mean_promoter_length",
            "all",
            _mean([float(row["promoter_length"]) for row in promoters if row.get("promoter_length", "")]),
        ),
        _row(
            "promoter",
            "boundary_clipped_count",
            "all",
            sum(1 for row in promoters if row.get("boundary_clipped", "").lower() == "true"),
        ),
    ]


def summarize_feature_tables(
    domains: list[dict[str, str]] | None = None,
    motifs: list[dict[str, str]] | None = None,
    gene_structures: list[dict[str, str]] | None = None,
    synteny: list[dict[str, str]] | None = None,
    promoters: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rows.extend(_domain_rows(domains or []))
    rows.extend(_motif_rows(motifs or []))
    rows.extend(_gene_structure_rows(gene_structures or []))
    rows.extend(_synteny_rows(synteny or []))
    rows.extend(_promoter_rows(promoters or []))
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domains", default=None, type=Path)
    parser.add_argument("--motifs", default=None, type=Path)
    parser.add_argument("--gene-structures", default=None, type=Path)
    parser.add_argument("--synteny", default=None, type=Path)
    parser.add_argument("--promoters", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        summarize_feature_tables(
            domains=read_tsv(args.domains),
            motifs=read_tsv(args.motifs),
            gene_structures=read_tsv(args.gene_structures),
            synteny=read_tsv(args.synteny),
            promoters=read_tsv(args.promoters),
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
