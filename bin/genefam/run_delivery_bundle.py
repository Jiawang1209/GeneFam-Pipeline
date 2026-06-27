#!/usr/bin/env python3
"""Build the final user-facing delivery manifest for GeneFam-Pipeline."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["section", "item", "status", "path", "note"]
FIGURE_GALLERY_FIELDNAMES = [
    "branch",
    "plot_key",
    "plot_path",
    "plot_png_path",
    "plot_description",
    "figure_interpretations",
    "software_versions",
    "final_report",
    "traceability_matrix",
]


FIGURE_GALLERY_ROWS = [
    {
        "branch": "standard",
        "plot_key": "family_counts",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/family_counts.pdf",
        "plot_description": "Family member counts by species",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "gene_family_info_summary",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/gene_family_info_summary.pdf",
        "plot_description": "Gene family copy-number and protein-property summary",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "gene_family_pangenome_summary",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/gene_family_info_summary.pdf",
        "plot_description": "Gene family pangenome presence and copy-number balance",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "tree_features",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/tree_features.pdf",
        "plot_description": "Tree, motif, gene-structure, and domain composite plot",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "feature_summary",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/feature_summary.pdf",
        "plot_description": "Integrated domain, motif, gene-structure, synteny, promoter, and expression feature summary",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "mcscanx_circlize",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/mcscanx_circlize.pdf",
        "plot_description": "MCScanX synteny and chromosome-scale circlize plot",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "promoter_cis_elements",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/promoter_cis_elements.pdf",
        "plot_description": "Promoter cis-element category matrix and top element summary",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "ppi_ggnetview",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/ppi_ggnetview.pdf",
        "plot_description": "PPI network generated with ggNetView",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "standard",
        "plot_key": "expression_heatmap",
        "plot_path": "results/nextflow_standard_feature_smoke/standard/plots/expression_heatmap.pdf",
        "plot_description": "Family member expression heatmap",
        "figure_interpretations": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
        "software_versions": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "final_report": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
    },
    {
        "branch": "wgd",
        "plot_key": "ks_distribution",
        "plot_path": "results/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf",
        "plot_description": "Ks distribution for duplicated pairs and WGD layer interpretation",
        "figure_interpretations": "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md",
        "software_versions": "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
        "final_report": "results/nextflow_wgd_smoke/wgd/report/final_report.md",
    },
    {
        "branch": "wgd",
        "plot_key": "duplicate_type_kaks",
        "plot_path": "results/nextflow_wgd_smoke/wgd/plots/duplicate_type_kaks.pdf",
        "plot_description": "Duplicate-type grouped Ks and Ka/Ks selection overview",
        "figure_interpretations": "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md",
        "software_versions": "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
        "final_report": "results/nextflow_wgd_smoke/wgd/report/final_report.md",
    },
    {
        "branch": "wgd",
        "plot_key": "pangenome_kaks",
        "plot_path": "results/nextflow_wgd_smoke/wgd/plots/pangenome_kaks.pdf",
        "plot_description": "Pangenome-class grouped Ks and Ka/Ks selection overview",
        "figure_interpretations": "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md",
        "software_versions": "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
        "final_report": "results/nextflow_wgd_smoke/wgd/report/final_report.md",
    },
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _status_from_step(rows: list[dict[str, str]], step: str) -> str:
    for row in rows:
        if row.get("step") == step:
            return "available" if row.get("status") == "passed" else "missing"
    return "missing"


def _status_from_check(rows: list[dict[str, str]], check: str) -> str:
    for row in rows:
        if row.get("check") == check:
            return "available" if row.get("status") == "passed" else "missing"
    return "missing"


def _path_from_step(rows: list[dict[str, str]], step: str, fallback: str) -> str:
    for row in rows:
        if row.get("step") == step and row.get("path"):
            return row["path"]
    return fallback


def _note_from_step(rows: list[dict[str, str]], step: str, fallback: str) -> str:
    for row in rows:
        if row.get("step") == step and row.get("note"):
            return row["note"]
    return fallback


def _readiness_by_command(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("command", ""): row for row in rows}


def _runtime_status(status: str) -> str:
    if status.startswith("available"):
        return "available"
    if status == "missing":
        return "missing"
    return status or "unknown"


def _objective_blockers(rows: list[dict[str, str]]) -> str:
    blockers = [
        row.get("requirement", "")
        for row in rows
        if row.get("status") in {"blocked", "missing"} and row.get("requirement")
    ]
    return ", ".join(blockers) if blockers else "none"


def _objective_blocker_status(rows: list[dict[str, str]]) -> str:
    statuses = {row.get("status") for row in rows if row.get("status") in {"blocked", "missing"}}
    if "blocked" in statuses:
        return "blocked"
    if "missing" in statuses:
        return "missing"
    return "available"


def _optional_failed(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if row.get("required") == "false" and row.get("status") == "failed")


def build_delivery_manifest(
    release_rows: list[dict[str, str]],
    objective_rows: list[dict[str, str]],
    readiness_rows: list[dict[str, str]],
    quickstart_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    readiness = _readiness_by_command(readiness_rows)
    release_failed = sum(1 for row in release_rows if row.get("status") == "failed")
    release_required_failed = sum(
        1 for row in release_rows if row.get("required") == "true" and row.get("status") == "failed"
    )
    release_ready = release_required_failed == 0
    optional_failed = _optional_failed(release_rows)
    blockers = _objective_blockers(objective_rows)
    local_acceptance_status = _objective_blocker_status(objective_rows)
    local_acceptance_note = (
        "compact local acceptance pass/fail index; overall=blocked; final_stage_blocker=" + blockers
        if local_acceptance_status in {"blocked", "missing"}
        else "compact local acceptance pass/fail index; overall=passed; final_stage_blocker=none"
    )

    rows = [
        {
            "section": "status",
            "item": "release_checks",
            "status": "available",
            "path": "results/release_checks/release_checks.md",
            "note": f"failed={release_failed}; required_failed={release_required_failed}",
        },
        {
            "section": "status",
            "item": "release_ready",
            "status": "available" if release_ready else "missing",
            "path": "results/release_checks/release_checks.md",
            "note": f"release_ready={str(release_ready).lower()}; optional_failed={optional_failed}",
        },
        {
            "section": "status",
            "item": "r_runtime_health",
            "status": _status_from_check(release_rows, "R runtime health"),
            "path": "results/r_runtime_health/r_runtime_health.md",
            "note": "/usr/local/bin/R startup health before R plotting smokes",
        },
        {
            "section": "status",
            "item": "objective_audit",
            "status": "available",
            "path": "results/objective_audit/objective_audit.md",
            "note": f"blocked_or_missing={blockers}",
        },
        {
            "section": "status",
            "item": "final_stage_blocker",
            "status": _objective_blocker_status(objective_rows),
            "path": "results/objective_audit/objective_audit.md",
            "note": blockers,
        },
        {
            "section": "status",
            "item": "local_acceptance_summary",
            "status": local_acceptance_status,
            "path": "results/local_acceptance/local_acceptance_summary.md",
            "note": local_acceptance_note,
        },
        {
            "section": "status",
            "item": "publication_report_audit",
            "status": _status_from_check(release_rows, "publication report audit"),
            "path": "results/publication_report_audit/publication_report_audit.md",
            "note": "paper-style report closure: valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete per-figure close-reading text, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands",
        },
        {
            "section": "status",
            "item": "standard_report_index_audit",
            "status": _status_from_check(release_rows, "standard report index audit"),
            "path": "results/report_index_audit/standard_report_index_audit.md",
            "note": "report-index closure: standard report index exposes plot manifest, software versions, figure interpretations in TSV/Markdown, and final report",
        },
        {
            "section": "status",
            "item": "wgd_publication_report_audit",
            "status": _status_from_check(release_rows, "WGD publication report audit"),
            "path": "results/publication_report_audit/wgd_publication_report_audit.md",
            "note": "WGD report closure: valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, complete Ka/Ks/WGD figure close-reading text, gamma beta alpha theta interpretation, QC tables and warnings, software/R package versions, per-figure method/software version coverage, and reproducibility commands",
        },
        {
            "section": "status",
            "item": "wgd_report_index_audit",
            "status": _status_from_check(release_rows, "WGD report index audit"),
            "path": "results/report_index_audit/wgd_report_index_audit.md",
            "note": "report-index closure: WGD report index exposes plot manifest, software versions, figure interpretations in TSV/Markdown, and final report",
        },
        {
            "section": "input",
            "item": "manifest_config",
            "status": "available",
            "path": "configs/manifest.example.yaml",
            "note": "manifest-mode YAML example",
        },
        {
            "section": "input",
            "item": "species_bank_config",
            "status": "available",
            "path": "configs/example.config.yaml",
            "note": "species-bank YAML example with selected species",
        },
        {
            "section": "input",
            "item": "manifest_fixture",
            "status": "available",
            "path": "tests/fixtures/species_manifest.tsv",
            "note": "prebuilt species manifest fixture",
        },
        {
            "section": "input",
            "item": "manifest_selection_smoke",
            "status": "available",
            "path": "results/species_manifest_selection_smoke/tables/species_manifest.tsv",
            "note": "manifest-mode selected species",
        },
        {
            "section": "nextflow",
            "item": "nextflow_mock_mvp_smoke",
            "status": _status_from_check(release_rows, "Nextflow mock MVP smoke"),
            "path": "results/nextflow_smoke/nextflow_smoke.md",
            "note": "Nextflow mock MVP smoke for the baseline workflow",
        },
        {
            "section": "nextflow",
            "item": "nextflow_standard_manifest_smoke",
            "status": _status_from_check(release_rows, "Nextflow standard manifest smoke"),
            "path": "results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv",
            "note": "manifest-mode standard DSL2 smoke",
        },
        {
            "section": "nextflow",
            "item": "nextflow_single_tool_smoke",
            "status": _status_from_check(release_rows, "Nextflow standard single-tool smoke"),
            "path": "results/nextflow_single_tool_smoke/nextflow_single_tool_smoke.tsv",
            "note": "HMMER-only and DIAMOND-only standard workflow routing smoke",
        },
        {
            "section": "nextflow",
            "item": "config_preflight",
            "status": "available",
            "path": "workflows/modules/config_validation.nf",
            "note": "strict config path preflight before Nextflow branches",
        },
        {
            "section": "standard",
            "item": "final_report",
            "status": _status_from_step(quickstart_rows, "standard_branch_smoke"),
            "path": _path_from_step(
                quickstart_rows,
                "standard_branch_smoke",
                "results/quickstart/standard_smoke/report/final_report.md",
            ),
            "note": _note_from_step(quickstart_rows, "standard_branch_smoke", "standard gene-family report"),
        },
        {
            "section": "standard",
            "item": "mock_mvp",
            "status": _status_from_check(release_rows, "mock MVP"),
            "path": "results/mock_mvp/report/final_report.md",
            "note": "Python mock MVP baseline with family candidates, counts, FASTA, and report outputs",
        },
        {
            "section": "standard",
            "item": "family_candidates",
            "status": "available",
            "path": "results/quickstart/standard_smoke/tables/family_candidates.tsv",
            "note": "species-bank candidates selected from YAML",
        },
        {
            "section": "standard",
            "item": "run_config_snapshot",
            "status": "available",
            "path": "results/quickstart/standard_smoke/tables/run_config_snapshot.tsv",
            "note": "standard branch run configuration",
        },
        {
            "section": "standard",
            "item": "wgd_handoff_manifest",
            "status": "available",
            "path": "results/quickstart/standard_smoke/tables/wgd_handoff_manifest.tsv",
            "note": "standard-to-WGD handoff checklist",
        },
        {
            "section": "standard",
            "item": "paper_level_visual_report",
            "status": "available",
            "path": "results/nextflow_standard_feature_smoke/standard/report/final_report.md",
            "note": "paper-level standard visualization report with tree/motif/gene-structure/domain, MCScanX/circlize, promoter cis-elements, expression heatmap, copy number, feature summary, and ggNetView PPI",
        },
        {
            "section": "standard",
            "item": "paper_level_plot_manifest",
            "status": "available",
            "path": "results/nextflow_standard_feature_smoke/standard/report/plot_manifest.tsv",
            "note": "registered plot inventory for the full standard visualization branch",
        },
        {
            "section": "standard",
            "item": "paper_level_figure_interpretations",
            "status": "available",
            "path": "results/nextflow_standard_feature_smoke/standard/report/figure_interpretations.md",
            "note": "per-figure close reading for the full standard visualization branch",
        },
        {
            "section": "standard",
            "item": "paper_level_software_versions",
            "status": "available",
            "path": "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
            "note": "software and R package versions for the full standard visualization branch",
        },
        {
            "section": "wgd",
            "item": "final_report",
            "status": _status_from_step(quickstart_rows, "prepared_wgd_handoff"),
            "path": _path_from_step(
                quickstart_rows,
                "prepared_wgd_handoff",
                "results/quickstart/example_prepared_wgd/report/final_report.md",
            ),
            "note": _note_from_step(quickstart_rows, "prepared_wgd_handoff", "prepared WGD handoff report"),
        },
        {
            "section": "wgd",
            "item": "run_config_snapshot",
            "status": "available",
            "path": "results/quickstart/example_prepared_wgd/tables/wgd_run_config_snapshot.tsv",
            "note": "WGD branch run configuration",
        },
        {
            "section": "wgd",
            "item": "wgd_paper_level_visual_report",
            "status": "available",
            "path": "results/nextflow_wgd_smoke/wgd/report/final_report.md",
            "note": "paper-level Nextflow WGD report with Ka/Ks, Ks-derived WGD layers, gamma beta alpha theta event interpretation, retention enrichment, duplicate-type selection, and pangenome-class selection",
        },
        {
            "section": "wgd",
            "item": "wgd_paper_level_plot_manifest",
            "status": "available",
            "path": "results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv",
            "note": "registered plot inventory for the formal Nextflow WGD branch",
        },
        {
            "section": "wgd",
            "item": "wgd_paper_level_figure_interpretations",
            "status": "available",
            "path": "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md",
            "note": "per-figure close reading for the formal Nextflow WGD branch",
        },
        {
            "section": "wgd",
            "item": "wgd_paper_level_software_versions",
            "status": "available",
            "path": "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
            "note": "software and R package versions for the formal Nextflow WGD branch",
        },
        {
            "section": "wgd",
            "item": "events_config",
            "status": "available",
            "path": "configs/wgd_events.brassicaceae.yaml",
            "note": "gamma beta alpha theta named-event YAML mapping",
        },
        {
            "section": "wgd",
            "item": "event_evidence",
            "status": "available",
            "path": "results/wgd_smoke/tables/wgd_event_evidence.tsv",
            "note": "alpha,beta,gamma,theta",
        },
        {
            "section": "wgd",
            "item": "retention_enrichment",
            "status": "available",
            "path": "results/wgd_smoke/tables/retention_enrichment.tsv",
            "note": "family retention enrichment evidence",
        },
        {
            "section": "governance",
            "item": "reference_governance",
            "status": "available",
            "path": "results/reference_governance/reference_governance.md",
            "note": "tracked Reference/ changes are release-blocking",
        },
        {
            "section": "governance",
            "item": "reference_gitignore",
            "status": "available",
            "path": ".gitignore",
            "note": "Reference/ ignored so paper PDFs, source data, and plotting templates are not accidentally staged",
        },
        {
            "section": "governance",
            "item": "reference_governance_tsv",
            "status": "available",
            "path": "results/reference_governance/reference_governance.tsv",
            "note": "machine-readable Reference/ status",
        },
    ]

    for command, item in [
        ("nextflow", "GeneFamilyFlow"),
        ("/usr/local/bin/R", "/usr/local/bin/R"),
        ("docker", "docker"),
        ("apptainer", "apptainer"),
    ]:
        runtime = readiness.get(command, {})
        rows.append(
            {
                "section": "runtime",
                "item": item,
                "status": _runtime_status(runtime.get("status", "")),
                "path": runtime.get("path", ""),
                "note": command,
            }
        )

    rows.extend(
        [
            {
                "section": "runtime_recovery",
                "item": "bootstrap_plan",
                "status": "available",
                "path": "results/readiness/runtime_bootstrap_plan.md",
                "note": "container/runtime recovery plan",
            },
            {
                "section": "runtime_recovery",
                "item": "bootstrap_shell",
                "status": "available",
                "path": "results/readiness/runtime_bootstrap.sh",
                "note": "executable recovery and verification script",
            },
            {
                "section": "runtime_recovery",
                "item": "local_acceptance",
                "status": "available",
                "path": "scripts/run_local_acceptance.sh",
                "note": "refreshes release, handoff, quickstart, and delivery bundle outputs",
            },
            {
                "section": "runtime_recovery",
                "item": "container_default_smoke",
                "status": "available",
                "path": "Dockerfile",
                "note": "docker run default command writes results/container_default_smoke",
            },
            {
                "section": "runtime_recovery",
                "item": "docker_profile_smoke",
                "status": _status_from_check(release_rows, "Docker profile smoke"),
                "path": "results/container_profile_smoke/docker/container_profile_smoke.md",
                "note": "optional container profile diagnostic",
            },
            {
                "section": "runtime_recovery",
                "item": "apptainer_profile_smoke",
                "status": _status_from_check(release_rows, "Apptainer profile smoke"),
                "path": "results/container_profile_smoke/apptainer/container_profile_smoke.md",
                "note": "optional container profile diagnostic",
            },
        ]
    )

    rows.extend(
        [
            {
                "section": "docs",
                "item": "quickstart",
                "status": "available",
                "path": "docs/quickstart.md",
                "note": "shortest verified local run path",
            },
            {
                "section": "docs",
                "item": "release_audit",
                "status": "available",
                "path": "docs/release_audit.md",
                "note": "requirement-to-evidence map",
            },
            {
                "section": "docs",
                "item": "history",
                "status": "available",
                "path": "HISTORY.md",
                "note": "development diary and commit log",
            },
        ]
    )
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_link_target(target: str) -> str:
    return f"<{target}>" if any(character.isspace() for character in target) else target


def _delivery_markdown_path_cell(item: str, path: str) -> str:
    if not path:
        return ""
    return _markdown_link(item, _markdown_link_target(path))


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    blockers = next(
        (row["note"].replace("blocked_or_missing=", "") for row in rows if row["item"] == "objective_audit"),
        "unknown",
    )
    lines = [
        "# GeneFam-Pipeline Delivery Bundle",
        "",
        f"Objective blockers: {blockers}",
        "",
        "This bundle is the final handoff index for species-bank and manifest-mode input, standard gene-family analysis, WGD event evidence, Reference governance, runtime status, runtime recovery, and documentation.",
        "",
        "Named WGD event evidence: alpha, beta, gamma, theta.",
        "",
        "| section | item | status | path | note |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        path_cell = _delivery_markdown_path_cell(row["item"], row["path"])
        lines.append(
            "| {section} | {item} | {status} | {path} | {note} |".format(
                section=row["section"],
                item=row["item"],
                status=row["status"],
                path=path_cell,
                note=row["note"],
            )
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure_gallery_tsv(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIGURE_GALLERY_FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(_figure_gallery_rows_with_traceability())


def _figure_gallery_rows_with_traceability() -> list[dict[str, str]]:
    rows = []
    for row in FIGURE_GALLERY_ROWS:
        enriched = dict(row)
        enriched["plot_png_path"] = str(Path(row["plot_path"]).with_suffix(".png"))
        enriched["figure_interpretations"] = f"{row['figure_interpretations']}#{row['plot_key']}"
        enriched["traceability_matrix"] = f"{row['final_report']}#figure-traceability-matrix"
        rows.append(enriched)
    return rows


def _markdown_link(label: str, target: str) -> str:
    return f"[{label}]({target})"


def write_figure_gallery_markdown(out_path: Path) -> None:
    lines = [
        "# GeneFam-Pipeline Figure Gallery",
        "",
        "This gallery is the global plot index for the paper-level standard and WGD result packages.",
        "",
        "| branch | plot_key | plot_path | plot_png_path | description | close-reading report | software versions | final report | traceability_matrix |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in _figure_gallery_rows_with_traceability():
        lines.append(
            "| {branch} | {plot_key} | {plot_path} | {plot_png_path} | {plot_description} | {figure_interpretations} | {software_versions} | {final_report} | {traceability_matrix} |".format(
                branch=row["branch"],
                plot_key=row["plot_key"],
                plot_path=_markdown_link("PDF", row["plot_path"]),
                plot_png_path=_markdown_link("PNG", row["plot_png_path"]),
                plot_description=row["plot_description"],
                figure_interpretations=_markdown_link("close reading", row["figure_interpretations"]),
                software_versions=_markdown_link("versions", row["software_versions"]),
                final_report=_markdown_link("final report", row["final_report"]),
                traceability_matrix=_markdown_link("traceability", row["traceability_matrix"]),
            )
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_delivery_bundle(
    release_checks: Path,
    objective_audit: Path,
    readiness: Path,
    quickstart: Path,
    outdir: Path,
) -> dict[str, Path]:
    release_rows = read_tsv(release_checks)
    rows = build_delivery_manifest(
        release_rows=release_rows,
        objective_rows=read_tsv(objective_audit),
        readiness_rows=read_tsv(readiness),
        quickstart_rows=read_tsv(quickstart),
    )
    manifest = outdir / "delivery_manifest.tsv"
    summary = outdir / "delivery_bundle.md"
    figure_gallery = outdir / "figure_gallery.tsv"
    figure_gallery_md = outdir / "figure_gallery.md"
    rows.insert(
        5,
        {
            "section": "status",
            "item": "figure_gallery",
            "status": "available",
            "path": str(figure_gallery),
            "note": "global figure gallery linking paper-level plots to their close-reading reports and software versions",
        },
    )
    rows.insert(
        6,
        {
            "section": "status",
            "item": "delivery_bundle_figure_gallery_smoke",
            "status": _status_from_check(release_rows, "delivery bundle figure gallery smoke"),
            "path": "results/delivery_bundle_smoke/delivery_bundle_smoke.md",
            "note": "delivery bundle smoke writes manifest, Markdown summary, figure gallery TSV, and figure gallery Markdown",
        },
    )
    write_figure_gallery_tsv(figure_gallery)
    write_figure_gallery_markdown(figure_gallery_md)
    write_tsv(rows, manifest)
    write_markdown(rows, summary)
    return {
        "delivery_manifest": manifest,
        "delivery_bundle": summary,
        "figure_gallery": figure_gallery,
        "figure_gallery_md": figure_gallery_md,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-checks", default=Path("results/release_checks/release_checks.tsv"), type=Path)
    parser.add_argument("--objective-audit", default=Path("results/objective_audit/objective_audit.tsv"), type=Path)
    parser.add_argument("--readiness", default=Path("results/readiness/command_readiness.tsv"), type=Path)
    parser.add_argument("--quickstart", default=Path("results/quickstart/quickstart_summary.tsv"), type=Path)
    parser.add_argument("--outdir", default=Path("results/delivery_bundle"), type=Path)
    args = parser.parse_args()
    outputs = run_delivery_bundle(
        release_checks=args.release_checks,
        objective_audit=args.objective_audit,
        readiness=args.readiness,
        quickstart=args.quickstart,
        outdir=args.outdir,
    )
    print("output\tpath")
    for key, path in sorted(outputs.items()):
        print(f"{key}\t{path}")


if __name__ == "__main__":
    main()
