#!/usr/bin/env python3
"""Run a small alignment and phylogeny manifest smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.prepare_alignment_inputs import (
    prepare_alignment_manifest,
    write_tsv as write_alignment_tsv,
)
from bin.genefam.prepare_phylogeny_inputs import (
    prepare_phylogeny_manifest,
    write_tsv as write_phylogeny_tsv,
)


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_alignment_phylogeny_smoke(
    family_name: str,
    fasta: Path,
    aligner: str,
    tree_builder: str,
    outdir: Path,
) -> dict[str, Path]:
    alignment_dir = outdir / "alignment"
    phylogeny_dir = outdir / "phylogeny"
    outputs = {
        "alignment_manifest": outdir / "tables/alignment_manifest.tsv",
        "phylogeny_manifest": outdir / "tables/phylogeny_manifest.tsv",
        "summary": outdir / "alignment_phylogeny_smoke.md",
    }

    alignment_rows = prepare_alignment_manifest(family_name, fasta, alignment_dir, aligner)
    phylogeny_rows = prepare_phylogeny_manifest(alignment_rows, phylogeny_dir, tree_builder)
    write_alignment_tsv(alignment_rows, outputs["alignment_manifest"])
    write_phylogeny_tsv(phylogeny_rows, outputs["phylogeny_manifest"])

    sequence_count = alignment_rows[0]["sequence_count"]
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Alignment Phylogeny Smoke",
                "",
                f"Input FASTA: `{fasta}`",
                f"Family: {family_name}",
                f"Sequence count: {sequence_count}",
                f"Aligner: {aligner}",
                f"Tree builder: {tree_builder}",
                f"Alignment manifest: `{outputs['alignment_manifest']}`",
                f"Phylogeny manifest: `{outputs['phylogeny_manifest']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-name", required=True)
    parser.add_argument("--fasta", required=True, type=Path)
    parser.add_argument("--aligner", default="mafft", choices=["mafft", "muscle"])
    parser.add_argument("--tree-builder", default="iqtree", choices=["iqtree", "fasttree"])
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_alignment_phylogeny_smoke(
            args.family_name,
            args.fasta,
            args.aligner,
            args.tree_builder,
            args.outdir,
        )
    )


if __name__ == "__main__":
    main()
