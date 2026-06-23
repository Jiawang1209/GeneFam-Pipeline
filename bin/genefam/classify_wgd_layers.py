#!/usr/bin/env python3
"""Classify duplicated pairs into anonymous WGD layers from Ks bins."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["gene_a", "gene_b", "ks", "wgd_layer", "event_name", "confidence"]


def _layer_for_ks(ks: float, bins: list[float]) -> str:
    for index, upper_bound in enumerate(sorted(bins), start=1):
        if ks <= upper_bound:
            return f"WGD_layer_{index}"
    return f"WGD_layer_{len(bins) + 1}"


def classify_pairs(
    rows: list[dict[str, str]],
    bins: list[float],
    named_events: dict[str, str],
) -> list[dict[str, str]]:
    classified: list[dict[str, str]] = []
    for row in rows:
        ks = float(row["ks"])
        layer = _layer_for_ks(ks, bins)
        event_name = named_events.get(layer, "unannotated")
        confidence = "configured" if event_name != "unannotated" else "layer_only"
        classified.append(
            {
                "gene_a": row["gene_a"],
                "gene_b": row["gene_b"],
                "ks": row["ks"],
                "wgd_layer": layer,
                "event_name": event_name,
                "confidence": confidence,
            }
        )
    return classified


def read_pairs(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_pairs(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def parse_named_events(values: list[str]) -> dict[str, str]:
    events: dict[str, str] = {}
    for value in values:
        layer, event_name = value.split("=", 1)
        events[layer] = event_name
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True, type=Path)
    parser.add_argument("--bins", required=True, help="Comma-separated Ks upper bounds, for example 0.3,0.8")
    parser.add_argument("--event", action="append", default=[], help="Optional mapping like WGD_layer_1=alpha")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    bins = [float(value) for value in args.bins.split(",") if value]
    write_pairs(classify_pairs(read_pairs(args.pairs), bins, parse_named_events(args.event)), args.out)


if __name__ == "__main__":
    main()
