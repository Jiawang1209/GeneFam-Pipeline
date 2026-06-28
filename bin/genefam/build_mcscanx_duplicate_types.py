#!/usr/bin/env python3
"""Derive gene-level duplicate types from MCScanX self gene pairs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["species_id", "gene_id", "duplicate_type", "raw_duplicate_type", "evidence_pair_count"]
TYPE_PRIORITY = {
    "tandem": 0,
    "proximal": 1,
    "WGD/segmental": 2,
    "dispersed": 3,
    "singleton": 4,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _normalize_type(raw_type: str) -> str:
    value = raw_type.strip()
    lowered = value.lower()
    if lowered in {"wgd", "segmental", "collinear", "collinearity", "syntenic"}:
        return "WGD/segmental"
    if lowered in {"tandem", "proximal", "dispersed", "singleton"}:
        return lowered
    return value or "unknown"


def _best_type(raw_types: list[str]) -> str:
    normalized = [_normalize_type(raw_type) for raw_type in raw_types]
    return sorted(normalized, key=lambda item: (TYPE_PRIORITY.get(item, 99), item))[0]


def build_duplicate_type_rows(pair_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    evidence: dict[tuple[str, str], list[str]] = {}
    for row in pair_rows:
        species_id = row.get("species_id", "").strip()
        raw_type = (row.get("type") or row.get("duplicate_type") or row.get("pair_type") or "").strip()
        for key in ("gene_a", "gene_b"):
            gene_id = row.get(key, "").strip()
            if species_id and gene_id and raw_type:
                evidence.setdefault((species_id, gene_id), []).append(raw_type)

    output_rows: list[dict[str, str]] = []
    for (species_id, gene_id), raw_types in sorted(evidence.items()):
        output_rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "duplicate_type": _best_type(raw_types),
                "raw_duplicate_type": ",".join(sorted(set(raw_types))),
                "evidence_pair_count": str(len(raw_types)),
            }
        )
    return output_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcscanx-pairs", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(build_duplicate_type_rows(read_tsv(args.mcscanx_pairs)), args.out)


if __name__ == "__main__":
    main()
