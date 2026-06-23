import subprocess
import sys

from bin.genefam.run_nextflow_smoke import build_nextflow_command


def test_build_nextflow_command_targets_mock_mvp_branch():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_smoke/mock_mvp",
    )

    assert command == [
        "nextflow",
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
        "--config",
        "configs/example.config.yaml",
        "--groups",
        "configs/species_groups.yaml",
        "--mock_mvp",
        "true",
        "--mock_evidence_dir",
        "tests/fixtures/mock_evidence",
        "--outdir",
        "results/nextflow_smoke/mock_mvp",
    ]


def test_run_nextflow_smoke_cli_reports_missing_nextflow(tmp_path):
    outdir = tmp_path / "nextflow_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_nextflow_smoke.py",
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
    assert (outdir / "nextflow_smoke.tsv").read_text(encoding="utf-8").startswith(
        "check\tstatus\texit_code\tcommand\tnote\n"
    )
    assert "missing_nextflow" in (outdir / "nextflow_smoke.tsv").read_text(encoding="utf-8")
    assert "Nextflow Mock MVP Smoke" in (outdir / "nextflow_smoke.md").read_text(encoding="utf-8")
