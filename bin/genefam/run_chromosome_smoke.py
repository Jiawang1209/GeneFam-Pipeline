#!/usr/bin/env python3
"""Run a small chromosome-location extraction smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.discover_species import species_rows_from_config, write_manifest
from bin.genefam.extract_chromosome_locations import extract_locations_for_manifest, write_tsv as write_locations_tsv
from bin.genefam.merge_identification_evidence import merge_evidence, read_tsv, write_tsv as write_candidates_tsv
from bin.genefam.run_mock_mvp import _load_yaml


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_chromosome_smoke(
    config_path: Path,
    groups_path: Path,
    mock_evidence_dir: Path,
    outdir: Path,
) -> dict[str, Path]:
    outputs = {
        "species_manifest": outdir / "tables/species_manifest.tsv",
        "family_candidates": outdir / "tables/family_candidates.tsv",
        "chromosome_locations": outdir / "tables/chromosome_locations.tsv",
        "summary": outdir / "chromosome_smoke.md",
    }
    config = _load_yaml(config_path)
    groups = _load_yaml(groups_path) if groups_path and groups_path.exists() else {}
    final_rule = (config.get("identification", {}) or {}).get("final_rule", "intersection")
    manifest_rows = species_rows_from_config(config, groups)
    candidates = merge_evidence(
        read_tsv(mock_evidence_dir / "hmmer.tsv"),
        read_tsv(mock_evidence_dir / "diamond.tsv"),
        final_rule=final_rule,
    )
    locations = extract_locations_for_manifest(candidates, manifest_rows)

    write_manifest(manifest_rows, outputs["species_manifest"])
    write_candidates_tsv(candidates, outputs["family_candidates"])
    write_locations_tsv(locations, outputs["chromosome_locations"])
    species_count = len({row["species_id"] for row in locations})
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Chromosome Location Smoke",
                "",
                f"Config: `{config_path}`",
                f"Located genes: {len(locations)}",
                f"Species represented: {species_count}",
                f"Output: `{outputs['chromosome_locations']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--groups", required=True, type=Path)
    parser.add_argument("--mock-evidence-dir", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_chromosome_smoke(args.config, args.groups, args.mock_evidence_dir, args.outdir))


if __name__ == "__main__":
    main()
