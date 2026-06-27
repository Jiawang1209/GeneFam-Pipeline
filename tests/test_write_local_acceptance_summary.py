import csv
from pathlib import Path

from bin.genefam.write_local_acceptance_summary import (
    build_acceptance_rows,
    write_acceptance_summary,
)


def test_write_local_acceptance_summary_records_step_statuses(tmp_path):
    outdir = tmp_path / "acceptance"

    write_acceptance_summary(
        release_status=1,
        publication_status=0,
        standard_report_index_status=0,
        wgd_publication_status=0,
        wgd_report_index_status=0,
        quickstart_status=0,
        delivery_status=0,
        release_outdir=Path("results/release_checks"),
        publication_outdir=Path("results/publication_report_audit"),
        report_index_outdir=Path("results/report_index_audit"),
        quickstart_outdir=Path("results/quickstart"),
        delivery_outdir=Path("results/delivery_bundle"),
        outdir=outdir,
    )

    with (outdir / "local_acceptance_summary.tsv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    assert rows == [
        {
            "step": "release_gate",
            "status": "failed",
            "exit_code": "1",
            "path": "results/release_checks/release_checks.md",
            "note": "required release gate and objective evidence",
        },
        {
            "step": "publication_report_audit",
            "status": "passed",
            "exit_code": "0",
            "path": "results/publication_report_audit/publication_report_audit.md",
            "note": "paper-style report closure evidence",
        },
        {
            "step": "standard_report_index_audit",
            "status": "passed",
            "exit_code": "0",
            "path": "results/report_index_audit/standard_report_index_audit.md",
            "note": "standard report-index closure evidence",
        },
        {
            "step": "wgd_publication_report_audit",
            "status": "passed",
            "exit_code": "0",
            "path": "results/publication_report_audit/wgd_publication_report_audit.md",
            "note": "WGD report closure evidence",
        },
        {
            "step": "wgd_report_index_audit",
            "status": "passed",
            "exit_code": "0",
            "path": "results/report_index_audit/wgd_report_index_audit.md",
            "note": "WGD report-index closure evidence",
        },
        {
            "step": "quickstart_handoff",
            "status": "passed",
            "exit_code": "0",
            "path": "results/quickstart/quickstart_summary.md",
            "note": "standard and prepared WGD handoff quickstart",
        },
        {
            "step": "delivery_bundle",
            "status": "passed",
            "exit_code": "0",
            "path": "results/delivery_bundle/delivery_bundle.md",
            "note": "final user-facing delivery index",
        },
    ]

    markdown = (outdir / "local_acceptance_summary.md").read_text(encoding="utf-8")
    assert "Overall status: failed" in markdown
    assert "results/release_checks/release_checks.md" in markdown
    assert "results/publication_report_audit/publication_report_audit.md" in markdown
    assert "results/report_index_audit/standard_report_index_audit.md" in markdown
    assert "standard report-index closure evidence" in markdown
    assert "results/publication_report_audit/wgd_publication_report_audit.md" in markdown
    assert "results/report_index_audit/wgd_report_index_audit.md" in markdown
    assert "WGD report-index closure evidence" in markdown
    assert "results/delivery_bundle/delivery_bundle.md" in markdown


def test_build_acceptance_rows_reports_all_passed_status():
    rows = build_acceptance_rows(
        release_status=0,
        publication_status=0,
        standard_report_index_status=0,
        wgd_publication_status=0,
        wgd_report_index_status=0,
        quickstart_status=0,
        delivery_status=0,
        release_outdir=Path("release"),
        publication_outdir=Path("publication"),
        report_index_outdir=Path("report_index"),
        quickstart_outdir=Path("quickstart"),
        delivery_outdir=Path("delivery"),
    )

    assert {row.status for row in rows} == {"passed"}
    assert [row.path for row in rows] == [
        Path("release/release_checks.md"),
        Path("publication/publication_report_audit.md"),
        Path("report_index/standard_report_index_audit.md"),
        Path("publication/wgd_publication_report_audit.md"),
        Path("report_index/wgd_report_index_audit.md"),
        Path("quickstart/quickstart_summary.md"),
        Path("delivery/delivery_bundle.md"),
    ]
