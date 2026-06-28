#!/usr/bin/env python3
"""Audit a real Reference-level GeneFam analysis module package."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["check", "status", "evidence", "note"]
REQUIRED_MODULES = [
    "00_preprocess",
    "01_gene_identification",
    "02_domain_filtering",
    "03_alignment",
    "04_phylogeny",
    "05_motif_analysis",
    "06_gene_structure",
    "07_chromosome_location",
    "08_promoter",
    "09_promoter_cis",
    "10_synteny_jcvi",
    "11_mcscanx",
    "12_ppi",
    "13_expression",
    "14_duplication_retention_kaks",
    "15_gene_family_summary",
    "report",
]
AVAILABLE_REQUIRED_MODULES = [
    "00_preprocess",
    "01_gene_identification",
    "02_domain_filtering",
    "03_alignment",
    "04_phylogeny",
    "05_motif_analysis",
    "06_gene_structure",
    "07_chromosome_location",
    "08_promoter",
    "10_synteny_jcvi",
    "11_mcscanx",
    "12_ppi",
    "15_gene_family_summary",
    "report",
]
REPORT_REQUIRED_FILES = [
    "report_index.tsv",
    "plot_manifest.tsv",
    "figure_interpretations.tsv",
    "software_versions.tsv",
    "final_report.md",
    "reproducibility_code.md",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _row(check: str, passed: bool, evidence: str, note: str) -> dict[str, str]:
    return {
        "check": check,
        "status": "passed" if passed else "failed",
        "evidence": evidence,
        "note": note,
    }


def _module_statuses(manifest: Path) -> dict[str, str]:
    return {
        row.get("module", "").strip(): row.get("status", "").strip()
        for row in read_tsv(manifest)
        if row.get("module", "").strip()
    }


def _first_status(path: Path) -> str:
    rows = read_tsv(path)
    if not rows:
        return ""
    return rows[0].get("status", "").strip()


def _has_nonempty_tsv(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0 and len(read_tsv(path)) > 0


def _existing_file_issues(paths: list[Path], base: Path) -> list[str]:
    issues: list[str] = []
    for path in paths:
        if not path.exists():
            issues.append(f"{path.relative_to(base)}:missing")
        elif path.is_file() and path.stat().st_size <= 0:
            issues.append(f"{path.relative_to(base)}:empty")
    return issues


def _mcscanx_self_issues(analysis_modules: Path) -> list[str]:
    module = analysis_modules / "11_mcscanx"
    issues: list[str] = []
    execution = module / "mcscanx_execution_status.tsv"
    execution_rows = read_tsv(execution)
    if not execution_rows:
        issues.append("11_mcscanx/mcscanx_execution_status.tsv:missing")
    else:
        row = execution_rows[0]
        if row.get("status", "").strip() != "executed":
            issues.append(f"mcscanx_execution_status={row.get('status', '').strip() or 'missing'}")
        if row.get("execute", "").strip().lower() != "true":
            issues.append(f"mcscanx_execute={row.get('execute', '').strip() or 'missing'}")
        if row.get("exit_code", "").strip() not in {"", "0"}:
            issues.append(f"mcscanx_exit_code={row.get('exit_code', '').strip()}")

    circlize_status = module / "mcscanx_circlize_status.tsv"
    if _first_status(circlize_status) != "available":
        issues.append("11_mcscanx/mcscanx_circlize_status.tsv:not_available_or_missing")
    for relative in [
        "mcscanx_gene_pairs.tsv",
        "tables/circlize_links.tsv",
        "plots/mcscanx_circlize.pdf",
        "plots/mcscanx_circlize.png",
    ]:
        path = module / relative
        if not path.exists():
            issues.append(f"11_mcscanx/{relative}:missing")
        elif path.stat().st_size <= 0:
            issues.append(f"11_mcscanx/{relative}:empty")
    if (module / "mcscanx_gene_pairs.tsv").exists() and not _has_nonempty_tsv(module / "mcscanx_gene_pairs.tsv"):
        issues.append("11_mcscanx/mcscanx_gene_pairs.tsv:no_pairs")
    return issues


def _jcvi_issues(analysis_modules: Path) -> list[str]:
    module = analysis_modules / "10_synteny_jcvi"
    issues: list[str] = []
    run_status = module / "jcvi_run_status.tsv"
    rows = read_tsv(run_status)
    if not rows:
        issues.append("10_synteny_jcvi/jcvi_run_status.tsv:missing")
    else:
        row = rows[0]
        if row.get("status", "").strip() != "available":
            issues.append(f"jcvi_run_status={row.get('status', '').strip() or 'missing'}")
        if row.get("failed_count", "").strip() not in {"", "0"}:
            issues.append(f"jcvi_failed_count={row.get('failed_count', '').strip()}")
    if not _has_nonempty_tsv(module / "jcvi_pair_manifest.tsv"):
        issues.append("10_synteny_jcvi/jcvi_pair_manifest.tsv:missing_or_empty")
    return issues


def _plantcare_handoff_issues(analysis_modules: Path, statuses: dict[str, str]) -> list[str]:
    status = statuses.get("09_promoter_cis", "")
    if status == "available":
        return []
    if status != "missing_input":
        return [f"09_promoter_cis:status={status or 'missing'}"]
    handoff = analysis_modules / "08_promoter" / "plantcare_submission"
    issues = _existing_file_issues(
        [
            handoff / "plantcare_submission_manifest.tsv",
            handoff / "plantcare_submission_status.tsv",
        ],
        analysis_modules,
    )
    if _first_status(handoff / "plantcare_submission_status.tsv") != "available":
        issues.append("08_promoter/plantcare_submission/plantcare_submission_status.tsv:not_available")
    return issues


def _expression_issues(analysis_modules: Path, statuses: dict[str, str]) -> list[str]:
    status = statuses.get("13_expression", "")
    if status == "available":
        return []
    if status != "skipped_optional":
        return [f"13_expression:status={status or 'missing'}"]
    expression_status = analysis_modules / "13_expression" / "expression_status.tsv"
    if _first_status(expression_status) != "skipped_optional":
        return ["13_expression/expression_status.tsv:not_skipped_optional_or_missing"]
    return []


def _kaks_issues(analysis_modules: Path, statuses: dict[str, str]) -> list[str]:
    status = statuses.get("14_duplication_retention_kaks", "")
    if status not in {"available", "partial"}:
        return [f"14_duplication_retention_kaks:status={status or 'missing'}"]
    module = analysis_modules / "14_duplication_retention_kaks"
    issues: list[str] = []
    if status == "partial" and not _has_nonempty_tsv(module / "kaks_failure_summary.tsv"):
        issues.append("14_duplication_retention_kaks/kaks_failure_summary.tsv:missing_or_empty")
    rows = read_tsv(module / "kaks_calculator_status.tsv")
    if not rows:
        issues.append("14_duplication_retention_kaks/kaks_calculator_status.tsv:missing")
    elif rows[0].get("status", "").strip() not in {"available", "partial"}:
        issues.append(f"kaks_calculator_status={rows[0].get('status', '').strip() or 'missing'}")
    return issues


def _report_file_issues(analysis_modules: Path) -> list[str]:
    report = analysis_modules / "report"
    return _existing_file_issues([report / filename for filename in REPORT_REQUIRED_FILES], analysis_modules)


def _reproducibility_issues(analysis_modules: Path) -> list[str]:
    repro = analysis_modules / "report" / "reproducibility_code.md"
    if not repro.exists():
        return ["report/reproducibility_code.md:missing"]
    text = repro.read_text(encoding="utf-8")
    required_terms = [
        "MCScanX self intra-species",
        "JCVI inter-species",
        "PlantCARE handoff",
        "kaks_failure_summary.tsv",
    ]
    return [f"missing_term:{term}" for term in required_terms if term not in text]


def audit_real_reference_package(analysis_modules: Path) -> list[dict[str, str]]:
    manifest = analysis_modules / "module_manifest.tsv"
    statuses = _module_statuses(manifest)
    missing_folders = [module for module in REQUIRED_MODULES if not (analysis_modules / module).is_dir()]
    unavailable_required = [
        f"{module}:{statuses.get(module, 'missing')}"
        for module in AVAILABLE_REQUIRED_MODULES
        if statuses.get(module) != "available"
    ]
    plantcare_issues = _plantcare_handoff_issues(analysis_modules, statuses)
    expression_issues = _expression_issues(analysis_modules, statuses)
    kaks_issues = _kaks_issues(analysis_modules, statuses)
    jcvi_issues = _jcvi_issues(analysis_modules)
    mcscanx_issues = _mcscanx_self_issues(analysis_modules)
    report_issues = _report_file_issues(analysis_modules)
    reproducibility_issues = _reproducibility_issues(analysis_modules)

    rows = [
        _row(
            "module_manifest_present",
            manifest.exists() and manifest.stat().st_size > 0,
            str(manifest),
            "module_manifest.tsv exists and is non-empty",
        ),
        _row(
            "required_module_folders",
            not missing_folders,
            str(analysis_modules),
            "all required per-module folders exist" if not missing_folders else "missing folders: " + ", ".join(missing_folders),
        ),
        _row(
            "required_module_statuses",
            not unavailable_required,
            str(manifest),
            "core modules are available" if not unavailable_required else "unavailable core modules: " + ", ".join(unavailable_required),
        ),
        _row(
            "accepted_promoter_cis_handoff",
            not plantcare_issues,
            str(analysis_modules / "08_promoter" / "plantcare_submission"),
            "PlantCARE handoff is available when promoter cis is missing_input"
            if not plantcare_issues
            else "PlantCARE handoff issues: " + ", ".join(plantcare_issues),
        ),
        _row(
            "accepted_expression_optional_skip",
            not expression_issues,
            str(analysis_modules / "13_expression"),
            "expression module is available or explicitly skipped_optional"
            if not expression_issues
            else "expression status issues: " + ", ".join(expression_issues),
        ),
        _row(
            "jcvi_interspecies_required",
            not jcvi_issues,
            str(analysis_modules / "10_synteny_jcvi"),
            "JCVI inter-species collinearity has run evidence and pair manifest"
            if not jcvi_issues
            else "JCVI inter-species issues: " + ", ".join(jcvi_issues),
        ),
        _row(
            "mcscanx_self_intraspecies_required",
            not mcscanx_issues,
            str(analysis_modules / "11_mcscanx"),
            "MCScanX self intra-species duplication and circlize outputs are present"
            if not mcscanx_issues
            else "MCScanX self intra-species issues: " + ", ".join(mcscanx_issues),
        ),
        _row(
            "kaks_partial_is_diagnosed",
            not kaks_issues,
            str(analysis_modules / "14_duplication_retention_kaks"),
            "Ka/Ks module is available or partial with failure diagnostics"
            if not kaks_issues
            else "Ka/Ks diagnostics issues: " + ", ".join(kaks_issues),
        ),
        _row(
            "report_package_files",
            not report_issues and not reproducibility_issues,
            str(analysis_modules / "report"),
            "report package contains publication report files and reproduction boundary text"
            if not report_issues and not reproducibility_issues
            else "report issues: " + ", ".join(report_issues + reproducibility_issues),
        ),
    ]
    failed_checks = [row["check"] for row in rows if row["status"] == "failed"]
    rows.append(
        _row(
            "overall_reference_mvp_package",
            not failed_checks,
            str(analysis_modules),
            "Reference MVP package passes with MCScanX self intra-species and JCVI inter-species separated"
            if not failed_checks
            else "failed checks: " + ", ".join(failed_checks),
        )
    )
    return rows


def summarize_audit(rows: list[dict[str, str]]) -> dict[str, int | bool]:
    passed = sum(1 for row in rows if row["status"] == "passed")
    failed = sum(1 for row in rows if row["status"] == "failed")
    return {"passed": passed, "failed": failed, "complete": failed == 0}


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    summary = summarize_audit(rows)
    overall = "passed" if summary["complete"] else "failed"
    lines = [
        "# Real Reference MVP Package Audit",
        "",
        f"Overall status: {overall}",
        f"Passed: {summary['passed']}",
        f"Failed: {summary['failed']}",
        "",
        "This audit treats MCScanX self intra-species duplication/circlize as required and JCVI inter-species collinearity as a separate required branch.",
        "",
        "| check | status | evidence | note |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(row[field]) for field in FIELDNAMES) + " |")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-modules", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Write failed audit rows but exit 0, useful for non-Reference smoke workflows.",
    )
    args = parser.parse_args()
    rows = audit_real_reference_package(args.analysis_modules)
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)
    complete = bool(summarize_audit(rows)["complete"])
    raise SystemExit(0 if complete or args.allow_incomplete else 1)


if __name__ == "__main__":
    main()
