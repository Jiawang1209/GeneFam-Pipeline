#!/usr/bin/env python3
"""Prepare a manifest for phylogenetic tree construction."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["family_name", "tree_builder", "alignment", "treefile", "support_file"]


def prepare_phylogeny_manifest(
    alignment_rows: list[dict[str, str]],
    outdir: Path,
    tree_builder: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for alignment_row in alignment_rows:
        family_name = alignment_row["family_name"]
        alignment = alignment_row.get("trimmed_alignment") or alignment_row["raw_alignment"]
        rows.append(
            {
                "family_name": family_name,
                "tree_builder": tree_builder,
                "alignment": alignment,
                "treefile": str(Path(outdir) / f"{family_name}.{tree_builder}.treefile"),
                "support_file": str(Path(outdir) / f"{family_name}.{tree_builder}.support.tsv"),
            }
        )
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alignment-manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--tree-builder", default="iqtree", choices=["iqtree", "fasttree"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        prepare_phylogeny_manifest(read_tsv(args.alignment_manifest), args.outdir, args.tree_builder),
        args.out,
    )


if __name__ == "__main__":
    main()
