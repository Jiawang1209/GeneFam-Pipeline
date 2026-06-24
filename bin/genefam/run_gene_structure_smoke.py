#!/usr/bin/env python3
"""Run a small gene-structure extraction smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.discover_species import _select_species, discover_species, write_manifest
from bin.genefam.extract_gene_structure import summarize_structure, write_tsv as write_structure_tsv
from bin.genefam.merge_identification_evidence import merge_evidence, read_tsv, write_tsv as write_candidates_tsv
from bin.genefam.run_mock_mvp import _load_yaml


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_gene_structure_smoke(
    config_path: Path,
    groups_path: Path,
    mock_evidence_dir: Path,
    outdir: Path,
) -> dict[str, Path]:
    outputs = {
        "species_manifest": outdir / "tables/species_manifest.tsv",
        "family_candidates": outdir / "tables/family_candidates.tsv",
        "gene_structure_summary": outdir / "tables/gene_structure_summary.tsv",
        "summary": outdir / "gene_structure_smoke.md",
    }
    config = _load_yaml(config_path)
    groups = _load_yaml(groups_path) if groups_path and groups_path.exists() else {}
    include, exclude = _select_species(config, groups)
    input_config = config.get("input", {}) or {}
    final_rule = (config.get("identification", {}) or {}).get("final_rule", "intersection")
    manifest_rows = discover_species(
        root=Path(input_config["root"]),
        include=include,
        exclude=exclude,
        patterns=input_config.get("patterns", {}),
        required=input_config.get("required", {}),
    )
    candidates = merge_evidence(
        read_tsv(mock_evidence_dir / "hmmer.tsv"),
        read_tsv(mock_evidence_dir / "diamond.tsv"),
        final_rule=final_rule,
    )
    structure_rows = summarize_structure(candidates, manifest_rows)

    write_manifest(manifest_rows, outputs["species_manifest"])
    write_candidates_tsv(candidates, outputs["family_candidates"])
    write_structure_tsv(structure_rows, outputs["gene_structure_summary"])
    species_count = len({row["species_id"] for row in structure_rows})
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Gene Structure Smoke",
                "",
                f"Config: `{config_path}`",
                f"Structured genes: {len(structure_rows)}",
                f"Species represented: {species_count}",
                f"Output: `{outputs['gene_structure_summary']}`",
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
    _print_outputs(run_gene_structure_smoke(args.config, args.groups, args.mock_evidence_dir, args.outdir))


if __name__ == "__main__":
    main()
