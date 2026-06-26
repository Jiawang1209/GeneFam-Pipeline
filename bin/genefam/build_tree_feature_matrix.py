#!/usr/bin/env python3
"""Build a tree-ordered gene feature matrix for combined tree/feature plots."""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


FIELDNAMES = [
    "tree_order",
    "species_id",
    "gene_id",
    "gene_length",
    "exon_count",
    "cds_count",
    "domain_count",
    "best_domain_coverage",
    "motif_catalog_count",
    "motif_total_sites",
    "motif_mean_width",
]
NEWICK_TOKEN_RE = re.compile(r"([A-Za-z0-9_.|+-]+)(?=[:),;])")


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tree_leaves(tree_text: str) -> list[str]:
    leaves: list[str] = []
    for token in NEWICK_TOKEN_RE.findall(tree_text):
        if token.replace(".", "", 1).isdigit():
            continue
        if token not in leaves:
            leaves.append(token)
    return leaves


def _mean(values: list[float]) -> str:
    if not values:
        return "0.0000"
    return f"{sum(values) / len(values):.4f}"


def _safe_int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _safe_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _motif_summary(motifs: list[dict[str, str]]) -> tuple[str, str, str]:
    widths = [_safe_float(row.get("width", "")) for row in motifs]
    sites = [_safe_int(row.get("sites", "")) for row in motifs]
    return (
        str(len(motifs)),
        str(sum(sites)),
        _mean([value for value in widths if value is not None]),
    )


def build_tree_feature_matrix(
    *,
    tree_text: str,
    family_candidates: list[dict[str, str]],
    motifs: list[dict[str, str]] | None = None,
    gene_structures: list[dict[str, str]] | None = None,
    domains: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    species_by_gene = {row.get("gene_id", ""): row.get("species_id", "") for row in family_candidates if row.get("gene_id")}
    tree_order = [gene_id for gene_id in tree_leaves(tree_text) if gene_id in species_by_gene]
    tree_order.extend(gene_id for gene_id in sorted(species_by_gene) if gene_id not in tree_order)

    structures_by_gene = {row.get("gene_id", ""): row for row in gene_structures or [] if row.get("gene_id")}
    domain_counts: Counter[str] = Counter()
    domain_coverages: dict[str, list[float]] = defaultdict(list)
    for row in domains or []:
        gene_id = row.get("gene_id", "")
        if not gene_id:
            continue
        domain_counts[gene_id] += 1
        coverage = _safe_float(row.get("domain_coverage", ""))
        if coverage is not None:
            domain_coverages[gene_id].append(coverage)

    motif_catalog_count, motif_total_sites, motif_mean_width = _motif_summary(motifs or [])
    rows: list[dict[str, str]] = []
    for index, gene_id in enumerate(tree_order, start=1):
        structure = structures_by_gene.get(gene_id, {})
        best_domain_coverage = max(domain_coverages.get(gene_id, [0.0]))
        rows.append(
            {
                "tree_order": str(index),
                "species_id": species_by_gene.get(gene_id, ""),
                "gene_id": gene_id,
                "gene_length": str(_safe_int(structure.get("gene_length", ""))),
                "exon_count": str(_safe_int(structure.get("exon_count", ""))),
                "cds_count": str(_safe_int(structure.get("cds_count", ""))),
                "domain_count": str(domain_counts.get(gene_id, 0)),
                "best_domain_coverage": f"{best_domain_coverage:.4f}",
                "motif_catalog_count": motif_catalog_count,
                "motif_total_sites": motif_total_sites,
                "motif_mean_width": motif_mean_width,
            }
        )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", required=True, type=Path)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--motifs", required=True, type=Path)
    parser.add_argument("--gene-structures", required=True, type=Path)
    parser.add_argument("--domains", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        build_tree_feature_matrix(
            tree_text=args.tree.read_text(encoding="utf-8"),
            family_candidates=read_tsv(args.family_candidates),
            motifs=read_tsv(args.motifs),
            gene_structures=read_tsv(args.gene_structures),
            domains=read_tsv(args.domains),
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
