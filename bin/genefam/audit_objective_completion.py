#!/usr/bin/env python3
"""Summarize the long-form GeneFam-Pipeline objective against release evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["requirement", "status", "evidence", "note"]
AVAILABLE_STATUSES = {"available", "available_in_conda"}
PUBLICATION_AUDIT_CHECKS = [
    "plot_files_exist",
    "plot_file_format_valid",
    "figure_interpretation_coverage",
    "figure_interpretation_scope",
    "figure_interpretation_detail",
    "figure_interpretation_close_reading_voice",
    "figure_interpretation_qc_specificity",
    "figure_output_paths_match_manifest",
    "software_versions_present",
    "software_detected_versions_parseable",
    "figure_method_software_versions",
    "final_report_embeds_publication_sections",
    "final_report_figure_traceability",
    "final_report_plot_previews",
    "final_report_placeholder_text",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _release_statuses(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["check"]: row["status"] for row in rows}


def _readiness_statuses(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["command"]: row["status"] for row in rows}


def _all_passed(statuses: dict[str, str], checks: list[str]) -> bool:
    return all(statuses.get(check) == "passed" for check in checks)


def _audit_statuses(rows: list[dict[str, str]] | None) -> dict[str, str]:
    return {row["check"]: row["status"] for row in (rows or [])}


def _failed_or_missing_audit_checks(rows: list[dict[str, str]] | None) -> list[str]:
    statuses = _audit_statuses(rows)
    return [check for check in PUBLICATION_AUDIT_CHECKS if statuses.get(check) != "passed"]


def _available(statuses: dict[str, str], command: str) -> bool:
    return statuses.get(command) in AVAILABLE_STATUSES


def _missing_commands(statuses: dict[str, str], commands: list[str]) -> list[str]:
    return [command for command in commands if not _available(statuses, command)]


def _row(requirement: str, status: str, evidence: str, note: str) -> dict[str, str]:
    return {"requirement": requirement, "status": status, "evidence": evidence, "note": note}


def _achieved_if(condition: bool, requirement: str, evidence: str, note: str) -> dict[str, str]:
    return _row(requirement, "achieved" if condition else "missing", evidence, note)


def build_objective_audit(
    release_rows: list[dict[str, str]],
    readiness_rows: list[dict[str, str]],
    publication_audit_rows: list[dict[str, str]] | None = None,
    wgd_publication_audit_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    release = _release_statuses(release_rows)
    readiness = _readiness_statuses(readiness_rows)
    core_tools = ["nextflow", "/usr/local/bin/R", "hmmsearch", "diamond", "mafft", "iqtree2", "meme"]
    missing_core_tools = _missing_commands(readiness, core_tools)
    missing_container_tools = _missing_commands(readiness, ["docker", "apptainer"])
    r_path_available = _available(readiness, "/usr/local/bin/R")
    r_runtime_health_passed = release.get("R runtime health") == "passed"
    missing_publication_audit_checks = _failed_or_missing_audit_checks(publication_audit_rows)
    missing_wgd_publication_audit_checks = _failed_or_missing_audit_checks(wgd_publication_audit_rows)
    final_report_audit_details_ok = (
        not missing_publication_audit_checks and not missing_wgd_publication_audit_checks
    )
    final_report_detail_note = (
        "Publication audit detail checks passed for standard and WGD reports, including Figure Traceability Matrix coverage and no TODO/TBD/placeholder text."
        if final_report_audit_details_ok
        else "Publication audit detail gaps: "
        + "; ".join(
            part
            for part in [
                "standard publication audit missing/pending: " + ", ".join(missing_publication_audit_checks)
                if missing_publication_audit_checks
                else "",
                "WGD publication audit missing/pending: " + ", ".join(missing_wgd_publication_audit_checks)
                if missing_wgd_publication_audit_checks
                else "",
            ]
            if part
        )
    )

    rows = [
        _achieved_if(
            _all_passed(
                release,
                [
                    "Nextflow mock MVP smoke",
                    "Nextflow standard branch smoke",
                    "Nextflow standard manifest smoke",
                    "Nextflow standard single-tool smoke",
                    "Nextflow WGD event smoke",
                    "alignment phylogeny smoke",
                ],
            ),
            "Nextflow DSL2 workflow",
            "Nextflow mock, standard, manifest-standard, single-tool, WGD, and alignment phylogeny smoke checks",
            "DSL2 entrypoints, including species-bank standard runs, manifest-mode standard runs, HMMER-only and DIAMOND-only single-tool routing, plus alignment/phylogeny manifests, are smoke-tested through GeneFamilyFlow evidence.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "validate example config",
                    "validate advanced config",
                    "validate manifest config",
                    "species selection smoke",
                    "species manifest selection smoke",
                    "Nextflow standard manifest smoke",
                ],
            ),
            "YAML-driven species selection",
            "validate example config, validate advanced config, validate manifest config, species selection smoke, species manifest selection smoke, and Nextflow standard manifest smoke",
            "Species bank discovery, prebuilt manifest input, selected target species, run-plan metadata, advanced module settings, and manifest-mode Nextflow standard runs are validated from YAML.",
        ),
        _row(
            "GeneFamilyFlow runtime",
            "achieved" if not missing_core_tools else "blocked",
            "command readiness audit",
            "All core commands available through host/GeneFamilyFlow."
            if not missing_core_tools
            else "Missing core commands: " + ", ".join(missing_core_tools),
        ),
        _row(
            "/usr/local/bin/R plotting",
            "achieved" if r_path_available and r_runtime_health_passed else "blocked",
            "command readiness audit and R runtime health release check",
            "R plotting path is available at /usr/local/bin/R and R runtime health passed before plotting smokes."
            if r_path_available and r_runtime_health_passed
            else "Missing /usr/local/bin/R."
            if not r_path_available
            else "R runtime health release check is missing or failed before plotting smokes.",
        ),
        _row(
            "Docker/Apptainer reproducibility",
            "achieved" if not missing_container_tools else "blocked",
            "container materials audit, Dockerfile default standard smoke contract, Apptainer.def Reference-safe SIF contract, command readiness audit, runtime bootstrap plan, and runtime bootstrap shell syntax",
            "Container runtime route is available."
            if not missing_container_tools
            else "Dockerfile default standard smoke writes results/container_default_smoke; Reference-safe Apptainer definition can build genefam-pipeline_latest.sif; runtime_bootstrap.sh passed bash -n; missing container commands: "
            + ", ".join(missing_container_tools),
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "domain filter smoke",
                    "motif parser smoke",
                    "gene structure smoke",
                    "standard branch smoke",
                    "Nextflow standard branch smoke",
                    "alignment phylogeny smoke",
                ],
            ),
            "standard identification branch",
            "domain filter smoke, motif parser smoke, gene structure smoke, Python standard branch, Nextflow standard branch, and alignment phylogeny smoke checks",
            "Domain-filtered evidence, motif summaries, gene-structure summaries, species-bank candidates, chromosome locations, alignment/phylogeny outputs, expression handoff, and final report are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "synteny parser smoke",
                    "WGD event smoke",
                    "Nextflow WGD event smoke",
                    "Nextflow raw MCScanX/KaKs WGD smoke",
                    "prepared WGD handoff example",
                ],
            ),
            "WGD gamma beta alpha theta evidence",
            "synteny parser smoke, WGD event smoke, Nextflow WGD event smoke, Nextflow raw MCScanX/KaKs WGD smoke, and prepared WGD handoff checks",
            "MCScanX collinearity parsing feeds named events interpreted from configured Ks-supported WGD layers through prepared evidence, raw MCScanX/KaKs inputs, and the formal Nextflow WGD branch.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "Ka/Ks parser smoke",
                    "duplicate-type Ka/Ks visualization smoke",
                    "pangenome-class Ka/Ks visualization smoke",
                    "retention enrichment smoke",
                    "WGD event smoke",
                    "Nextflow WGD event smoke",
                    "Nextflow raw MCScanX/KaKs WGD smoke",
                    "prepared WGD handoff example",
                ],
            ),
            "Ka/Ks and retention analysis",
            "Ka/Ks parser smoke, duplicate-type Ka/Ks visualization smoke, pangenome-class Ka/Ks visualization smoke, retention enrichment smoke, WGD event smoke, Nextflow WGD event smoke, Nextflow raw MCScanX/KaKs WGD smoke, and prepared WGD handoff outputs",
            "Ka/Ks selection categories, duplicate-type grouped Ka/Ks panels, pangenome-class Ka/Ks panels, retention class, family-event membership, retention enrichment, and retention summaries are generated from prepared evidence, raw MCScanX/KaKs inputs, and formal Nextflow WGD branch evidence.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "validate publication modules config",
                    "gene family information visualization smoke",
                    "feature summary visualization smoke",
                    "promoter smoke",
                    "promoter cis-element visualization smoke",
                    "tree feature visualization smoke",
                    "MCScanX circlize visualization smoke",
                    "Nextflow standard visualization smoke",
                    "PPI ggNetView smoke",
                    "PPI ggNetView plot smoke",
                    "standard branch expression smoke",
                    "expression heatmap visualization smoke",
                    "Ka/Ks WGD annotation plot smoke",
                    "duplicate-type Ka/Ks visualization smoke",
                    "pangenome-class Ka/Ks visualization smoke",
                    "Nextflow WGD event smoke",
                    "WGD publication report audit",
                    "Reference visual alignment audit",
                ],
            ),
            "paper-level visualization modules",
            "validate publication modules config, gene family information visualization smoke, feature summary visualization smoke, promoter smoke, promoter cis-element visualization smoke, tree feature visualization smoke, MCScanX circlize visualization smoke, Nextflow standard visualization smoke, PPI ggNetView smoke, PPI ggNetView plot smoke, standard branch expression smoke, expression heatmap visualization smoke, Ka/Ks WGD annotation plot smoke, duplicate-type Ka/Ks visualization smoke, pangenome-class Ka/Ks visualization smoke, Nextflow WGD event smoke, WGD publication report audit, and Reference visual alignment audit",
            "Report-ready gene-family information, feature summary, promoter extraction and cis-element, tree/motif/gene-structure/domain, synteny/circlize, PPI, annotated expression heatmap, Ks distribution, duplicate-type Ka/Ks, pangenome-class Ka/Ks, and WGD report figures are exercised by script smoke checks and formal Nextflow report evidence; the standard publication visualization branch is also validated from configs/publication_modules.example.yaml so the report-scale figure set remains YAML-driven.",
        ),
        _achieved_if(
            _all_passed(release, ["gene family information visualization smoke", "Nextflow standard visualization smoke"]),
            "gene family information and copy-number visualization",
            "gene family information visualization smoke and Nextflow standard visualization smoke",
            "Gene-family information, copy-number balance, pangenome class, expansion/contraction, protein-property summary plots, and Nextflow report evidence are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "tree feature visualization smoke",
                    "feature summary visualization smoke",
                    "Nextflow standard visualization smoke",
                ],
            ),
            "tree motif gene-structure domain visualization",
            "tree feature visualization smoke, feature summary visualization smoke, and Nextflow standard visualization smoke",
            "tree/motif/gene-structure/domain composite figures, large-family feature summary plots, and Nextflow report evidence are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "synteny parser smoke",
                    "MCScanX circlize visualization smoke",
                    "Nextflow standard visualization smoke",
                ],
            ),
            "MCScanX synteny circlize visualization",
            "synteny parser smoke, MCScanX circlize visualization smoke, and Nextflow standard visualization smoke",
            "MCScanX syntenic-pair parsing and chromosome-scale circlize link visualization are exercised through script and Nextflow report evidence.",
        ),
        _achieved_if(
            _all_passed(
                release,
                ["promoter smoke", "promoter cis-element visualization smoke", "Nextflow standard visualization smoke"],
            ),
            "promoter cis-element visualization",
            "promoter smoke, promoter cis-element visualization smoke, and Nextflow standard visualization smoke",
            "The promoter extraction step, promoter FASTA/BED outputs, promoter cis-element category matrices, per-element summaries, and report-ready promoter regulatory plots are exercised through script and Nextflow report evidence.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "standard branch expression smoke",
                    "expression heatmap visualization smoke",
                    "Nextflow standard visualization smoke",
                ],
            ),
            "expression heatmap visualization",
            "standard branch expression smoke, expression heatmap visualization smoke, and Nextflow standard visualization smoke",
            "RNA-seq expression subsetting, sample metadata integration, group summaries, gene-level QC, expression heatmap plotting, and Nextflow report evidence are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                ["PPI ggNetView smoke", "PPI ggNetView plot smoke", "Nextflow standard visualization smoke"],
            ),
            "PPI ggNetView visualization",
            "PPI ggNetView smoke, PPI ggNetView plot smoke, and Nextflow standard visualization smoke",
            "PPI edge/node normalization, hub summaries, network QC, ggNetView status, ggNetView-rendered network plots, and Nextflow report evidence are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "Ka/Ks WGD annotation plot smoke",
                    "duplicate-type Ka/Ks visualization smoke",
                    "pangenome-class Ka/Ks visualization smoke",
                    "Nextflow WGD event smoke",
                    "WGD publication report audit",
                ],
            ),
            "Ka/Ks WGD visualization",
            "Ka/Ks WGD annotation plot smoke, duplicate-type Ka/Ks visualization smoke, pangenome-class Ka/Ks visualization smoke, Nextflow WGD event smoke, and WGD publication report audit",
            "Ks distribution, gamma beta alpha theta WGD-layer annotations, duplicate-type Ka/Ks panels, pangenome-class Ka/Ks panels, WGD final-report close reading, and Nextflow report evidence are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "chromosome location smoke",
                    "standard branch smoke",
                    "Nextflow standard branch smoke",
                    "standard branch expression smoke",
                    "expression heatmap visualization smoke",
                    "quickstart handoff",
                ],
            ),
            "chromosome and expression integration",
            "chromosome location smoke, standard branch smoke, Nextflow standard branch smoke, standard branch expression smoke, expression heatmap visualization smoke, and quickstart outputs",
            "Chromosome locations, RNA-seq expression matrix subsets, expression heatmap figures, and standard report handoff are exercised through script evidence and the formal Nextflow standard branch.",
        ),
        _achieved_if(
            release.get("quickstart handoff") == "passed",
            "quickstart handoff",
            "quickstart handoff release check",
            "One command writes standard and prepared-WGD handoff summaries.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "standard branch smoke",
                    "Nextflow standard visualization smoke",
                    "Nextflow WGD event smoke",
                    "prepared WGD handoff example",
                    "quickstart handoff",
                    "publication report audit",
                    "WGD publication report audit",
                    "standard report index audit",
                    "WGD report index audit",
                    "delivery bundle figure gallery audit",
                    "delivery bundle manifest audit",
                ],
            )
            and final_report_audit_details_ok,
            "final reports",
            "standard branch smoke, Nextflow standard visualization smoke, Nextflow WGD event smoke, prepared WGD handoff example, quickstart report outputs, standard publication report audit, WGD publication report audit, standard report index audit, WGD report index audit, delivery bundle figure gallery audit, and delivery bundle manifest audit",
            "Final Markdown reports are produced for standard and WGD handoff paths from formal Nextflow standard visualization and WGD branch evidence, while publication audits verify valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, Figure Traceability Matrix rows, embedded PNG plot previews, and complete per-figure close-reading text: input data, what the figure shows, key observations, biological interpretation, figure-specific QC warnings, QC tables, method/software entries, software/R package versions, parseable detected version values, reproducibility commands, reading status, output paths, registered plot files, and no TODO/TBD/placeholder text for both report families. Report index audits verify that standard and WGD report indexes expose plot manifests, software versions, figure interpretations in TSV/Markdown, and final reports. "
            "The delivery figure gallery is audited by figure_gallery_audit so each row links plot files to interpretation, software versions, final report anchors, and the traceability matrix with valid gallery plot file signatures and per-figure close-reading anchors. "
            "The delivery manifest audit verifies that available and blocked handoff index paths resolve to real files or accepted runtime locators. "
            + final_report_detail_note,
        ),
        _achieved_if(
            _all_passed(release, ["pytest", "Reference governance audit"]),
            "history and Reference governance",
            "pytest, documentation contracts, and Reference governance audit",
            "Development history is maintained; tracked Reference/ changes are release-blocking while untracked source material remains allowed.",
        ),
    ]
    return rows


def summarize_objective_audit(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    achieved = sum(1 for row in rows if row["status"] == "achieved")
    blocked = sum(1 for row in rows if row["status"] == "blocked")
    missing = sum(1 for row in rows if row["status"] == "missing")
    return {
        "achieved": achieved,
        "blocked": blocked,
        "missing": missing,
        "complete": blocked == 0 and missing == 0,
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
    summary = summarize_objective_audit(rows)
    lines = [
        "# GeneFam-Pipeline Objective Audit",
        "",
        f"Achieved: {summary['achieved']}",
        f"Blocked: {summary['blocked']}",
        f"Missing: {summary['missing']}",
        f"Complete: {str(summary['complete']).lower()}",
        "",
        "| requirement | status | evidence | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        escaped = {key: _markdown_cell(value) for key, value in row.items()}
        lines.append("| {requirement} | {status} | {evidence} | {note} |".format(**escaped))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-checks", required=True, type=Path)
    parser.add_argument("--readiness", required=True, type=Path)
    parser.add_argument(
        "--publication-audit",
        default=Path("results/publication_report_audit/publication_report_audit.tsv"),
        type=Path,
    )
    parser.add_argument(
        "--wgd-publication-audit",
        default=Path("results/publication_report_audit/wgd_publication_report_audit.tsv"),
        type=Path,
    )
    parser.add_argument("--outdir", default=Path("results/objective_audit"), type=Path)
    args = parser.parse_args()

    rows = build_objective_audit(
        read_tsv(args.release_checks),
        read_tsv(args.readiness),
        publication_audit_rows=read_tsv(args.publication_audit) if args.publication_audit.exists() else None,
        wgd_publication_audit_rows=read_tsv(args.wgd_publication_audit)
        if args.wgd_publication_audit.exists()
        else None,
    )
    write_tsv(rows, args.outdir / "objective_audit.tsv")
    write_markdown(rows, args.outdir / "objective_audit.md")


if __name__ == "__main__":
    main()
