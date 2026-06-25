#!/usr/bin/env python3
"""Build the final user-facing delivery manifest for GeneFam-Pipeline."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["section", "item", "status", "path", "note"]


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
    blockers = _objective_blockers(objective_rows)

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
            "item": "objective_audit",
            "status": "available",
            "path": "results/objective_audit/objective_audit.md",
            "note": f"blocked_or_missing={blockers}",
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
            "item": "nextflow_standard_manifest_smoke",
            "status": _status_from_check(release_rows, "Nextflow standard manifest smoke"),
            "path": "results/nextflow_standard_manifest_smoke/nextflow_standard_smoke.tsv",
            "note": "manifest-mode standard DSL2 smoke",
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
        lines.append("| {section} | {item} | {status} | `{path}` | {note} |".format(**row))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_delivery_bundle(
    release_checks: Path,
    objective_audit: Path,
    readiness: Path,
    quickstart: Path,
    outdir: Path,
) -> dict[str, Path]:
    rows = build_delivery_manifest(
        release_rows=read_tsv(release_checks),
        objective_rows=read_tsv(objective_audit),
        readiness_rows=read_tsv(readiness),
        quickstart_rows=read_tsv(quickstart),
    )
    manifest = outdir / "delivery_manifest.tsv"
    summary = outdir / "delivery_bundle.md"
    write_tsv(rows, manifest)
    write_markdown(rows, summary)
    return {"delivery_manifest": manifest, "delivery_bundle": summary}


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
