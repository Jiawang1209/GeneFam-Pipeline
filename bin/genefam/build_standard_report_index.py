#!/usr/bin/env python3
"""Build a report index for the standard identification branch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "path", "status", "description"]
DESCRIPTIONS = {
    "species_manifest": "Selected species and input files",
    "family_candidates": "Merged family candidate members",
    "family_counts": "Per-species family member counts",
    "family_members_faa": "Family member peptide FASTA",
    "alignment_manifest": "Alignment preparation manifest",
    "phylogeny_manifest": "Phylogeny preparation manifest",
    "chromosome_locations": "Family member chromosome coordinates",
    "family_expression": "Family member RNA-seq expression matrix",
    "plot_manifest": "Generated plot inventory",
}


def build_report_index(paths: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "path": paths[key],
            "status": "available" if paths[key] else "missing",
            "description": DESCRIPTIONS[key],
        }
        for key in DESCRIPTIONS
    ]


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
    for key in DESCRIPTIONS:
        parser.add_argument(f"--{key.replace('_', '-')}", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in DESCRIPTIONS}
    write_tsv(build_report_index(paths), args.out)


if __name__ == "__main__":
    main()
