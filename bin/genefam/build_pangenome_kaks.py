#!/usr/bin/env python3
"""Join pangenome presence classes with pairwise Ka/Ks metrics."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path


PAIR_FIELDNAMES = [
    "gene_a",
    "gene_b",
    "pangenome_class_a",
    "pangenome_class_b",
    "pair_pangenome_class",
    "ks",
    "ka",
    "ka_ks",
    "selection_category",
]
SUMMARY_FIELDNAMES = [
    "pair_pangenome_class",
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


def _first(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key) or row.get(key.capitalize()) or row.get(key.upper())
        if value:
            return value.strip()
    return ""


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


def _pangenome_index(rows: list[dict[str, str]]) -> dict[str, str]:
    index: dict[str, str] = {}
    for row in rows:
        gene_id = _first(row, "gene_id", "gene", "id")
        pangenome_class = _first(row, "pangenome_class", "presence_class", "core_class", "class")
        if gene_id and pangenome_class:
            index[gene_id] = pangenome_class
    return index


def _pair_class(class_a: str, class_b: str) -> str:
    if class_a == class_b:
        return class_a
    return "mixed"


def build_pair_rows(
    pangenome_rows: list[dict[str, str]],
    kaks_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    class_by_gene = _pangenome_index(pangenome_rows)
    pair_rows: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    for row in kaks_rows:
        gene_a = _first(row, "gene_a", "gene1", "gene_id_a")
        gene_b = _first(row, "gene_b", "gene2", "gene_id_b")
        class_a = class_by_gene.get(gene_a, "")
        class_b = class_by_gene.get(gene_b, "")
        missing = [gene for gene, pangenome_class in [(gene_a, class_a), (gene_b, class_b)] if not pangenome_class]
        if missing:
            skipped.append(
                {
                    "gene_a": gene_a,
                    "gene_b": gene_b,
                    "reason": "missing_pangenome_class",
                    "missing_genes": ",".join(missing),
                }
            )
            continue
        pair_rows.append(
            {
                "gene_a": gene_a,
                "gene_b": gene_b,
                "pangenome_class_a": class_a,
                "pangenome_class_b": class_b,
                "pair_pangenome_class": _pair_class(class_a, class_b),
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
        grouped.setdefault(row["pair_pangenome_class"], []).append(row)
    summary: list[dict[str, str]] = []
    for pangenome_class in sorted(grouped):
        rows = grouped[pangenome_class]
        ks_values = [_as_float(row.get("ks")) for row in rows]
        ks_values = [value for value in ks_values if value is not None]
        ka_ks_values = [_as_float(row.get("ka_ks")) for row in rows]
        ka_ks_values = [value for value in ka_ks_values if value is not None]
        examples = [f"{row['gene_a']}-{row['gene_b']}" for row in rows[:5]]
        summary.append(
            {
                "pair_pangenome_class": pangenome_class,
                "pair_count": str(len(rows)),
                "median_ks": _fmt(statistics.median(ks_values) if ks_values else None),
                "mean_ka_ks": _fmt(statistics.fmean(ka_ks_values) if ka_ks_values else None),
                "gene_pair_examples": ",".join(examples),
            }
        )
    return summary


def build_pangenome_kaks(*, pangenome_classes: Path, kaks_pairs: Path, outdir: Path) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "pair_table": outdir / "pangenome_kaks.tsv",
        "summary_table": outdir / "pangenome_kaks_summary.tsv",
        "skipped_pairs": outdir / "pangenome_kaks_skipped.tsv",
    }
    pair_rows, skipped = build_pair_rows(read_tsv(pangenome_classes), read_tsv(kaks_pairs))
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
    parser.add_argument("--pangenome-classes", required=True, type=Path)
    parser.add_argument("--kaks-pairs", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(
        build_pangenome_kaks(
            pangenome_classes=args.pangenome_classes,
            kaks_pairs=args.kaks_pairs,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
