#!/usr/bin/env python3
"""Prepare a manifest for alignment and phylogeny steps."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["family_name", "aligner", "sequence_count", "input_fasta", "raw_alignment", "trimmed_alignment"]


def _count_fasta_records(path: Path) -> int:
    count = 0
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith(">"):
                count += 1
    return count


def prepare_alignment_manifest(
    family_name: str,
    fasta_path: Path,
    outdir: Path,
    aligner: str,
) -> list[dict[str, str]]:
    sequence_count = _count_fasta_records(fasta_path)
    if sequence_count < 2:
        raise ValueError("At least two sequences are required for alignment")
    outdir = Path(outdir)
    return [
        {
            "family_name": family_name,
            "aligner": aligner,
            "sequence_count": str(sequence_count),
            "input_fasta": str(fasta_path),
            "raw_alignment": str(outdir / f"{family_name}.{aligner}.aln.faa"),
            "trimmed_alignment": str(outdir / f"{family_name}.{aligner}.trimmed.aln.faa"),
        }
    ]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-name", required=True)
    parser.add_argument("--fasta", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--aligner", default="mafft", choices=["mafft", "muscle"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(prepare_alignment_manifest(args.family_name, args.fasta, args.outdir, args.aligner), args.out)


if __name__ == "__main__":
    main()
