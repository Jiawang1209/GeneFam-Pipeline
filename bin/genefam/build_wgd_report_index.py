#!/usr/bin/env python3
"""Build a report index for the WGD/duplication retention branch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "path", "status", "description"]
DESCRIPTIONS = {
    "normalized_duplicates": "Normalized whole-genome duplicate type table",
    "family_duplicates": "Family members joined to duplicate classifications",
    "wgd_layers": "Ks-derived anonymous WGD layer assignments",
    "wgd_event_evidence": "Named WGD event evidence including gamma beta alpha theta labels",
    "family_wgd_event_membership": "Family member membership in named WGD events",
    "family_event_retention_summary": "Family retention summary by WGD event and duplicate type",
    "retention_enrichment": "Duplicate-type retention enrichment for family members",
}


def build_report_index(published_outdir: str) -> list[dict[str, str]]:
    outdir = Path(published_outdir)
    paths = {
        "normalized_duplicates": outdir / "tables/normalized_duplicate_types.tsv",
        "family_duplicates": outdir / "tables/family_duplicate_classification.tsv",
        "wgd_layers": outdir / "tables/wgd_layers.tsv",
        "wgd_event_evidence": outdir / "tables/wgd_event_evidence.tsv",
        "family_wgd_event_membership": outdir / "tables/family_wgd_event_membership.tsv",
        "family_event_retention_summary": outdir / "tables/family_event_retention_summary.tsv",
        "retention_enrichment": outdir / "tables/retention_enrichment.tsv",
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
