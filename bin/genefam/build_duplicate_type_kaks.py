#!/usr/bin/env python3
"""Join duplicate-type classifications with pairwise Ka/Ks metrics."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path


PAIR_FIELDNAMES = [
    "gene_a",
    "gene_b",
    "duplicate_type_a",
    "duplicate_type_b",
    "pair_duplicate_type",
    "ks",
    "ka",
    "ka_ks",
    "selection_category",
]
SUMMARY_FIELDNAMES = [
    "pair_duplicate_type",
    "pair_count",
    "median_ks",
    "mean_ka_ks",
    "gene_pair_examples",
]
SKIPPED_FIELDNAMES = ["gene_a", "gene_b", "reason", "missing_genes"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6g}"


def _as_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _duplicate_index(rows: list[dict[str, str]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for row in rows:
        gene_id = row.get("gene_id", "").strip()
        duplicate_type = row.get("duplicate_type", "").strip()
        if gene_id and duplicate_type:
            index[gene_id] = duplicate_type
    return index


def _pair_type(type_a: str, type_b: str) -> str:
    if type_a == type_b:
        return type_a
    return "mixed"


def build_pair_rows(
    duplicate_rows: list[dict[str, str]],
    kaks_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    duplicate_by_gene = _duplicate_index(duplicate_rows)
    pair_rows: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for row in kaks_rows:
        gene_a = row.get("gene_a", "").strip()
        gene_b = row.get("gene_b", "").strip()
        type_a = duplicate_by_gene.get(gene_a, "")
        type_b = duplicate_by_gene.get(gene_b, "")
        missing = [gene for gene, duplicate_type in [(gene_a, type_a), (gene_b, type_b)] if not duplicate_type]
        if missing:
            skipped.append(
                {
                    "gene_a": gene_a,
                    "gene_b": gene_b,
                    "reason": "missing_duplicate_type",
                    "missing_genes": ",".join(missing),
                }
            )
            continue
        pair_rows.append(
            {
                "gene_a": gene_a,
                "gene_b": gene_b,
                "duplicate_type_a": type_a,
                "duplicate_type_b": type_b,
                "pair_duplicate_type": _pair_type(type_a, type_b),
                "ks": row.get("ks", ""),
                "ka": row.get("ka", ""),
                "ka_ks": row.get("ka_ks", row.get("Ka/Ks", "")),
                "selection_category": row.get("selection_category", ""),
            }
        )
    return pair_rows, skipped


def summarize_pair_rows(pair_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in pair_rows:
        grouped.setdefault(row["pair_duplicate_type"], []).append(row)
    summary: list[dict[str, str]] = []
    for duplicate_type in sorted(grouped):
        rows = grouped[duplicate_type]
        ks_values = [_as_float(row.get("ks")) for row in rows]
        ks_values = [value for value in ks_values if value is not None]
        ka_ks_values = [_as_float(row.get("ka_ks")) for row in rows]
        ka_ks_values = [value for value in ka_ks_values if value is not None]
        examples = [f"{row['gene_a']}-{row['gene_b']}" for row in rows[:5]]
        summary.append(
            {
                "pair_duplicate_type": duplicate_type,
                "pair_count": str(len(rows)),
                "median_ks": _fmt(statistics.median(ks_values) if ks_values else None),
                "mean_ka_ks": _fmt(statistics.fmean(ka_ks_values) if ka_ks_values else None),
                "gene_pair_examples": ",".join(examples),
            }
        )
    return summary


def build_duplicate_type_kaks(*, duplicates: Path, kaks_pairs: Path, outdir: Path) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "pair_table": outdir / "duplicate_type_kaks.tsv",
        "summary_table": outdir / "duplicate_type_kaks_summary.tsv",
        "skipped_pairs": outdir / "duplicate_type_kaks_skipped.tsv",
    }
    pair_rows, skipped = build_pair_rows(read_tsv(duplicates), read_tsv(kaks_pairs))
    write_tsv(pair_rows, outputs["pair_table"], PAIR_FIELDNAMES)
    write_tsv(summarize_pair_rows(pair_rows), outputs["summary_table"], SUMMARY_FIELDNAMES)
    write_tsv(skipped, outputs["skipped_pairs"], SKIPPED_FIELDNAMES)
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key, path in outputs.items():
        writer.writerow([key, path])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duplicates", required=True, type=Path)
    parser.add_argument("--kaks-pairs", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(build_duplicate_type_kaks(duplicates=args.duplicates, kaks_pairs=args.kaks_pairs, outdir=args.outdir))


if __name__ == "__main__":
    main()
