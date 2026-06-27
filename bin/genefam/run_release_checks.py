#!/usr/bin/env python3
"""Run repository release checks and write TSV/Markdown summaries."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.audit_objective_completion import (
    build_objective_audit,
    read_tsv,
    write_markdown as write_objective_markdown,
    write_tsv as write_objective_tsv,
)
from bin.genefam.build_handoff_report import (
    build_handoff_sections,
    read_tsv as read_handoff_tsv,
    write_markdown as write_handoff_markdown,
    write_summary_tsv as write_handoff_summary_tsv,
)
from bin.genefam.run_delivery_bundle import run_delivery_bundle


FIELDNAMES = ["check", "required", "status", "exit_code", "command", "note"]


@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: list[str]
    required: bool = True


def default_checks() -> list[CheckSpec]:
    python = sys.executable
    return [
        CheckSpec("pytest", [python, "-m", "pytest", "tests", "-q"]),
        CheckSpec(
            "validate example config",
            [python, "bin/genefam/validate_config.py", "configs/example.config.yaml", "--check-paths"],
        ),
        CheckSpec(
            "validate advanced config",
            [python, "bin/genefam/validate_config.py", "configs/advanced_modules.example.yaml"],
        ),
        CheckSpec(
            "validate manifest config",
            [python, "bin/genefam/validate_config.py", "configs/manifest.example.yaml", "--check-paths"],
        ),
        CheckSpec(
            "validate publication modules config",
            [
                python,
                "bin/genefam/validate_config.py",
                "configs/publication_modules.example.yaml",
                "--check-paths",
            ],
        ),
        CheckSpec(
            "species selection smoke",
            [
                python,
                "bin/genefam/run_species_selection_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--outdir",
                "results/species_selection_smoke",
            ],
        ),
        CheckSpec(
            "species manifest selection smoke",
            [
                python,
                "bin/genefam/run_species_selection_smoke.py",
                "--config",
                "configs/manifest.example.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--outdir",
                "results/species_manifest_selection_smoke",
            ],
        ),
        CheckSpec(
            "Reference governance audit",
            [
                python,
                "bin/genefam/audit_reference_governance.py",
                "--outdir",
                "results/reference_governance",
            ],
        ),
        CheckSpec(
            "mock MVP",
            [
                python,
                "bin/genefam/run_mock_mvp.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/mock_mvp",
            ],
        ),
        CheckSpec(
            "domain filter smoke",
            [
                python,
                "bin/genefam/run_domain_filter_smoke.py",
                "--input",
                "tests/fixtures/hmmer_domains/domains.tsv",
                "--max-evalue",
                "1e-10",
                "--min-bitscore",
                "50",
                "--min-domain-coverage",
                "0.5",
                "--outdir",
                "results/domain_filter_smoke",
            ],
        ),
        CheckSpec(
            "motif parser smoke",
            [
                python,
                "bin/genefam/run_motif_smoke.py",
                "--meme-txt",
                "tests/fixtures/mock_evidence/meme.txt",
                "--family-name",
                "GDSL",
                "--outdir",
                "results/motif_smoke",
            ],
        ),
        CheckSpec(
            "standard branch smoke",
            [
                python,
                "bin/genefam/run_standard_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/standard_smoke",
            ],
        ),
        CheckSpec(
            "gene structure smoke",
            [
                python,
                "bin/genefam/run_gene_structure_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/gene_structure_smoke",
            ],
        ),
        CheckSpec(
            "chromosome location smoke",
            [
                python,
                "bin/genefam/run_chromosome_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--outdir",
                "results/chromosome_smoke",
            ],
        ),
        CheckSpec(
            "R runtime health",
            [
                python,
                "bin/genefam/check_r_runtime.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/r_runtime_health",
            ],
        ),
        CheckSpec(
            "promoter smoke",
            [
                python,
                "bin/genefam/run_promoter_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/promoter_smoke",
            ],
        ),
        CheckSpec(
            "standard branch expression smoke",
            [
                python,
                "bin/genefam/run_standard_smoke.py",
                "--config",
                "configs/example.config.yaml",
                "--groups",
                "configs/species_groups.yaml",
                "--mock-evidence-dir",
                "tests/fixtures/mock_evidence",
                "--expression-matrix",
                "tests/fixtures/expression/family_expression.tsv",
                "--expression-metadata",
                "tests/fixtures/expression/sample_metadata.tsv",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/standard_expression_smoke",
            ],
        ),
        CheckSpec(
            "expression heatmap visualization smoke",
            [
                python,
                "bin/genefam/run_expression_heatmap_smoke.py",
                "--expression",
                "tests/fixtures/expression/family_expression.tsv",
                "--metadata",
                "tests/fixtures/expression/sample_metadata.tsv",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/expression_heatmap_smoke",
            ],
        ),
        CheckSpec(
            "alignment phylogeny smoke",
            [
                python,
                "bin/genefam/run_alignment_phylogeny_smoke.py",
                "--family-name",
                "GDSL",
                "--fasta",
                "tests/fixtures/alignment/family_members.faa",
                "--aligner",
                "mafft",
                "--tree-builder",
                "iqtree",
                "--outdir",
                "results/alignment_phylogeny_smoke",
            ],
        ),
        CheckSpec(
            "synteny parser smoke",
            [
                python,
                "bin/genefam/run_synteny_smoke.py",
                "--collinearity",
                "tests/fixtures/mcscanx/sample.collinearity",
                "--outdir",
                "results/synteny_smoke",
            ],
        ),
        CheckSpec(
            "MCScanX circlize visualization smoke",
            [
                python,
                "bin/genefam/run_mcscanx_circlize_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/mcscanx_circlize_smoke",
            ],
        ),
        CheckSpec(
            "gene family information visualization smoke",
            [
                python,
                "bin/genefam/run_gene_family_info_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/gene_family_info_smoke",
            ],
        ),
        CheckSpec(
            "feature summary visualization smoke",
            [
                python,
                "bin/genefam/run_feature_summary_smoke.py",
                "--domains",
                "results/domain_filter_smoke/tables/filtered_domains.tsv",
                "--motifs",
                "results/motif_smoke/tables/motif_summary.tsv",
                "--gene-structures",
                "results/gene_structure_smoke/tables/gene_structure_summary.tsv",
                "--synteny",
                "results/synteny_smoke/tables/syntenic_pairs.tsv",
                "--promoters",
                "results/promoter_smoke/tables/promoters.bed",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/feature_summary_smoke",
            ],
        ),
        CheckSpec(
            "promoter cis-element visualization smoke",
            [
                python,
                "bin/genefam/run_promoter_cis_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/promoter_cis_smoke",
            ],
        ),
        CheckSpec(
            "tree feature visualization smoke",
            [
                python,
                "bin/genefam/run_tree_feature_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/tree_feature_smoke",
            ],
        ),
        CheckSpec(
            "PPI ggNetView smoke",
            [
                python,
                "bin/genefam/run_ppi_ggnetview_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/ppi_ggnetview_smoke",
            ],
        ),
        CheckSpec(
            "PPI ggNetView plot smoke",
            [
                python,
                "bin/genefam/run_ppi_ggnetview_plot_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/ppi_ggnetview_plot_smoke",
            ],
        ),
        CheckSpec(
            "Ka/Ks parser smoke",
            [
                python,
                "bin/genefam/run_kaks_smoke.py",
                "--kaks",
                "tests/fixtures/kaks/kaks_calculator.tsv",
                "--outdir",
                "results/kaks_smoke",
            ],
        ),
        CheckSpec(
            "duplicate-type Ka/Ks visualization smoke",
            [
                python,
                "bin/genefam/run_duplicate_type_kaks_smoke.py",
                "--duplicates",
                "examples/prepared_wgd_handoff/duplicate_types.tsv",
                "--kaks-pairs",
                "examples/prepared_wgd_handoff/kaks_pairs.tsv",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/duplicate_type_kaks_smoke",
            ],
        ),
        CheckSpec(
            "pangenome-class Ka/Ks visualization smoke",
            [
                python,
                "bin/genefam/run_pangenome_kaks_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/pangenome_kaks_smoke",
            ],
        ),
        CheckSpec(
            "retention enrichment smoke",
            [
                python,
                "bin/genefam/run_retention_enrichment_smoke.py",
                "--family-members",
                "examples/prepared_wgd_handoff/family_candidates.tsv",
                "--duplicates",
                "examples/prepared_wgd_handoff/duplicate_types.tsv",
                "--outdir",
                "results/retention_enrichment_smoke",
            ],
        ),
        CheckSpec(
            "WGD event smoke",
            [
                python,
                "bin/genefam/run_wgd_smoke.py",
                "--events-config",
                "configs/wgd_events.brassicaceae.yaml",
                "--outdir",
                "results/wgd_smoke",
            ],
        ),
        CheckSpec(
            "Ka/Ks WGD annotation plot smoke",
            [
                python,
                "bin/genefam/run_kaks_wgd_plot_smoke.py",
                "--r-bin",
                "/usr/local/bin/R",
                "--outdir",
                "results/kaks_wgd_plot_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow mock MVP smoke",
            [
                python,
                "bin/genefam/run_nextflow_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow standard branch smoke",
            [
                python,
                "bin/genefam/run_nextflow_standard_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_standard_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow standard visualization smoke",
            [
                python,
                "bin/genefam/run_nextflow_standard_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--config",
                "configs/publication_modules.example.yaml",
                "--outdir",
                "results/nextflow_standard_feature_smoke",
            ],
        ),
        CheckSpec(
            "publication report audit",
            [
                python,
                "bin/genefam/audit_publication_report.py",
                "--plot-manifest",
                "results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv",
                "--figure-interpretations",
                "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv",
                "--software-versions",
                "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
                "--final-report",
                "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
                "--report-index",
                "results/nextflow_standard_feature_smoke/standard/report/report_index.tsv",
                "--out-tsv",
                "results/publication_report_audit/publication_report_audit.tsv",
                "--out-md",
                "results/publication_report_audit/publication_report_audit.md",
            ],
        ),
        CheckSpec(
            "standard report index audit",
            [
                python,
                "bin/genefam/audit_report_index.py",
                "--report-index",
                "results/nextflow_standard_feature_smoke/standard/report/report_index.tsv",
                "--profile",
                "standard",
                "--out-tsv",
                "results/report_index_audit/standard_report_index_audit.tsv",
                "--out-md",
                "results/report_index_audit/standard_report_index_audit.md",
            ],
        ),
        CheckSpec(
            "Nextflow standard manifest smoke",
            [
                python,
                "bin/genefam/run_nextflow_standard_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--config",
                "configs/manifest.example.yaml",
                "--outdir",
                "results/nextflow_standard_manifest_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow standard single-tool smoke",
            [
                python,
                "bin/genefam/run_nextflow_single_tool_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_single_tool_smoke",
            ],
        ),
        CheckSpec(
            "Nextflow WGD event smoke",
            [
                python,
                "bin/genefam/run_nextflow_wgd_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/nextflow_wgd_smoke",
            ],
        ),
        CheckSpec(
            "WGD publication report audit",
            [
                python,
                "bin/genefam/audit_publication_report.py",
                "--plot-manifest",
                "results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv",
                "--figure-interpretations",
                "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv",
                "--software-versions",
                "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
                "--final-report",
                "results/nextflow_wgd_smoke/wgd/report/final_report.md",
                "--report-index",
                "results/nextflow_wgd_smoke/wgd/report/report_index.tsv",
                "--out-tsv",
                "results/publication_report_audit/wgd_publication_report_audit.tsv",
                "--out-md",
                "results/publication_report_audit/wgd_publication_report_audit.md",
            ],
        ),
        CheckSpec(
            "WGD report index audit",
            [
                python,
                "bin/genefam/audit_report_index.py",
                "--report-index",
                "results/nextflow_wgd_smoke/wgd/report/report_index.tsv",
                "--profile",
                "wgd",
                "--out-tsv",
                "results/report_index_audit/wgd_report_index_audit.tsv",
                "--out-md",
                "results/report_index_audit/wgd_report_index_audit.md",
            ],
        ),
        CheckSpec(
            "Reference visual alignment audit",
            [
                python,
                "bin/genefam/audit_reference_visual_alignment.py",
                "--standard-plot-manifest",
                "results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv",
                "--standard-figure-interpretations",
                "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.tsv",
                "--wgd-plot-manifest",
                "results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv",
                "--wgd-figure-interpretations",
                "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv",
                "--out-tsv",
                "results/reference_visual_alignment/reference_visual_alignment.tsv",
                "--out-md",
                "results/reference_visual_alignment/reference_visual_alignment.md",
            ],
        ),
        CheckSpec(
            "Nextflow raw MCScanX/KaKs WGD smoke",
            [
                python,
                "bin/genefam/run_nextflow_wgd_smoke.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--mode",
                "raw-mcscanx-kaks",
                "--outdir",
                "results/nextflow_wgd_raw_smoke",
            ],
        ),
        CheckSpec(
            "prepared WGD handoff example",
            [
                python,
                "bin/genefam/run_prepared_wgd_handoff_example.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--example-dir",
                "examples/prepared_wgd_handoff",
                "--outdir",
                "results/example_prepared_wgd",
            ],
        ),
        CheckSpec(
            "quickstart handoff",
            [
                python,
                "bin/genefam/run_quickstart.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/quickstart",
            ],
        ),
        CheckSpec(
            "delivery bundle figure gallery smoke",
            [
                python,
                "bin/genefam/run_delivery_bundle_smoke.py",
                "--outdir",
                "results/delivery_bundle_smoke",
            ],
        ),
        CheckSpec(
            "delivery bundle figure gallery audit",
            [
                python,
                "bin/genefam/audit_figure_gallery.py",
                "--figure-gallery",
                "results/delivery_bundle_smoke/delivery_bundle/figure_gallery.tsv",
                "--plot-manifest",
                "standard=results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv",
                "--plot-manifest",
                "wgd=results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv",
                "--out-tsv",
                "results/delivery_bundle_smoke/figure_gallery_audit.tsv",
                "--out-md",
                "results/delivery_bundle_smoke/figure_gallery_audit.md",
            ],
        ),
        CheckSpec(
            "delivery bundle manifest audit",
            [
                python,
                "bin/genefam/audit_delivery_manifest.py",
                "--delivery-manifest",
                "results/delivery_bundle_smoke/delivery_bundle/delivery_manifest.tsv",
                "--out-tsv",
                "results/delivery_bundle_smoke/delivery_manifest_audit.tsv",
                "--out-md",
                "results/delivery_bundle_smoke/delivery_manifest_audit.md",
            ],
        ),
        CheckSpec(
            "readiness audit",
            [
                python,
                "bin/genefam/audit_readiness.py",
                "--conda-env",
                "GeneFamilyFlow",
                "--out",
                "results/readiness/command_readiness.tsv",
            ],
        ),
        CheckSpec(
            "runtime bootstrap plan",
            [
                python,
                "bin/genefam/plan_runtime_bootstrap.py",
                "--readiness",
                "results/readiness/command_readiness.tsv",
                "--outdir",
                "results/readiness",
            ],
        ),
        CheckSpec(
            "runtime bootstrap shell syntax",
            [
                "bash",
                "-n",
                "results/readiness/runtime_bootstrap.sh",
            ],
        ),
        CheckSpec(
            "container materials audit",
            [
                python,
                "bin/genefam/audit_container_materials.py",
                "--outdir",
                "results/container_materials",
            ],
        ),
        CheckSpec(
            "Docker profile smoke",
            [
                python,
                "bin/genefam/run_container_profile_smoke.py",
                "--profile",
                "docker",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/container_profile_smoke/docker",
            ],
            required=False,
        ),
        CheckSpec(
            "Apptainer profile smoke",
            [
                python,
                "bin/genefam/run_container_profile_smoke.py",
                "--profile",
                "apptainer",
                "--conda-env",
                "GeneFamilyFlow",
                "--outdir",
                "results/container_profile_smoke/apptainer",
            ],
            required=False,
        ),
    ]


def quick_checks() -> list[CheckSpec]:
    return [CheckSpec("python self check", [sys.executable, "-c", "print('ok')"])]


def _subprocess_runner(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode, output


def _note(output: str) -> str:
    return " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500]


def run_checks(
    checks: list[CheckSpec],
    runner: Callable[[list[str]], tuple[int, str]] = _subprocess_runner,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for check in checks:
        exit_code, output = runner(check.command)
        rows.append(
            {
                "check": check.name,
                "required": "true" if check.required else "false",
                "status": "passed" if exit_code == 0 else "failed",
                "exit_code": str(exit_code),
                "command": " ".join(check.command),
                "note": _note(output),
            }
        )
    return rows


def summarize_checks(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    required_failed = sum(1 for row in rows if row["required"] == "true" and row["status"] == "failed")
    optional_failed = sum(1 for row in rows if row["required"] == "false" and row["status"] == "failed")
    return {
        "passed": passed,
        "failed": failed,
        "required_failed": required_failed,
        "optional_failed": optional_failed,
        "release_ready": required_failed == 0,
    }


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    summary = summarize_checks(rows)
    lines = [
        "# GeneFam-Pipeline Release Checks",
        "",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        f"Required failed: {summary['required_failed']}",
        f"Optional failed: {summary['optional_failed']}",
        f"Release ready: {str(summary['release_ready']).lower()}",
        "",
        "| check | required | status | exit_code | command | note |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        escaped = {key: _markdown_cell(value) for key, value in row.items()}
        lines.append(
            "| {check} | {required} | {status} | {exit_code} | `{command}` | {note} |".format(**escaped)
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_objective_audit(
    rows: list[dict[str, str]],
    readiness_path: Path = Path("results/readiness/command_readiness.tsv"),
    outdir: Path = Path("results/objective_audit"),
    publication_audit_path: Path = Path("results/publication_report_audit/publication_report_audit.tsv"),
    wgd_publication_audit_path: Path = Path("results/publication_report_audit/wgd_publication_report_audit.tsv"),
) -> bool:
    if not readiness_path.exists():
        return False
    objective_rows = build_objective_audit(
        rows,
        read_tsv(readiness_path),
        publication_audit_rows=read_tsv(publication_audit_path) if publication_audit_path.exists() else None,
        wgd_publication_audit_rows=read_tsv(wgd_publication_audit_path)
        if wgd_publication_audit_path.exists()
        else None,
    )
    write_objective_tsv(objective_rows, outdir / "objective_audit.tsv")
    write_objective_markdown(objective_rows, outdir / "objective_audit.md")
    return True


def write_handoff_report(
    release_checks_path: Path = Path("results/release_checks/release_checks.tsv"),
    objective_audit_path: Path = Path("results/objective_audit/objective_audit.tsv"),
    readiness_path: Path = Path("results/readiness/command_readiness.tsv"),
    container_smoke_paths: list[Path] | None = None,
    out_path: Path = Path("results/handoff/handoff_report.md"),
    summary_tsv_path: Path = Path("results/handoff/handoff_summary.tsv"),
) -> bool:
    if not release_checks_path.exists():
        return False
    smoke_paths = container_smoke_paths or [
        Path("results/container_profile_smoke/docker/container_profile_smoke.tsv"),
        Path("results/container_profile_smoke/apptainer/container_profile_smoke.tsv"),
    ]
    container_rows: list[dict[str, str]] = []
    for path in smoke_paths:
        container_rows.extend(read_handoff_tsv(path))
    sections = build_handoff_sections(
        release_rows=read_handoff_tsv(release_checks_path),
        objective_rows=read_handoff_tsv(objective_audit_path),
        readiness_rows=read_handoff_tsv(readiness_path),
        container_rows=container_rows,
    )
    write_handoff_markdown(sections, out_path)
    write_handoff_summary_tsv(sections, summary_tsv_path)
    return True


def write_delivery_bundle(
    release_checks_path: Path = Path("results/release_checks/release_checks.tsv"),
    objective_audit_path: Path = Path("results/objective_audit/objective_audit.tsv"),
    readiness_path: Path = Path("results/readiness/command_readiness.tsv"),
    quickstart_path: Path = Path("results/quickstart/quickstart_summary.tsv"),
    outdir: Path = Path("results/delivery_bundle"),
) -> bool:
    if not release_checks_path.exists():
        return False
    run_delivery_bundle(
        release_checks=release_checks_path,
        objective_audit=objective_audit_path,
        readiness=readiness_path,
        quickstart=quickstart_path,
        outdir=outdir,
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="results/release_checks", type=Path)
    parser.add_argument("--quick-self-check", action="store_true")
    args = parser.parse_args()
    checks = quick_checks() if args.quick_self_check else default_checks()
    rows = run_checks(checks)
    write_tsv(rows, args.outdir / "release_checks.tsv")
    write_markdown(rows, args.outdir / "release_checks.md")
    if not args.quick_self_check:
        write_objective_audit(rows)
        write_delivery_bundle(args.outdir / "release_checks.tsv")
        write_handoff_report(args.outdir / "release_checks.tsv")
    sys.exit(0 if summarize_checks(rows)["release_ready"] else 1)


if __name__ == "__main__":
    main()
