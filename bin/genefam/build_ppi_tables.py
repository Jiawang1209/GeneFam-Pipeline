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
METRIC_FIELDS = ["metric", "value", "description"]


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


def normalize_edges(edges: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict[str, int]]:
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    evidence = {
        "raw_edge_rows": len(edges),
        "normalized_edge_rows": 0,
        "skipped_missing_endpoint": 0,
        "skipped_self_loops": 0,
        "duplicate_edge_rows": 0,
    }
    for row in edges:
        source = _clean_node(_first(row, "source", "from", "Source"))
        target = _clean_node(_first(row, "target", "to", "Target"))
        if not source or not target:
            evidence["skipped_missing_endpoint"] += 1
            continue
        if source == target:
            evidence["skipped_self_loops"] += 1
            continue
        species = _first(row, "species", "Species") or "unknown"
        key = tuple(sorted([source, target]) + [species])
        if key in seen:
            evidence["duplicate_edge_rows"] += 1
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
    evidence["normalized_edge_rows"] = len(normalized)
    return normalized, evidence


def _metric_rows(metrics: dict[str, int], descriptions: dict[str, str]) -> list[dict[str, str]]:
    return [
        {"metric": metric, "value": str(value), "description": descriptions.get(metric, "")}
        for metric, value in metrics.items()
    ]


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
    normalized_edges, evidence = normalize_edges(edges)
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
    annotated_nodes = sum(1 for node in degree if node in annotations)
    network_qc = {
        "node_count": len(nodes),
        "edge_count": len(normalized_edges),
        "hub_count": len(hub_rows),
        "species_count": len({edge["species"] for edge in normalized_edges}),
        "annotated_nodes": annotated_nodes,
        "missing_annotation_nodes": len(nodes) - annotated_nodes,
    }
    return {
        "edges": normalized_edges,
        "nodes": nodes,
        "hubs": hub_rows,
        "input_evidence": _metric_rows(
            evidence,
            {
                "raw_edge_rows": "Raw PPI edge rows read from the user-provided edge table",
                "normalized_edge_rows": "Edges retained after endpoint cleanup, self-loop removal, and duplicate removal",
                "skipped_missing_endpoint": "Rows skipped because source or target was missing",
                "skipped_self_loops": "Rows skipped because source and target were the same gene",
                "duplicate_edge_rows": "Repeated undirected source-target-species rows removed before plotting",
            },
        ),
        "network_qc": _metric_rows(
            network_qc,
            {
                "node_count": "Unique genes present in the normalized PPI network",
                "edge_count": "Normalized PPI edges used for ggNetView plotting",
                "hub_count": "Hub genes reported in the ranked hub table",
                "species_count": "Species represented by normalized PPI edges",
                "annotated_nodes": "Network nodes matched to the optional node annotation table",
                "missing_annotation_nodes": "Network nodes without optional node annotation records",
            },
        ),
    }


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
    write_tsv(outputs["input_evidence"], args.outdir / "ppi_input_evidence.tsv", METRIC_FIELDS)
    write_tsv(outputs["network_qc"], args.outdir / "ppi_network_qc.tsv", METRIC_FIELDS)


if __name__ == "__main__":
    main()
