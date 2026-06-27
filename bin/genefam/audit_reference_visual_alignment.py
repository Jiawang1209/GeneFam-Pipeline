#!/usr/bin/env python3
"""Audit paper-level visual alignment against the Reference-derived figure set."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]

STANDARD_MODULES = [
    ("family_counts", "family member count overview"),
    ("gene_family_info_summary", "gene family information/copy number/protein properties"),
    ("gene_family_pangenome_summary", "pangenome breadth and copy-number balance"),
    ("tree_features", "tree_features, motif, gene structure, domain"),
    ("feature_summary", "large-family feature summary"),
    ("mcscanx_circlize", "MCScanX/synteny/circlize"),
    ("promoter_cis_elements", "promoter cis-element regulatory summary"),
    ("ppi_ggnetview", "ggNetView PPI network"),
    ("expression_heatmap", "RNA-seq expression heatmap"),
]

WGD_MODULES = [
    ("ks_distribution", "Ka/Ks/WGD gamma beta alpha theta"),
    ("duplicate_type_kaks", "duplicate-type Ka/Ks selection overview"),
    ("pangenome_kaks", "pangenome-class Ka/Ks selection overview"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _row(check: str, passed: bool, evidence: str, note: str) -> dict[str, str]:
    return {
        "check": check,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
        "note": note,
    }


def _keys(rows: list[dict[str, str]], field: str) -> set[str]:
    return {row.get(field, "").strip() for row in rows if row.get(field, "").strip()}


def _module_issues(rows: list[dict[str, str]], modules: list[tuple[str, str]]) -> list[str]:
    plot_keys = _keys(rows, "plot_key")
    return [f"{plot_key}:missing_plot" for plot_key, _label in modules if plot_key not in plot_keys]


def _interpretation_issues(
    standard_interpretations: list[dict[str, str]],
    wgd_interpretations: list[dict[str, str]],
) -> list[str]:
    standard_keys = _keys(standard_interpretations, "figure_key")
    wgd_keys = _keys(wgd_interpretations, "figure_key")
    issues: list[str] = []
    for plot_key, _label in STANDARD_MODULES:
        if plot_key not in standard_keys:
            issues.append(f"standard:{plot_key}:missing_interpretation")
    for plot_key, _label in WGD_MODULES:
        if plot_key not in wgd_keys:
            issues.append(f"wgd:{plot_key}:missing_interpretation")
    return issues


def _module_labels(modules: list[tuple[str, str]]) -> str:
    return "; ".join(label for _plot_key, label in modules)


def audit_reference_visual_alignment(
    standard_plot_manifest: Path,
    standard_figure_interpretations: Path,
    wgd_plot_manifest: Path,
    wgd_figure_interpretations: Path,
) -> list[dict[str, str]]:
    standard_plots = read_tsv(standard_plot_manifest)
    wgd_plots = read_tsv(wgd_plot_manifest)
    standard_interpretations = read_tsv(standard_figure_interpretations)
    wgd_interpretations = read_tsv(wgd_figure_interpretations)

    standard_issues = _module_issues(standard_plots, STANDARD_MODULES)
    wgd_issues = _module_issues(wgd_plots, WGD_MODULES)
    interpretation_issues = _interpretation_issues(standard_interpretations, wgd_interpretations)

    return [
        _row(
            "standard_reference_visual_modules",
            not standard_issues,
            str(standard_plot_manifest),
            "standard plot manifest covers Reference-level modules: " + _module_labels(STANDARD_MODULES)
            if not standard_issues
            else "missing standard Reference-level plot modules: " + ", ".join(standard_issues),
        ),
        _row(
            "wgd_reference_visual_modules",
            not wgd_issues,
            str(wgd_plot_manifest),
            "WGD plot manifest covers Reference-level modules: " + _module_labels(WGD_MODULES)
            if not wgd_issues
            else "missing WGD Reference-level plot modules: " + ", ".join(wgd_issues),
        ),
        _row(
            "reference_visual_interpretations",
            not interpretation_issues,
            f"{standard_figure_interpretations};{wgd_figure_interpretations}",
            "standard and WGD Reference-level plot modules have per-figure close-reading interpretation rows"
            if not interpretation_issues
            else "missing Reference-level figure interpretation rows: " + ", ".join(interpretation_issues),
        ),
    ]


def summarize_audit(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    return {"passed": passed, "failed": failed, "complete": failed == 0}


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    summary = summarize_audit(rows)
    lines = [
        "# Reference Visual Alignment Audit",
        "",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Complete: {str(summary['complete']).lower()}",
        "",
        "| check | status | evidence | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(row[field]) for field in FIELDNAMES) + " |")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--standard-plot-manifest", required=True, type=Path)
    parser.add_argument("--standard-figure-interpretations", required=True, type=Path)
    parser.add_argument("--wgd-plot-manifest", required=True, type=Path)
    parser.add_argument("--wgd-figure-interpretations", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_reference_visual_alignment(
        standard_plot_manifest=args.standard_plot_manifest,
        standard_figure_interpretations=args.standard_figure_interpretations,
        wgd_plot_manifest=args.wgd_plot_manifest,
        wgd_figure_interpretations=args.wgd_figure_interpretations,
    )
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    raise SystemExit(0 if summarize_audit(rows)["complete"] else 1)


if __name__ == "__main__":
    main()
