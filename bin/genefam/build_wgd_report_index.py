#!/usr/bin/env python3
"""Build a report index for the WGD/duplication retention branch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "path", "status", "description"]
DESCRIPTIONS = {
    "wgd_run_config_snapshot": "WGD run parameters including Ks bins and named event mappings",
    "normalized_duplicates": "Normalized whole-genome duplicate type table",
    "family_duplicates": "Family members joined to duplicate classifications",
    "wgd_layers": "Ks-derived anonymous WGD layer assignments",
    "kaks_wgd_annotations": "WGD event labels and Ks positions used to annotate the Ks distribution plot",
    "wgd_event_evidence": "Named WGD event evidence including gamma beta alpha theta labels",
    "family_wgd_event_membership": "Family member membership in named WGD events",
    "family_event_retention_summary": "Family retention summary by WGD event and duplicate type",
    "retention_enrichment": "Duplicate-type retention enrichment for family members",
    "ks_distribution_pdf": "Ks distribution PDF plot for WGD-layer interpretation",
    "ks_distribution_png": "Ks distribution PNG plot for WGD-layer interpretation",
    "duplicate_type_kaks": "Pairwise Ka/Ks values joined to duplicate type classes",
    "duplicate_type_kaks_summary": "Duplicate-type grouped Ka/Ks summary table",
    "duplicate_type_kaks_skipped": "Ka/Ks pairs skipped because duplicate type evidence was missing",
    "duplicate_type_kaks_pdf": "Duplicate-type grouped Ks and Ka/Ks PDF plot",
    "duplicate_type_kaks_png": "Duplicate-type grouped Ks and Ka/Ks PNG plot",
    "pangenome_kaks": "Pairwise Ka/Ks values joined to pangenome presence classes",
    "pangenome_kaks_summary": "Pangenome-class grouped Ka/Ks summary table",
    "pangenome_kaks_skipped": "Ka/Ks pairs skipped because pangenome class evidence was missing",
    "pangenome_kaks_pdf": "Pangenome-class grouped Ks and Ka/Ks PDF plot",
    "pangenome_kaks_png": "Pangenome-class grouped Ks and Ka/Ks PNG plot",
}


def build_report_index(published_outdir: str) -> list[dict[str, str]]:
    outdir = Path(published_outdir)
    paths = {
        "wgd_run_config_snapshot": outdir / "tables/wgd_run_config_snapshot.tsv",
        "normalized_duplicates": outdir / "tables/normalized_duplicate_types.tsv",
        "family_duplicates": outdir / "tables/family_duplicate_classification.tsv",
        "wgd_layers": outdir / "tables/wgd_layers.tsv",
        "kaks_wgd_annotations": outdir / "tables/kaks_wgd_annotations.tsv",
        "wgd_event_evidence": outdir / "tables/wgd_event_evidence.tsv",
        "family_wgd_event_membership": outdir / "tables/family_wgd_event_membership.tsv",
        "family_event_retention_summary": outdir / "tables/family_event_retention_summary.tsv",
        "retention_enrichment": outdir / "tables/retention_enrichment.tsv",
        "ks_distribution_pdf": outdir / "plots/ks_distribution.pdf",
        "ks_distribution_png": outdir / "plots/ks_distribution.png",
        "duplicate_type_kaks": outdir / "tables/duplicate_type_kaks.tsv",
        "duplicate_type_kaks_summary": outdir / "tables/duplicate_type_kaks_summary.tsv",
        "duplicate_type_kaks_skipped": outdir / "tables/duplicate_type_kaks_skipped.tsv",
        "duplicate_type_kaks_pdf": outdir / "plots/duplicate_type_kaks.pdf",
        "duplicate_type_kaks_png": outdir / "plots/duplicate_type_kaks.png",
        "pangenome_kaks": outdir / "tables/pangenome_kaks.tsv",
        "pangenome_kaks_summary": outdir / "tables/pangenome_kaks_summary.tsv",
        "pangenome_kaks_skipped": outdir / "tables/pangenome_kaks_skipped.tsv",
        "pangenome_kaks_pdf": outdir / "plots/pangenome_kaks.pdf",
        "pangenome_kaks_png": outdir / "plots/pangenome_kaks.png",
    }
    return [
        {
            "key": key,
            "path": str(paths[key]),
            "status": "available",
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
    parser.add_argument("--published-outdir", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(build_report_index(args.published_outdir), args.out)


if __name__ == "__main__":
    main()
