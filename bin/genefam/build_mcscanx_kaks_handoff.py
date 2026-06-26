#!/usr/bin/env python3
"""Build prepared WGD handoff tables from real MCScanX and Ka/Ks outputs."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.parse_kaks_results import parse_kaks_table, write_tsv as write_kaks_tsv
from bin.genefam.parse_mcscanx_collinearity import parse_collinearity, write_tsv as write_synteny_tsv
from bin.genefam.prepare_kaks_pairs import prepare_kaks_pairs, write_tsv as write_kaks_manifest_tsv


DUPLICATE_FIELDNAMES = ["gene_id", "duplicate_type", "raw_duplicate_type"]
KAKS_PAIR_FIELDNAMES = ["gene_a", "gene_b", "ks", "ka", "ka_ks", "selection_category"]


def _write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _duplicate_rows(syntenic_pairs: list[dict[str, str]]) -> list[dict[str, str]]:
    genes = sorted({row["gene_a"] for row in syntenic_pairs} | {row["gene_b"] for row in syntenic_pairs})
    return [
        {"gene_id": gene_id, "duplicate_type": "WGD/segmental", "raw_duplicate_type": "MCScanX_collinear"}
        for gene_id in genes
    ]


def _kaks_pairs_for_synteny(kaks_rows: list[dict[str, str]], syntenic_pairs: list[dict[str, str]]) -> list[dict[str, str]]:
    allowed = {(row["gene_a"], row["gene_b"]) for row in syntenic_pairs}
    allowed |= {(right, left) for left, right in allowed}
    filtered: list[dict[str, str]] = []
    for row in kaks_rows:
        if (row["gene_a"], row["gene_b"]) in allowed:
            filtered.append(
                {
                    "gene_a": row["gene_a"],
                    "gene_b": row["gene_b"],
                    "ks": row["ks"],
                    "ka": row["ka"],
                    "ka_ks": row["ka_ks"],
                    "selection_category": row["selection_category"],
                }
            )
    return filtered


def _write_summary(
    out_path: Path,
    *,
    collinearity: Path,
    kaks: Path | None,
    syntenic_count: int,
    duplicate_gene_count: int,
    normalized_kaks_count: int,
    handoff_kaks_count: int,
    pair_manifest_count: int,
) -> None:
    out_path.write_text(
        "\n".join(
            [
                "# MCScanX/KaKs Handoff",
                "",
                f"MCScanX collinearity: `{collinearity}`",
                f"Ka/Ks table: `{kaks}`" if kaks else "Ka/Ks table: not provided",
                "",
                f"- Syntenic pairs: {syntenic_count}",
                f"- WGD/segmental duplicate genes: {duplicate_gene_count}",
                f"- Normalized Ka/Ks rows: {normalized_kaks_count}",
                f"- Ka/Ks rows retained for syntenic pairs: {handoff_kaks_count}",
                f"- Pair FASTA manifest rows: {pair_manifest_count}",
                "",
                "The generated `duplicate_types.tsv` and `kaks_pairs.tsv` can be passed to the WGD Nextflow branch.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def build_handoff(
    *,
    collinearity: Path,
    kaks: Path | None,
    outdir: Path,
    cds_a: Path | None = None,
    cds_b: Path | None = None,
) -> dict[str, Path]:
    outdir = Path(outdir)
    tables_dir = outdir / "tables"
    pair_fastas_dir = outdir / "kaks_pair_fastas"
    outputs = {
        "syntenic_pairs": tables_dir / "syntenic_pairs.tsv",
        "duplicate_types": tables_dir / "duplicate_types.tsv",
        "normalized_kaks": tables_dir / "normalized_kaks.tsv",
        "kaks_pairs": tables_dir / "kaks_pairs.tsv",
        "kaks_pair_manifest": tables_dir / "kaks_pair_manifest.tsv",
        "summary": outdir / "mcscanx_kaks_handoff.md",
    }

    syntenic_pairs = parse_collinearity(collinearity)
    write_synteny_tsv(syntenic_pairs, outputs["syntenic_pairs"])

    duplicate_rows = _duplicate_rows(syntenic_pairs)
    _write_tsv(duplicate_rows, DUPLICATE_FIELDNAMES, outputs["duplicate_types"])

    normalized_kaks: list[dict[str, str]] = parse_kaks_table(kaks) if kaks else []
    write_kaks_tsv(normalized_kaks, outputs["normalized_kaks"])

    handoff_kaks = _kaks_pairs_for_synteny(normalized_kaks, syntenic_pairs)
    _write_tsv(handoff_kaks, KAKS_PAIR_FIELDNAMES, outputs["kaks_pairs"])

    pair_manifest: list[dict[str, str]] = []
    if cds_a and cds_b:
        pair_manifest = prepare_kaks_pairs(syntenic_pairs, cds_a, cds_b, pair_fastas_dir)
    write_kaks_manifest_tsv(pair_manifest, outputs["kaks_pair_manifest"])

    _write_summary(
        outputs["summary"],
        collinearity=collinearity,
        kaks=kaks,
        syntenic_count=len(syntenic_pairs),
        duplicate_gene_count=len(duplicate_rows),
        normalized_kaks_count=len(normalized_kaks),
        handoff_kaks_count=len(handoff_kaks),
        pair_manifest_count=len(pair_manifest),
    )
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collinearity", required=True, type=Path)
    parser.add_argument("--kaks", default=None, type=Path)
    parser.add_argument("--cds-a", default=None, type=Path)
    parser.add_argument("--cds-b", default=None, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(
        build_handoff(
            collinearity=args.collinearity,
            kaks=args.kaks,
            cds_a=args.cds_a,
            cds_b=args.cds_b,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
