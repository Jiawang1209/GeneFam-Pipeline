#!/usr/bin/env python3
"""Prepare CDS pair FASTA files for Ka/Ks calculation."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["gene_a", "gene_b", "pair_fasta", "expected_kaks"]


def _read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id: str | None = None
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                records[current_id] = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def prepare_kaks_pairs(
    syntenic_pairs: list[dict[str, str]],
    cds_a: Path,
    cds_b: Path,
    outdir: Path,
) -> list[dict[str, str]]:
    records_a = _read_fasta(cds_a)
    records_b = _read_fasta(cds_b)
    missing_a = sorted({row["gene_a"] for row in syntenic_pairs} - set(records_a))
    missing_b = sorted({row["gene_b"] for row in syntenic_pairs} - set(records_b))
    if missing_a:
        raise ValueError(f"Missing CDS IDs in first FASTA: {', '.join(missing_a)}")
    if missing_b:
        raise ValueError(f"Missing CDS IDs in second FASTA: {', '.join(missing_b)}")

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for pair in syntenic_pairs:
        gene_a = pair["gene_a"]
        gene_b = pair["gene_b"]
        stem = f"{gene_a}__{gene_b}"
        pair_fasta = outdir / f"{stem}.cds.fa"
        pair_fasta.write_text(f">{gene_a}\n{records_a[gene_a]}\n>{gene_b}\n{records_b[gene_b]}\n", encoding="utf-8")
        rows.append(
            {
                "gene_a": gene_a,
                "gene_b": gene_b,
                "pair_fasta": str(pair_fasta),
                "expected_kaks": str(outdir / f"{stem}.kaks.tsv"),
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
    parser.add_argument("--syntenic-pairs", required=True, type=Path)
    parser.add_argument("--cds-a", required=True, type=Path)
    parser.add_argument("--cds-b", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(prepare_kaks_pairs(read_tsv(args.syntenic_pairs), args.cds_a, args.cds_b, args.outdir), args.out)


if __name__ == "__main__":
    main()
