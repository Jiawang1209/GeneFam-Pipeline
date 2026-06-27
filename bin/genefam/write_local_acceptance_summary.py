#!/usr/bin/env python3
"""Write a compact summary for the local acceptance wrapper."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AcceptanceRow:
    step: str
    status: str
    exit_code: int
    path: Path
    note: str


def _status_label(exit_code: int) -> str:
    return "passed" if exit_code == 0 else "failed"


def build_acceptance_rows(
    *,
    release_status: int,
    publication_status: int,
    standard_report_index_status: int,
    wgd_publication_status: int,
    wgd_report_index_status: int,
    figure_gallery_status: int,
    delivery_manifest_status: int,
    quickstart_status: int,
    delivery_status: int,
    final_stage_blocker_status: str,
    final_stage_blocker_note: str,
    release_outdir: Path,
    publication_outdir: Path,
    report_index_outdir: Path,
    quickstart_outdir: Path,
    delivery_outdir: Path,
) -> list[AcceptanceRow]:
    return [
        AcceptanceRow(
            step="release_gate",
            status=_status_label(release_status),
            exit_code=release_status,
            path=release_outdir / "release_checks.md",
            note="required release gate and objective evidence",
        ),
        AcceptanceRow(
            step="publication_report_audit",
            status=_status_label(publication_status),
            exit_code=publication_status,
            path=publication_outdir / "publication_report_audit.md",
            note="paper-style report closure evidence",
        ),
        AcceptanceRow(
            step="standard_report_index_audit",
            status=_status_label(standard_report_index_status),
            exit_code=standard_report_index_status,
            path=report_index_outdir / "standard_report_index_audit.md",
            note="standard report-index closure evidence",
        ),
        AcceptanceRow(
            step="wgd_publication_report_audit",
            status=_status_label(wgd_publication_status),
            exit_code=wgd_publication_status,
            path=publication_outdir / "wgd_publication_report_audit.md",
            note="WGD report closure evidence",
        ),
        AcceptanceRow(
            step="wgd_report_index_audit",
            status=_status_label(wgd_report_index_status),
            exit_code=wgd_report_index_status,
            path=report_index_outdir / "wgd_report_index_audit.md",
            note="WGD report-index closure evidence",
        ),
        AcceptanceRow(
            step="figure_gallery_audit",
            status=_status_label(figure_gallery_status),
            exit_code=figure_gallery_status,
            path=Path("results/delivery_bundle_smoke/figure_gallery_audit.md"),
            note="global figure gallery coverage and link evidence",
        ),
        AcceptanceRow(
            step="delivery_manifest_audit",
            status=_status_label(delivery_manifest_status),
            exit_code=delivery_manifest_status,
            path=Path("results/delivery_bundle_smoke/delivery_manifest_audit.md"),
            note="delivery manifest handoff path evidence",
        ),
        AcceptanceRow(
            step="quickstart_handoff",
            status=_status_label(quickstart_status),
            exit_code=quickstart_status,
            path=quickstart_outdir / "quickstart_summary.md",
            note="standard and prepared WGD handoff quickstart",
        ),
        AcceptanceRow(
            step="delivery_bundle",
            status=_status_label(delivery_status),
            exit_code=delivery_status,
            path=delivery_outdir / "delivery_bundle.md",
            note="final user-facing delivery index",
        ),
        AcceptanceRow(
            step="final_stage_blocker",
            status=final_stage_blocker_status,
            exit_code=0,
            path=Path("results/objective_audit/objective_audit.md"),
            note=final_stage_blocker_note,
        ),
    ]


def _overall_status(rows: list[AcceptanceRow]) -> str:
    if any(row.status == "failed" for row in rows):
        return "failed"
    if any(row.status in {"blocked", "missing"} for row in rows):
        return "blocked"
    return "passed"


def write_acceptance_summary(
    *,
    release_status: int,
    publication_status: int,
    standard_report_index_status: int,
    wgd_publication_status: int,
    wgd_report_index_status: int,
    figure_gallery_status: int,
    delivery_manifest_status: int,
    quickstart_status: int,
    delivery_status: int,
    final_stage_blocker_status: str,
    final_stage_blocker_note: str,
    release_outdir: Path,
    publication_outdir: Path,
    report_index_outdir: Path,
    quickstart_outdir: Path,
    delivery_outdir: Path,
    outdir: Path,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    rows = build_acceptance_rows(
        release_status=release_status,
        publication_status=publication_status,
        standard_report_index_status=standard_report_index_status,
        wgd_publication_status=wgd_publication_status,
        wgd_report_index_status=wgd_report_index_status,
        figure_gallery_status=figure_gallery_status,
        delivery_manifest_status=delivery_manifest_status,
        quickstart_status=quickstart_status,
        delivery_status=delivery_status,
        final_stage_blocker_status=final_stage_blocker_status,
        final_stage_blocker_note=final_stage_blocker_note,
        release_outdir=release_outdir,
        publication_outdir=publication_outdir,
        report_index_outdir=report_index_outdir,
        quickstart_outdir=quickstart_outdir,
        delivery_outdir=delivery_outdir,
    )

    tsv_path = outdir / "local_acceptance_summary.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=["step", "status", "exit_code", "path", "note"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "step": row.step,
                    "status": row.status,
                    "exit_code": row.exit_code,
                    "path": row.path,
                    "note": row.note,
                }
            )

    overall_status = _overall_status(rows)
    markdown_lines = [
        "# GeneFam-Pipeline Local Acceptance Summary",
        "",
        f"Overall status: {overall_status}",
        "",
        "| Step | Status | Exit code | Path | Note |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        markdown_lines.append(
            f"| {row.step} | {row.status} | {row.exit_code} | {row.path} | {row.note} |"
        )
    markdown_lines.append("")
    (outdir / "local_acceptance_summary.md").write_text(
        "\n".join(markdown_lines),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-status", type=int, required=True)
    parser.add_argument("--publication-status", type=int, required=True)
    parser.add_argument("--standard-report-index-status", type=int, required=True)
    parser.add_argument("--wgd-publication-status", type=int, required=True)
    parser.add_argument("--wgd-report-index-status", type=int, required=True)
    parser.add_argument("--figure-gallery-status", type=int, required=True)
    parser.add_argument("--delivery-manifest-status", type=int, required=True)
    parser.add_argument("--quickstart-status", type=int, required=True)
    parser.add_argument("--delivery-status", type=int, required=True)
    parser.add_argument("--final-stage-blocker-status", choices=["passed", "blocked", "missing"], required=True)
    parser.add_argument("--final-stage-blocker-note", required=True)
    parser.add_argument("--release-outdir", type=Path, required=True)
    parser.add_argument("--publication-outdir", type=Path, required=True)
    parser.add_argument("--report-index-outdir", type=Path, required=True)
    parser.add_argument("--quickstart-outdir", type=Path, required=True)
    parser.add_argument("--delivery-outdir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_acceptance_summary(
        release_status=args.release_status,
        publication_status=args.publication_status,
        standard_report_index_status=args.standard_report_index_status,
        wgd_publication_status=args.wgd_publication_status,
        wgd_report_index_status=args.wgd_report_index_status,
        figure_gallery_status=args.figure_gallery_status,
        delivery_manifest_status=args.delivery_manifest_status,
        quickstart_status=args.quickstart_status,
        delivery_status=args.delivery_status,
        final_stage_blocker_status=args.final_stage_blocker_status,
        final_stage_blocker_note=args.final_stage_blocker_note,
        release_outdir=args.release_outdir,
        publication_outdir=args.publication_outdir,
        report_index_outdir=args.report_index_outdir,
        quickstart_outdir=args.quickstart_outdir,
        delivery_outdir=args.delivery_outdir,
        outdir=args.outdir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
