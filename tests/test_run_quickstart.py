import subprocess
import sys
from pathlib import Path

from bin.genefam.run_quickstart import run_quickstart, write_markdown, write_tsv


def test_run_quickstart_summarizes_standard_and_wgd_outputs(tmp_path):
    def standard_runner(config, groups, mock_evidence_dir, outdir, expression_matrix=None):
        report = outdir / "report/final_report.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("# Standard\n", encoding="utf-8")
        return {
            "standard_final_report": report,
            "family_candidates": outdir / "tables/family_candidates.tsv",
        }

    def wgd_runner(nextflow_bin, example_dir, events_config, outdir, conda_env=None):
        report = outdir / "report/final_report.md"
        evidence = outdir / "tables/wgd_event_evidence.tsv"
        report.parent.mkdir(parents=True, exist_ok=True)
        evidence.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("# WGD\n", encoding="utf-8")
        evidence.write_text("event_name\nalpha\nbeta\ngamma\ntheta\n", encoding="utf-8")
        return {"status": "passed", "exit_code": "0", "command": "nextflow run ...", "note": ""}

    rows = run_quickstart(
        config=Path("configs/example.config.yaml"),
        groups=Path("configs/species_groups.yaml"),
        mock_evidence_dir=Path("tests/fixtures/mock_evidence"),
        example_dir=Path("examples/prepared_wgd_handoff"),
        events_config="configs/wgd_events.brassicaceae.yaml",
        conda_env="GeneFamilyFlow",
        outdir=tmp_path,
        standard_runner=standard_runner,
        wgd_runner=wgd_runner,
    )

    assert rows == [
        {
            "step": "standard_branch_smoke",
            "status": "passed",
            "path": str(tmp_path / "standard_smoke/report/final_report.md"),
            "note": "family candidates and standard report generated",
        },
        {
            "step": "prepared_wgd_handoff",
            "status": "passed",
            "path": str(tmp_path / "example_prepared_wgd/report/final_report.md"),
            "note": "alpha beta gamma theta evidence generated",
        },
    ]


def test_write_quickstart_summaries(tmp_path):
    rows = [
        {"step": "standard_branch_smoke", "status": "passed", "path": "results/x/final_report.md", "note": "ok"},
        {"step": "prepared_wgd_handoff", "status": "passed", "path": "results/y/final_report.md", "note": "ok"},
    ]

    write_tsv(rows, tmp_path / "quickstart_summary.tsv")
    write_markdown(rows, tmp_path / "quickstart_summary.md")

    assert (tmp_path / "quickstart_summary.tsv").read_text(encoding="utf-8").startswith(
        "step\tstatus\tpath\tnote\n"
    )
    text = (tmp_path / "quickstart_summary.md").read_text(encoding="utf-8")
    assert "# GeneFam-Pipeline Quickstart Summary" in text
    assert "standard_branch_smoke" in text
    assert "prepared_wgd_handoff" in text


def test_run_quickstart_cli_writes_summary_files(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_quickstart.py",
            "--skip-wgd",
            "--outdir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "standard_branch_smoke" in (tmp_path / "quickstart_summary.tsv").read_text(encoding="utf-8")
    assert "GeneFam-Pipeline Quickstart Summary" in (tmp_path / "quickstart_summary.md").read_text(
        encoding="utf-8"
    )
