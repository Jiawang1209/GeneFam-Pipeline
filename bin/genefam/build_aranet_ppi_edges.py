#!/usr/bin/env python3
"""Transfer Arabidopsis AraNet interactions to family genes by Arabidopsis homolog hits."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


EDGE_FIELDS = ["source", "target", "weight", "species"]
NODE_FIELDS = ["node", "species", "type", "domain"]
EVIDENCE_FIELDS = ["metric", "value", "description"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_aranet_edges(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if len(fields) < 2:
                continue
            if fields[0].lower() in {"source", "gene1", "from"}:
                continue
            rows.append(
                {
                    "source": fields[0].strip(),
                    "target": fields[1].strip(),
                    "weight": fields[2].strip() if len(fields) > 2 and fields[2].strip() else "1",
                }
            )
    return rows


def _format_weight(value: str) -> str:
    try:
        return f"{float(value):.4f}"
    except ValueError:
        return "1.0000"


def _metric_rows(metrics: dict[str, int]) -> list[dict[str, str]]:
    descriptions = {
        "family_candidate_rows": "Rows read from family_candidates.tsv",
        "mapped_family_genes": "Family genes with a non-empty best_reference_hit Arabidopsis homolog",
        "aranet_edges_read": "AraNet Arabidopsis network edges read from the configured PPI file",
        "aranet_edges_with_family_homologs": "AraNet edges whose two Arabidopsis endpoints both have selected family homologs",
        "transferred_edges": "Species-level PPI edges transferred from AraNet through best_reference_hit homolog mapping",
        "species_with_transferred_edges": "Species with at least one transferred PPI edge",
    }
    return [
        {"metric": metric, "value": str(value), "description": descriptions.get(metric, "")}
        for metric, value in metrics.items()
    ]


def build_aranet_ppi_edges(
    family_candidates: list[dict[str, str]],
    aranet_edges: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    homolog_map: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in family_candidates:
        species_id = row.get("species_id", "").strip()
        gene_id = row.get("gene_id", "").strip()
        ath_hit = row.get("best_reference_hit", "").strip()
        if species_id and gene_id and ath_hit:
            homolog_map[species_id][ath_hit].append(gene_id)

    transferred_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    aranet_edges_with_family_homologs = 0
    for aranet_edge in aranet_edges:
        ath_a = aranet_edge["source"]
        ath_b = aranet_edge["target"]
        edge_supported = False
        for species_id, species_homologs in sorted(homolog_map.items()):
            genes_a = sorted(set(species_homologs.get(ath_a, [])))
            genes_b = sorted(set(species_homologs.get(ath_b, [])))
            if not genes_a or not genes_b:
                continue
            edge_supported = True
            for gene_a in genes_a:
                for gene_b in genes_b:
                    if gene_a == gene_b:
                        continue
                    source, target = sorted([gene_a, gene_b])
                    key = (source, target, species_id)
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)
                    transferred_edges.append(
                        {
                            "source": source,
                            "target": target,
                            "weight": _format_weight(aranet_edge.get("weight", "1")),
                            "species": species_id,
                        }
                    )
        if edge_supported:
            aranet_edges_with_family_homologs += 1

    nodes_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for edge in transferred_edges:
        for node in (edge["source"], edge["target"]):
            nodes_by_key[(edge["species"], node)] = {
                "node": node,
                "species": edge["species"],
                "type": "GDSL",
                "domain": "PF00657",
            }
    metrics = {
        "family_candidate_rows": len(family_candidates),
        "mapped_family_genes": sum(len(genes) for by_hit in homolog_map.values() for genes in by_hit.values()),
        "aranet_edges_read": len(aranet_edges),
        "aranet_edges_with_family_homologs": aranet_edges_with_family_homologs,
        "transferred_edges": len(transferred_edges),
        "species_with_transferred_edges": len({edge["species"] for edge in transferred_edges}),
    }
    return {
        "edges": sorted(transferred_edges, key=lambda row: (row["species"], row["source"], row["target"])),
        "nodes": [nodes_by_key[key] for key in sorted(nodes_by_key)],
        "evidence": _metric_rows(metrics),
    }


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--aranet", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    outputs = build_aranet_ppi_edges(read_tsv(args.family_candidates), read_aranet_edges(args.aranet))
    write_tsv(outputs["edges"], args.outdir / "ppi_edges.tsv", EDGE_FIELDS)
    write_tsv(outputs["nodes"], args.outdir / "ppi_nodes.tsv", NODE_FIELDS)
    write_tsv(outputs["evidence"], args.outdir / "ppi_transfer_evidence.tsv", EVIDENCE_FIELDS)


if __name__ == "__main__":
    main()
