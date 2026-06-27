#!/usr/bin/env python3
"""Write a Markdown file containing the commands needed to reproduce an analysis run."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_markdown(
    config: Path,
    clean_species_manifest: Path,
    reference_manifest: Path,
    family_candidates: Path,
    config_label: str | None = None,
    groups_label: str = "configs/species_groups.yaml",
    outdir: str = "results/standard",
    preprocess_outdir: str = "results/00_preprocess",
    clean_species_manifest_label: str | None = None,
    reference_manifest_label: str | None = None,
    family_candidates_label: str | None = None,
) -> str:
    config_for_command = config_label or str(config)
    clean_species_manifest_for_report = clean_species_manifest_label or str(clean_species_manifest)
    reference_manifest_for_report = reference_manifest_label or str(reference_manifest)
    family_candidates_for_report = family_candidates_label or str(family_candidates)
    return "\n".join(
        [
            "# Analysis Reproducibility Code",
            "",
            "This file records the command-level reproduction path for the current GeneFam-Pipeline analysis.",
            "",
            "## Inputs",
            "",
            f"- Config: `{config_for_command}`",
            f"- Groups: `{groups_label}`",
            f"- Standard output directory: `{outdir}`",
            f"- Preprocess output directory: `{preprocess_outdir}`",
            f"- Clean species manifest: `{clean_species_manifest_for_report}`",
            f"- Reference manifest: `{reference_manifest_for_report}`",
            f"- Family candidates: `{family_candidates_for_report}`",
            "",
            "## 00_preprocess",
            "",
            "```bash",
            "python bin/genefam/discover_species.py \\",
            f"  --config {config_for_command} \\",
            f"  --groups {groups_label} \\",
            "  --base-dir . \\",
            f"  --out {preprocess_outdir}/species_manifest.raw.tsv",
            "",
            "python bin/genefam/preprocess_species.py \\",
            f"  --species-manifest {preprocess_outdir}/species_manifest.raw.tsv \\",
            f"  --outdir {preprocess_outdir}",
            "```",
            "",
            "## Reference Generation",
            "",
            "```bash",
            "python bin/genefam/build_reference_from_config.py \\",
            f"  --config {config_for_command} \\",
            f"  --species-manifest {preprocess_outdir}/species_manifest.clean.tsv \\",
            "  --base-dir . \\",
            f"  --outdir {preprocess_outdir}/reference",
            "```",
            "",
            reference_manifest.read_text(encoding="utf-8").strip(),
            "",
            "## Standard Nextflow Run",
            "",
            "```bash",
            'PATH="/Users/liuyue/miniforge3/envs/GeneFamilyFlow/bin:$PATH" \\',
            "nextflow run workflows/main.nf \\",
            "  -c workflows/nextflow.config \\",
            "  -profile activated \\",
            f"  --config {config_for_command} \\",
            f"  --groups {groups_label} \\",
            "  --run_identification true \\",
            "  --use_hmmer true \\",
            "  --use_diamond true \\",
            "  --final_rule intersection \\",
            f"  --outdir {outdir} \\",
            f"  --preprocess_outdir {preprocess_outdir}",
            "```",
            "",
            "## Key Outputs",
            "",
            f"- `{preprocess_outdir}/species_manifest.clean.tsv`",
            f"- `{preprocess_outdir}/reference/PF00657.reference.pep.fa`",
            f"- `{family_candidates_for_report}`",
            f"- `{outdir}/report/final_report.md`",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--clean-species-manifest", required=True, type=Path)
    parser.add_argument("--reference-manifest", required=True, type=Path)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--config-label")
    parser.add_argument("--groups-label", default="configs/species_groups.yaml")
    parser.add_argument("--outdir", default="results/standard")
    parser.add_argument("--preprocess-outdir", default="results/00_preprocess")
    parser.add_argument("--clean-species-manifest-label")
    parser.add_argument("--reference-manifest-label")
    parser.add_argument("--family-candidates-label")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        build_markdown(
            args.config,
            args.clean_species_manifest,
            args.reference_manifest,
            args.family_candidates,
            config_label=args.config_label,
            groups_label=args.groups_label,
            outdir=args.outdir,
            preprocess_outdir=args.preprocess_outdir,
            clean_species_manifest_label=args.clean_species_manifest_label,
            reference_manifest_label=args.reference_manifest_label,
            family_candidates_label=args.family_candidates_label,
        ),
        encoding="utf-8",
    )
    print(f"Wrote reproducibility code Markdown: {args.out}")


if __name__ == "__main__":
    main()
