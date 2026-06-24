import csv
import subprocess
import sys

from bin.genefam.run_nextflow_single_tool_smoke import (
    FIELDNAMES,
    build_single_tool_configs,
    write_markdown,
    write_tsv,
)


def read_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_build_single_tool_configs_writes_non_mock_hmmer_and_diamond_configs(tmp_path):
    configs = build_single_tool_configs("configs/example.config.yaml", tmp_path)

    assert [case.name for case in configs] == ["hmmer_only", "diamond_only"]
    hmmer_text = configs[0].config_path.read_text(encoding="utf-8")
    diamond_text = configs[1].config_path.read_text(encoding="utf-8")

    assert "use_hmmer: true" in hmmer_text
    assert "use_diamond: false" in hmmer_text
    assert "final_rule: hmmer_only" in hmmer_text
    assert "mock_external_tools: false" in hmmer_text

    assert "use_hmmer: false" in diamond_text
    assert "use_diamond: true" in diamond_text
    assert "final_rule: union" in diamond_text
    assert "mock_external_tools: false" in diamond_text


def test_write_outputs_record_both_single_tool_rows(tmp_path):
    rows = [
        {
            "check": "nextflow_standard_hmmer_only",
            "status": "passed",
            "exit_code": "0",
            "command": "nextflow run --use_hmmer true --use_diamond false",
            "note": "ok",
        },
        {
            "check": "nextflow_standard_diamond_only",
            "status": "passed",
            "exit_code": "0",
            "command": "nextflow run --use_hmmer false --use_diamond true",
            "note": "ok",
        },
    ]

    write_tsv(rows, tmp_path / "single_tool.tsv")
    write_markdown(rows, tmp_path / "single_tool.md")

    assert read_tsv(tmp_path / "single_tool.tsv") == rows
    markdown = (tmp_path / "single_tool.md").read_text(encoding="utf-8")
    assert "# Nextflow Standard Single-Tool Smoke" in markdown
    assert "nextflow_standard_hmmer_only" in markdown
    assert "nextflow_standard_diamond_only" in markdown


def test_run_nextflow_single_tool_smoke_cli_reports_missing_nextflow(tmp_path):
    outdir = tmp_path / "single_tool"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_nextflow_single_tool_smoke.py",
            "--nextflow-bin",
            "/definitely/missing/nextflow",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    rows = read_tsv(outdir / "nextflow_single_tool_smoke.tsv")
    assert [row["check"] for row in rows] == [
        "nextflow_standard_hmmer_only",
        "nextflow_standard_diamond_only",
    ]
    assert {row["status"] for row in rows} == {"missing_nextflow"}
    assert FIELDNAMES == ["check", "status", "exit_code", "command", "note"]
