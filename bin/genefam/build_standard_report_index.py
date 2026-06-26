#!/usr/bin/env python3
"""Build a report index for the standard identification branch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "path", "status", "description"]
DESCRIPTIONS = {
    "species_manifest": "Selected species and input files",
    "run_config_snapshot": "Run configuration and selected species snapshot",
    "family_candidates": "Merged family candidate members",
    "family_counts": "Per-species family member counts",
    "family_members_faa": "Family member peptide FASTA",
    "alignment_manifest": "Alignment preparation manifest",
    "alignment_file": "Multiple sequence alignment FASTA",
    "phylogeny_manifest": "Phylogeny preparation manifest",
    "phylogeny_tree": "Phylogenetic tree file",
    "motif_summary": "MEME motif summary table",
    "gene_structure_summary": "Gene structure summary from GFF3 annotation",
    "chromosome_locations": "Family member chromosome coordinates",
    "promoters_bed": "Promoter coordinate BED table",
    "promoters_fasta": "Promoter sequence FASTA",
    "feature_summary": "Combined domain, motif, gene-structure, synteny, and promoter feature statistics",
    "feature_summary_pdf": "Feature summary PDF plot",
    "feature_summary_png": "Feature summary PNG plot",
    "mcscanx_circlize_pdf": "MCScanX syntenic-link circlize PDF plot",
    "mcscanx_circlize_png": "MCScanX syntenic-link circlize PNG plot",
    "family_expression": "Family member RNA-seq expression matrix",
    "wgd_handoff_manifest": "Standard-to-WGD handoff manifest for duplication and WGD event analysis",
    "plot_manifest": "Generated plot inventory",
    "software_versions": "Software and R package version table for methods reporting",
    "figure_interpretations": "Structured per-figure result interpretation notes",
}
OPTIONAL_KEYS = {
    "promoters_bed",
    "promoters_fasta",
    "feature_summary",
    "feature_summary_pdf",
    "feature_summary_png",
    "mcscanx_circlize_pdf",
    "mcscanx_circlize_png",
    "family_expression",
}


def build_report_index(paths: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "path": paths[key],
            "status": "available" if paths[key] else "missing",
            "description": DESCRIPTIONS[key],
        }
        for key in DESCRIPTIONS
    ]


def published_paths(
    published_outdir: str,
    family_expression_available: bool,
    promoter_available: bool = False,
    feature_summary_available: bool = False,
    mcscanx_circlize_available: bool = False,
) -> dict[str, str]:
    outdir = Path(published_outdir)
    return {
        "species_manifest": str(outdir / "tables/species_manifest.tsv"),
        "run_config_snapshot": str(outdir / "tables/run_config_snapshot.tsv"),
        "family_candidates": str(outdir / "tables/family_candidates.tsv"),
        "family_counts": str(outdir / "tables/family_counts.tsv"),
        "family_members_faa": str(outdir / "sequences/family_members.faa"),
        "alignment_manifest": str(outdir / "tables/alignment_manifest.tsv"),
        "alignment_file": str(outdir / "alignment/GDSL.mafft.aln.faa"),
        "phylogeny_manifest": str(outdir / "tables/phylogeny_manifest.tsv"),
        "phylogeny_tree": str(outdir / "phylogeny/GDSL.fasttree.treefile"),
        "motif_summary": str(outdir / "tables/motif_summary.tsv"),
        "gene_structure_summary": str(outdir / "tables/gene_structure_summary.tsv"),
        "chromosome_locations": str(outdir / "tables/chromosome_locations.tsv"),
        "promoters_bed": str(outdir / "tables/promoters.bed") if promoter_available else "",
        "promoters_fasta": str(outdir / "sequences/promoters.fa") if promoter_available else "",
        "feature_summary": str(outdir / "tables/feature_summary.tsv") if feature_summary_available else "",
        "feature_summary_pdf": str(outdir / "plots/feature_summary.pdf") if feature_summary_available else "",
        "feature_summary_png": str(outdir / "plots/feature_summary.png") if feature_summary_available else "",
        "mcscanx_circlize_pdf": str(outdir / "plots/mcscanx_circlize.pdf") if mcscanx_circlize_available else "",
        "mcscanx_circlize_png": str(outdir / "plots/mcscanx_circlize.png") if mcscanx_circlize_available else "",
        "family_expression": str(outdir / "tables/family_expression.tsv") if family_expression_available else "",
        "wgd_handoff_manifest": str(outdir / "tables/wgd_handoff_manifest.tsv"),
        "plot_manifest": str(outdir / "report/plot_manifest.tsv"),
        "software_versions": str(outdir / "report/software_versions.tsv"),
        "figure_interpretations": str(outdir / "report/figure_interpretations.tsv"),
    }


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
    for key in DESCRIPTIONS:
        parser.add_argument(f"--{key.replace('_', '-')}", default="", required=key not in OPTIONAL_KEYS)
    parser.add_argument("--published-outdir", default=None)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in DESCRIPTIONS}
    if args.published_outdir:
        paths = published_paths(
            args.published_outdir,
            family_expression_available=bool(paths["family_expression"]),
            promoter_available=bool(paths["promoters_bed"] or paths["promoters_fasta"]),
            feature_summary_available=bool(paths["feature_summary"] or paths["feature_summary_pdf"] or paths["feature_summary_png"]),
            mcscanx_circlize_available=bool(paths["mcscanx_circlize_pdf"] or paths["mcscanx_circlize_png"]),
        )
    write_tsv(build_report_index(paths), args.out)


if __name__ == "__main__":
    main()
