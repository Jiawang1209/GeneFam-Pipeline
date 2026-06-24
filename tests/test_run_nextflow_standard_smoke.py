import subprocess
import sys

from bin.genefam.run_nextflow_standard_smoke import build_nextflow_command


def test_build_nextflow_command_targets_standard_identification_branch():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_smoke/standard",
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
        "--run_identification",
        "true",
        "--mock_external_tools",
        "true",
        "--mock_evidence_dir",
        "tests/fixtures/mock_evidence",
        "--outdir",
        "results/nextflow_standard_smoke/standard",
    ]


def test_build_nextflow_command_can_use_activated_profile():
    command = build_nextflow_command(
        nextflow_bin="/envs/GeneFamilyFlow/bin/nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_smoke/standard",
        profile="activated",
    )

    assert command[:5] == [
        "/envs/GeneFamilyFlow/bin/nextflow",
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
    ]
    assert "-profile" in command
    assert "activated" in command


def test_run_nextflow_standard_smoke_cli_reports_missing_nextflow(tmp_path):
    outdir = tmp_path / "nextflow_standard_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_nextflow_standard_smoke.py",
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
    assert (outdir / "nextflow_standard_smoke.tsv").read_text(encoding="utf-8").startswith(
        "check\tstatus\texit_code\tcommand\tnote\n"
    )
    assert "missing_nextflow" in (outdir / "nextflow_standard_smoke.tsv").read_text(encoding="utf-8")
    assert "Nextflow Standard Branch Smoke" in (outdir / "nextflow_standard_smoke.md").read_text(
        encoding="utf-8"
    )
