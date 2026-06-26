#!/usr/bin/env python3
"""Normalize PPI edges and build node/hub tables for ggNetView plots."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


EDGE_FIELDS = ["source", "target", "weight", "species"]
NODE_FIELDS = ["node", "species", "type", "domain", "degree", "weighted_degree"]
HUB_FIELDS = ["rank", "node", "species", "type", "domain", "degree", "weighted_degree"]


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key) or row.get(key.capitalize()) or row.get(key.upper())
        if value:
            return value
    return ""


def _weight(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 1.0


def _clean_node(value: str) -> str:
    for suffix in [".1", ".2", ".3", ".p", ".cds"]:
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value


def normalize_edges(edges: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in edges:
        source = _clean_node(_first(row, "source", "from", "Source"))
        target = _clean_node(_first(row, "target", "to", "Target"))
        if not source or not target or source == target:
            continue
        species = _first(row, "species", "Species") or "unknown"
        key = tuple(sorted([source, target]) + [species])
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                "source": source,
                "target": target,
                "weight": f"{_weight(_first(row, 'weight', 'score')):.4f}",
                "species": species,
            }
        )
    return normalized


def _node_annotation_map(node_annotations: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    annotations: dict[str, dict[str, str]] = {}
    for row in node_annotations:
        node = _clean_node(_first(row, "node", "id", "Id", "gene_id"))
        if not node:
            continue
        annotations[node] = {
            "species": _first(row, "species", "Species") or "unknown",
            "type": _first(row, "type", "Type") or "GDSL",
            "domain": _first(row, "domain", "Domain", "hmm_id") or "unknown",
        }
    return annotations


def build_ppi_tables(
    *,
    edges: list[dict[str, str]],
    node_annotations: list[dict[str, str]] | None = None,
    top_n: int = 20,
) -> dict[str, list[dict[str, str]]]:
    normalized_edges = normalize_edges(edges)
    annotations = _node_annotation_map(node_annotations or [])
    degree: defaultdict[str, int] = defaultdict(int)
    weighted_degree: defaultdict[str, float] = defaultdict(float)
    species_by_node: dict[str, str] = {}
    for edge in normalized_edges:
        weight = _weight(edge["weight"])
        for endpoint in [edge["source"], edge["target"]]:
            degree[endpoint] += 1
            weighted_degree[endpoint] += weight
            species_by_node.setdefault(endpoint, edge["species"])

    nodes: list[dict[str, str]] = []
    for node in sorted(degree):
        annotation = annotations.get(node, {})
        species = annotation.get("species") or species_by_node.get(node, "unknown")
        nodes.append(
            {
                "node": node,
                "species": species,
                "type": annotation.get("type") or "Others",
                "domain": annotation.get("domain") or "unknown",
                "degree": str(degree[node]),
                "weighted_degree": f"{weighted_degree[node]:.4f}",
            }
        )

    hubs = sorted(nodes, key=lambda row: (-float(row["weighted_degree"]), row["node"]))[:top_n]
    hub_rows = [{"rank": str(index), **row} for index, row in enumerate(hubs, start=1)]
    return {"edges": normalized_edges, "nodes": nodes, "hubs": hub_rows}


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edges", required=True, type=Path)
    parser.add_argument("--nodes", default=None, type=Path)
    parser.add_argument("--top-n", default=20, type=int)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    outputs = build_ppi_tables(edges=read_tsv(args.edges), node_annotations=read_tsv(args.nodes), top_n=args.top_n)
    write_tsv(outputs["edges"], args.outdir / "ppi_edges.tsv", EDGE_FIELDS)
    write_tsv(outputs["nodes"], args.outdir / "ppi_nodes.tsv", NODE_FIELDS)
    write_tsv(outputs["hubs"], args.outdir / "ppi_hubs.tsv", HUB_FIELDS)


if __name__ == "__main__":
    main()
