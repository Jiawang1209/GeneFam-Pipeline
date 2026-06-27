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
) -> str:
    return "\n".join(
        [
            "# Analysis Reproducibility Code",
            "",
            "This file records the command-level reproduction path for the current GeneFam-Pipeline analysis.",
            "",
            "## Inputs",
            "",
            f"- Config: `{config}`",
            f"- Clean species manifest: `{clean_species_manifest}`",
            f"- Reference manifest: `{reference_manifest}`",
            f"- Family candidates: `{family_candidates}`",
            "",
            "## 00_preprocess",
            "",
            "```bash",
            "python bin/genefam/discover_species.py \\",
            f"  --config {config} \\",
            "  --groups configs/species_groups.yaml \\",
            "  --base-dir . \\",
            "  --out results/00_preprocess/species_manifest.raw.tsv",
            "",
            "python bin/genefam/preprocess_species.py \\",
            "  --species-manifest results/00_preprocess/species_manifest.raw.tsv \\",
            "  --outdir results/00_preprocess",
            "```",
            "",
            "## Reference Generation",
            "",
            "```bash",
            "python bin/genefam/build_reference_from_config.py \\",
            f"  --config {config} \\",
            f"  --species-manifest {clean_species_manifest} \\",
            "  --base-dir . \\",
            "  --outdir results/00_preprocess/reference",
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
            f"  --config {config} \\",
            "  --groups configs/species_groups.yaml \\",
            "  --run_identification true \\",
            "  --use_hmmer true \\",
            "  --use_diamond true \\",
            "  --final_rule intersection",
            "```",
            "",
            "## Key Outputs",
            "",
            "- `results/00_preprocess/species_manifest.clean.tsv`",
            "- `results/00_preprocess/reference/PF00657.reference.pep.fa`",
            f"- `{family_candidates}`",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--clean-species-manifest", required=True, type=Path)
    parser.add_argument("--reference-manifest", required=True, type=Path)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        build_markdown(args.config, args.clean_species_manifest, args.reference_manifest, args.family_candidates),
        encoding="utf-8",
    )
    print(f"Wrote reproducibility code Markdown: {args.out}")


if __name__ == "__main__":
    main()
