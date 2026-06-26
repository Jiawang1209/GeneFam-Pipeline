#!/usr/bin/env python3
"""Summarize the long-form GeneFam-Pipeline objective against release evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["requirement", "status", "evidence", "note"]
AVAILABLE_STATUSES = {"available", "available_in_conda"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _release_statuses(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["check"]: row["status"] for row in rows}


def _readiness_statuses(rows: list[dict[str, str]]) -> dict[str, str]:
    return {row["command"]: row["status"] for row in rows}


def _all_passed(statuses: dict[str, str], checks: list[str]) -> bool:
    return all(statuses.get(check) == "passed" for check in checks)


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
) -> list[dict[str, str]]:
    release = _release_statuses(release_rows)
    readiness = _readiness_statuses(readiness_rows)
    core_tools = ["nextflow", "/usr/local/bin/R", "hmmsearch", "diamond", "mafft", "iqtree2", "meme"]
    missing_core_tools = _missing_commands(readiness, core_tools)
    missing_container_tools = _missing_commands(readiness, ["docker", "apptainer"])

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
                ],
            ),
            "YAML-driven species selection",
            "validate example config, validate advanced config, validate manifest config, species selection smoke, and species manifest selection smoke",
            "Species bank discovery, prebuilt manifest input, selected target species, run-plan metadata, and advanced module settings are validated from YAML.",
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
            "achieved" if _available(readiness, "/usr/local/bin/R") else "blocked",
            "command readiness audit",
            "R plotting path is available at /usr/local/bin/R."
            if _available(readiness, "/usr/local/bin/R")
            else "Missing /usr/local/bin/R.",
        ),
        _row(
            "Docker/Apptainer reproducibility",
            "achieved" if not missing_container_tools else "blocked",
            "container materials audit, Dockerfile default standard smoke contract, command readiness audit, and runtime bootstrap plan",
            "Container runtime route is available."
            if not missing_container_tools
            else "Dockerfile default standard smoke writes results/container_default_smoke; missing container commands: "
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
                ],
            ),
            "standard identification branch",
            "domain filter smoke, motif parser smoke, gene structure smoke, Python standard branch, and Nextflow standard branch smoke checks",
            "Domain-filtered evidence, motif summaries, gene-structure summaries, species-bank candidates, chromosome locations, expression handoff, and final report are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "synteny parser smoke",
                    "WGD event smoke",
                    "Nextflow WGD event smoke",
                    "prepared WGD handoff example",
                ],
            ),
            "WGD gamma beta alpha theta evidence",
            "synteny parser smoke, WGD event smoke, and prepared WGD handoff checks",
            "MCScanX collinearity parsing feeds named events interpreted from configured Ks-supported WGD layers.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "Ka/Ks parser smoke",
                    "duplicate-type Ka/Ks visualization smoke",
                    "retention enrichment smoke",
                    "WGD event smoke",
                    "prepared WGD handoff example",
                ],
            ),
            "Ka/Ks and retention analysis",
            "Ka/Ks parser smoke, duplicate-type Ka/Ks visualization smoke, retention enrichment smoke, and WGD/retention smoke outputs",
            "Ka/Ks selection categories, duplicate-type grouped Ka/Ks panels, retention class, family-event membership, retention enrichment, and retention summaries are generated from prepared evidence.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "gene family information visualization smoke",
                    "feature summary visualization smoke",
                    "promoter cis-element visualization smoke",
                    "tree feature visualization smoke",
                    "MCScanX circlize visualization smoke",
                    "PPI ggNetView plot smoke",
                    "standard branch expression smoke",
                    "expression heatmap visualization smoke",
                ],
            ),
            "paper-level visualization modules",
            "gene family information visualization smoke, feature summary visualization smoke, promoter cis-element visualization smoke, tree feature visualization smoke, MCScanX circlize visualization smoke, PPI ggNetView plot smoke, standard branch expression smoke, and expression heatmap visualization smoke",
            "Report-ready gene-family information, feature summary, promoter cis-element, tree/motif/gene-structure/domain, synteny/circlize, PPI, and annotated expression heatmap figures are exercised by smoke checks.",
        ),
        _achieved_if(
            _all_passed(release, ["gene family information visualization smoke"]),
            "gene family information and copy-number visualization",
            "gene family information visualization smoke",
            "Gene-family information, copy-number balance, pangenome class, expansion/contraction, and protein-property summary plots are exercised.",
        ),
        _achieved_if(
            _all_passed(release, ["tree feature visualization smoke", "feature summary visualization smoke"]),
            "tree motif gene-structure domain visualization",
            "tree feature visualization smoke and feature summary visualization smoke",
            "tree/motif/gene-structure/domain composite figures and large-family feature summary plots are exercised.",
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
            _all_passed(release, ["promoter cis-element visualization smoke"]),
            "promoter cis-element visualization",
            "promoter cis-element visualization smoke",
            "promoter cis-element category matrices, per-element summaries, and report-ready promoter regulatory plots are exercised.",
        ),
        _achieved_if(
            _all_passed(release, ["standard branch expression smoke", "expression heatmap visualization smoke"]),
            "expression heatmap visualization",
            "standard branch expression smoke and expression heatmap visualization smoke",
            "RNA-seq expression subsetting, sample metadata integration, group summaries, gene-level QC, and expression heatmap plotting are exercised.",
        ),
        _achieved_if(
            _all_passed(release, ["PPI ggNetView plot smoke"]),
            "PPI ggNetView visualization",
            "PPI ggNetView plot smoke",
            "PPI edge/node normalization, hub summaries, network QC, ggNetView status, and ggNetView-rendered network plots are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                [
                    "Ka/Ks WGD annotation plot smoke",
                    "duplicate-type Ka/Ks visualization smoke",
                    "pangenome-class Ka/Ks visualization smoke",
                ],
            ),
            "Ka/Ks WGD visualization",
            "Ka/Ks WGD annotation plot smoke, duplicate-type Ka/Ks visualization smoke, and pangenome-class Ka/Ks visualization smoke",
            "Ks distribution, gamma beta alpha theta WGD-layer annotations, duplicate-type Ka/Ks panels, and pangenome-class Ka/Ks panels are exercised.",
        ),
        _achieved_if(
            _all_passed(
                release,
                ["chromosome location smoke", "standard branch smoke", "standard branch expression smoke", "quickstart handoff"],
            ),
            "chromosome and expression integration",
            "chromosome location smoke, standard branch, expression smoke, and quickstart outputs",
            "Chromosome locations and an RNA-seq expression matrix subset are represented in standard reports.",
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
                    "prepared WGD handoff example",
                    "quickstart handoff",
                    "publication report audit",
                    "WGD publication report audit",
                ],
            ),
            "final reports",
            "standard, prepared WGD, quickstart report outputs, standard publication report audit, and WGD publication report audit",
            "Final Markdown reports are produced for standard and WGD handoff paths, while publication audits verify valid plot file signatures, registered-only figure interpretation scope, plot manifest and interpretation output path consistency, and complete per-figure close-reading text: input data, what the figure shows, key observations, biological interpretation, QC warnings, QC tables, method/software entries, software/R package versions, reproducibility commands, reading status, output paths, and registered plot files for both report families.",
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
    parser.add_argument("--outdir", default=Path("results/objective_audit"), type=Path)
    args = parser.parse_args()

    rows = build_objective_audit(read_tsv(args.release_checks), read_tsv(args.readiness))
    write_tsv(rows, args.outdir / "objective_audit.tsv")
    write_markdown(rows, args.outdir / "objective_audit.md")


if __name__ == "__main__":
    main()
