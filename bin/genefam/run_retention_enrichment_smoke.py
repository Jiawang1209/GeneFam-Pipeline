#!/usr/bin/env python3
"""Run a small duplicate-retention enrichment smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.join_family_duplicates import join_family_duplicates, write_tsv as write_family_duplicates_tsv
from bin.genefam.normalize_duplicate_types import normalize_duplicate_rows, read_tsv, write_tsv as write_duplicates_tsv
from bin.genefam.retention_enrichment import compute_enrichment, write_tsv as write_enrichment_tsv


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_retention_enrichment_smoke(
    family_members: Path,
    duplicates: Path,
    outdir: Path,
) -> dict[str, Path]:
    outputs = {
        "normalized_duplicates": outdir / "tables/normalized_duplicate_types.tsv",
        "family_duplicates": outdir / "tables/family_duplicate_classification.tsv",
        "retention_enrichment": outdir / "tables/retention_enrichment.tsv",
        "summary": outdir / "retention_enrichment_smoke.md",
    }

    family_rows = read_tsv(family_members)
    duplicate_rows = read_tsv(duplicates)
    normalized_duplicates = normalize_duplicate_rows(duplicate_rows)
    family_duplicates = join_family_duplicates(family_rows, normalized_duplicates)
    enrichment = compute_enrichment(family_duplicates, normalized_duplicates)

    write_duplicates_tsv(normalized_duplicates, outputs["normalized_duplicates"])
    write_family_duplicates_tsv(family_duplicates, outputs["family_duplicates"])
    write_enrichment_tsv(enrichment, outputs["retention_enrichment"])
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Retention Enrichment Smoke",
                "",
                f"Family members: `{family_members}`",
                f"Duplicate classifications: `{duplicates}`",
                f"Family genes: {len(family_duplicates)}",
                f"Background genes: {len(normalized_duplicates)}",
                f"Enrichment rows: {len(enrichment)}",
                f"Output: `{outputs['retention_enrichment']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-members", required=True, type=Path)
    parser.add_argument("--duplicates", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_retention_enrichment_smoke(args.family_members, args.duplicates, args.outdir))


if __name__ == "__main__":
    main()
