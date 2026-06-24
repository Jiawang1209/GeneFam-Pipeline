#!/usr/bin/env python3
"""Run a small YAML-driven species-bank selection smoke check."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_run_plan import build_run_plan, write_tsv as write_run_plan_tsv
from bin.genefam.discover_species import _load_yaml, _select_species, discover_species, write_manifest


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_species_selection_smoke(
    config_path: Path,
    groups_path: Path,
    outdir: Path,
) -> dict[str, Path]:
    outputs = {
        "species_manifest": outdir / "tables/species_manifest.tsv",
        "run_plan": outdir / "tables/run_plan.tsv",
        "summary": outdir / "species_selection_smoke.md",
    }
    config = _load_yaml(config_path)
    groups = _load_yaml(groups_path) if groups_path and groups_path.exists() else {}
    include, exclude = _select_species(config, groups)
    input_config = config.get("input", {}) or {}
    manifest_rows = discover_species(
        root=Path(input_config["root"]),
        include=include,
        exclude=exclude,
        patterns=input_config.get("patterns", {}),
        required=input_config.get("required", {}),
    )
    write_manifest(manifest_rows, outputs["species_manifest"])
    write_run_plan_tsv(build_run_plan(config), outputs["run_plan"])

    species_ids = [row["species_id"] for row in manifest_rows]
    outputs["summary"].parent.mkdir(parents=True, exist_ok=True)
    outputs["summary"].write_text(
        "\n".join(
            [
                "# Species Selection Smoke",
                "",
                f"Config: `{config_path}`",
                f"Groups: `{groups_path}`",
                f"Species bank: `{input_config.get('root', '')}`",
                f"Selected species: {len(species_ids)}",
                ", ".join(species_ids),
                f"Species manifest: `{outputs['species_manifest']}`",
                f"Run plan: `{outputs['run_plan']}`",
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
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_species_selection_smoke(args.config, args.groups, args.outdir))


if __name__ == "__main__":
    main()
