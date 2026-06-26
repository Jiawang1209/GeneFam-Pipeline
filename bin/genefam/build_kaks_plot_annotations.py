#!/usr/bin/env python3
"""Build WGD layer annotations for the Ks distribution plot."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path


FIELDNAMES = [
    "wgd_layer",
    "event_name",
    "pair_count",
    "ks_min",
    "ks_median",
    "ks_max",
    "label_position",
    "label",
]


def build_kaks_plot_annotations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_layer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("ks") not in {None, ""}:
            by_layer[row["wgd_layer"]].append(row)

    annotations: list[dict[str, str]] = []
    for layer in sorted(by_layer):
        layer_rows = by_layer[layer]
        ks_values = sorted(float(row["ks"]) for row in layer_rows)
        event_names = sorted({row.get("event_name", "unannotated") or "unannotated" for row in layer_rows})
        event_name = event_names[0] if len(event_names) == 1 else "mixed"
        pair_count = len(layer_rows)
        ks_median = statistics.median(ks_values)
        label = f"{event_name} ({layer}, n={pair_count})"
        annotations.append(
            {
                "wgd_layer": layer,
                "event_name": event_name,
                "pair_count": str(pair_count),
                "ks_min": f"{min(ks_values):.4f}",
                "ks_median": f"{ks_median:.4f}",
                "ks_max": f"{max(ks_values):.4f}",
                "label_position": f"{ks_median:.4f}",
                "label": label,
            }
        )
    return annotations


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classified-pairs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(build_kaks_plot_annotations(read_tsv(args.classified_pairs)), args.out)


if __name__ == "__main__":
    main()
