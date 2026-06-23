#!/usr/bin/env python3
"""Run a standard-branch Python smoke test without external bioinformatics tools."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.assemble_report import assemble_report, write_report
from bin.genefam.build_plot_manifest import build_plot_manifest, write_tsv as write_plot_manifest_tsv
from bin.genefam.build_standard_report_index import DESCRIPTIONS, build_report_index, write_tsv as write_report_index_tsv
from bin.genefam.discover_species import _select_species, discover_species, write_manifest
from bin.genefam.extract_family_sequences import extract_family_sequences, read_tsv as read_table, write_fasta
from bin.genefam.extract_chromosome_locations import extract_locations_for_manifest, write_tsv as write_locations_tsv
from bin.genefam.merge_identification_evidence import merge_evidence, read_tsv, write_tsv
from bin.genefam.prepare_alignment_inputs import prepare_alignment_manifest, write_tsv as write_alignment_tsv
from bin.genefam.prepare_phylogeny_inputs import prepare_phylogeny_manifest, write_tsv as write_phylogeny_tsv
from bin.genefam.summarize_family import summarize_candidates, write_tsv as write_summary_tsv
from bin.genefam.run_mock_mvp import _load_yaml


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_standard_smoke(config_path: Path, groups_path: Path, mock_evidence_dir: Path, outdir: Path) -> dict[str, Path]:
    config = _load_yaml(config_path)
    groups = _load_yaml(groups_path) if groups_path and groups_path.exists() else {}
    include, exclude = _select_species(config, groups)
    input_config = config.get("input", {}) or {}
    gene_family = (config.get("gene_family", {}) or {}).get("name", "family")
    project_name = (config.get("project", {}) or {}).get("name", "GeneFam standard smoke")
    final_rule = (config.get("identification", {}) or {}).get("final_rule", "intersection")
    manifest_rows = discover_species(
        root=Path(input_config["root"]),
        include=include,
        exclude=exclude,
        patterns=input_config.get("patterns", {}),
        required=input_config.get("required", {}),
    )

    tables_dir = outdir / "tables"
    sequences_dir = outdir / "sequences"
    report_dir = outdir / "report"
    outputs = {
        "species_manifest": tables_dir / "species_manifest.tsv",
        "family_candidates": tables_dir / "family_candidates.tsv",
        "family_counts": tables_dir / "family_counts.tsv",
        "family_members_faa": sequences_dir / "family_members.faa",
        "alignment_manifest": tables_dir / "alignment_manifest.tsv",
        "phylogeny_manifest": tables_dir / "phylogeny_manifest.tsv",
        "chromosome_locations": tables_dir / "chromosome_locations.tsv",
        "plot_manifest": report_dir / "plot_manifest.tsv",
        "report_index": report_dir / "report_index.tsv",
        "standard_final_report": report_dir / "final_report.md",
    }

    write_manifest(manifest_rows, outputs["species_manifest"])
    candidates = merge_evidence(
        read_tsv(mock_evidence_dir / "hmmer.tsv"),
        read_tsv(mock_evidence_dir / "diamond.tsv"),
        final_rule=final_rule,
    )
    write_tsv(candidates, outputs["family_candidates"])
    write_summary_tsv(summarize_candidates(candidates), outputs["family_counts"])
    write_fasta(extract_family_sequences(candidates, manifest_rows), outputs["family_members_faa"])
    alignment_rows = prepare_alignment_manifest(
        family_name=gene_family,
        fasta_path=outputs["family_members_faa"],
        outdir=outdir / "alignment",
        aligner="mafft",
    )
    write_alignment_tsv(alignment_rows, outputs["alignment_manifest"])
    write_phylogeny_tsv(
        prepare_phylogeny_manifest(alignment_rows, outdir=outdir / "phylogeny", tree_builder="iqtree"),
        outputs["phylogeny_manifest"],
    )
    write_locations_tsv(extract_locations_for_manifest(candidates, manifest_rows), outputs["chromosome_locations"])
    write_plot_manifest_tsv(
        build_plot_manifest([("family_counts", "plots/family_counts.pdf", "Family member counts by species")]),
        outputs["plot_manifest"],
    )
    write_report_index_tsv(
        build_report_index({key: str(outputs[key]) if key in outputs else "" for key in DESCRIPTIONS}),
        outputs["report_index"],
    )
    write_report(
        assemble_report(
            project_name=project_name,
            gene_family=gene_family,
            report_index_rows=read_table(outputs["report_index"]),
            plot_manifest=read_table(outputs["plot_manifest"]),
        ),
        outputs["standard_final_report"],
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--groups", required=True, type=Path)
    parser.add_argument("--mock-evidence-dir", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_standard_smoke(args.config, args.groups, args.mock_evidence_dir, args.outdir))


if __name__ == "__main__":
    main()
