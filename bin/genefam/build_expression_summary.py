#!/usr/bin/env python3
"""Build expression heatmap annotation and replicate-summary tables."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path


SAMPLE_METADATA_FIELDS = ["sample_id", "condition", "timepoint", "replicate", "group", "plot_label"]
GENE_SUMMARY_FIELDS = [
    "gene_id",
    "detected_sample_count",
    "mean_expression",
    "max_group",
    "max_group_expression",
    "min_group",
    "min_group_expression",
    "fold_change_max_min",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str] | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else ["gene_id"]
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


def _sample_columns(expression_rows: list[dict[str, str]]) -> list[str]:
    if not expression_rows:
        raise ValueError("Expression table must not be empty")
    return [column for column in expression_rows[0] if column != "gene_id"]


def _default_metadata(sample_ids: list[str]) -> list[dict[str, str]]:
    return [
        {
            "sample_id": sample_id,
            "condition": "unannotated",
            "timepoint": "",
            "replicate": str(index + 1),
            "group": sample_id,
            "plot_label": sample_id,
        }
        for index, sample_id in enumerate(sample_ids)
    ]


def normalize_sample_metadata(
    sample_ids: list[str],
    metadata_rows: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    if not metadata_rows:
        return _default_metadata(sample_ids)
    by_sample = {row.get("sample_id", row.get("sample", "")).strip(): row for row in metadata_rows}
    missing = [sample_id for sample_id in sample_ids if sample_id not in by_sample]
    if missing:
        raise ValueError(f"Missing expression sample metadata: {', '.join(missing)}")
    normalized: list[dict[str, str]] = []
    for sample_id in sample_ids:
        row = by_sample[sample_id]
        condition = row.get("condition", row.get("treatment", "unannotated")) or "unannotated"
        timepoint = row.get("timepoint", row.get("time", "")) or ""
        replicate = row.get("replicate", row.get("rep", "")) or ""
        group = row.get("group", "") or "_".join(part for part in [condition, timepoint] if part) or sample_id
        plot_label = row.get("plot_label", "") or "|".join(
            part for part in [condition, timepoint, f"r{replicate}" if replicate else ""] if part
        )
        normalized.append(
            {
                "sample_id": sample_id,
                "condition": condition,
                "timepoint": timepoint,
                "replicate": replicate,
                "group": group,
                "plot_label": plot_label or sample_id,
            }
        )
    return normalized


def build_group_matrix(
    expression_rows: list[dict[str, str]],
    metadata_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    groups: list[str] = []
    samples_by_group: dict[str, list[str]] = {}
    for row in metadata_rows:
        group = row["group"]
        if group not in samples_by_group:
            groups.append(group)
            samples_by_group[group] = []
        samples_by_group[group].append(row["sample_id"])
    matrix: list[dict[str, str]] = []
    for row in expression_rows:
        out = {"gene_id": row["gene_id"]}
        for group in groups:
            values = [_as_float(row.get(sample_id)) for sample_id in samples_by_group[group]]
            numeric = [value for value in values if value is not None]
            out[group] = _fmt(statistics.fmean(numeric) if numeric else None)
        matrix.append(out)
    return matrix


def build_gene_summary(
    expression_rows: list[dict[str, str]],
    group_matrix: list[dict[str, str]],
) -> list[dict[str, str]]:
    sample_ids = _sample_columns(expression_rows)
    summaries: list[dict[str, str]] = []
    for expression_row, group_row in zip(expression_rows, group_matrix, strict=True):
        sample_values = [_as_float(expression_row.get(sample_id)) for sample_id in sample_ids]
        detected = [value for value in sample_values if value is not None and value > 0]
        group_values = {
            group: value
            for group, value in ((key, _as_float(value)) for key, value in group_row.items() if key != "gene_id")
            if value is not None
        }
        max_group = max(group_values, key=group_values.get) if group_values else ""
        min_group = min(group_values, key=group_values.get) if group_values else ""
        max_value = group_values.get(max_group) if max_group else None
        min_value = group_values.get(min_group) if min_group else None
        fold_change = None
        if max_value is not None and min_value is not None:
            fold_change = max_value / min_value if min_value > 0 else None
        summaries.append(
            {
                "gene_id": expression_row["gene_id"],
                "detected_sample_count": str(len(detected)),
                "mean_expression": _fmt(statistics.fmean(detected) if detected else None),
                "max_group": max_group,
                "max_group_expression": _fmt(max_value),
                "min_group": min_group,
                "min_group_expression": _fmt(min_value),
                "fold_change_max_min": _fmt(fold_change),
            }
        )
    return summaries


def build_expression_summary(*, expression: Path, metadata: Path | None, outdir: Path) -> dict[str, Path]:
    expression_rows = read_tsv(expression)
    sample_ids = _sample_columns(expression_rows)
    metadata_rows = read_tsv(metadata) if metadata else None
    normalized_metadata = normalize_sample_metadata(sample_ids, metadata_rows)
    group_matrix = build_group_matrix(expression_rows, normalized_metadata)
    gene_summary = build_gene_summary(expression_rows, group_matrix)
    outputs = {
        "sample_metadata": outdir / "expression_sample_metadata.tsv",
        "group_matrix": outdir / "expression_group_matrix.tsv",
        "gene_summary": outdir / "expression_gene_summary.tsv",
    }
    write_tsv(normalized_metadata, outputs["sample_metadata"], SAMPLE_METADATA_FIELDS)
    write_tsv(group_matrix, outputs["group_matrix"])
    write_tsv(gene_summary, outputs["gene_summary"], GENE_SUMMARY_FIELDS)
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key, path in outputs.items():
        writer.writerow([key, path])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expression", required=True, type=Path)
    parser.add_argument("--metadata", default=None, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(build_expression_summary(expression=args.expression, metadata=args.metadata, outdir=args.outdir))


if __name__ == "__main__":
    main()
