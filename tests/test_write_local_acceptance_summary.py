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
        quickstart_status=0,
        delivery_status=0,
        release_outdir=Path("results/release_checks"),
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
    assert "results/delivery_bundle/delivery_bundle.md" in markdown


def test_build_acceptance_rows_reports_all_passed_status():
    rows = build_acceptance_rows(
        release_status=0,
        quickstart_status=0,
        delivery_status=0,
        release_outdir=Path("release"),
        quickstart_outdir=Path("quickstart"),
        delivery_outdir=Path("delivery"),
    )

    assert {row.status for row in rows} == {"passed"}
    assert [row.path for row in rows] == [
        Path("release/release_checks.md"),
        Path("quickstart/quickstart_summary.md"),
        Path("delivery/delivery_bundle.md"),
    ]
