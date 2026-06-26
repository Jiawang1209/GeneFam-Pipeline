import subprocess
import sys

from bin.genefam.run_container_profile_smoke import (
    build_container_smoke_command,
    runtime_command_for_profile,
    run_container_profile_smoke,
)


def test_runtime_command_for_profile_maps_container_profiles():
    assert runtime_command_for_profile("docker") == "docker"
    assert runtime_command_for_profile("apptainer") == "apptainer"


def test_build_container_smoke_command_uses_requested_profile():
    command = build_container_smoke_command(
        nextflow_bin="nextflow",
        profile="docker",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/container_profile_smoke/docker/mock_mvp",
    )

    assert command[:7] == [
        "nextflow",
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
        "-profile",
        "docker",
    ]
    assert "--mock_mvp" in command
    assert "true" in command


def test_run_container_profile_smoke_reports_missing_runtime_before_nextflow():
    row = run_container_profile_smoke(
        profile="docker",
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/container_profile_smoke",
        which=lambda command: "",
        path_exists=lambda path: True,
    )

    assert row["check"] == "docker_profile_smoke"
    assert row["status"] == "missing_runtime"
    assert row["exit_code"] == "127"
    assert "docker was not found" in row["note"]
    assert "bash results/readiness/runtime_bootstrap.sh" in row["note"]
    assert "run_container_profile_smoke.py --profile docker" in row["note"]
    assert "results/container_profile_smoke/docker/container_profile_smoke.md" in row["note"]
    assert "--outdir results/container_profile_smoke/mock_mvp" in row["command"]
    assert "docker/docker/mock_mvp" not in row["command"]


def test_run_container_profile_smoke_reports_missing_nextflow_after_runtime_exists():
    row = run_container_profile_smoke(
        profile="apptainer",
        nextflow_bin="/missing/nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/container_profile_smoke",
        which=lambda command: "/usr/bin/apptainer" if command == "apptainer" else "",
        path_exists=lambda path: path == "/usr/bin/apptainer",
    )

    assert row["check"] == "apptainer_profile_smoke"
    assert row["status"] == "missing_nextflow"
    assert "nextflow was not found" in row["note"]


def test_run_container_profile_smoke_does_not_duplicate_profile_named_outdir():
    row = run_container_profile_smoke(
        profile="docker",
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/container_profile_smoke/docker",
        which=lambda command: "",
        path_exists=lambda path: True,
    )

    assert "--outdir results/container_profile_smoke/docker/mock_mvp" in row["command"]
    assert "docker/docker/mock_mvp" not in row["command"]


def test_run_container_profile_smoke_cli_writes_outputs(tmp_path):
    outdir = tmp_path / "container_profile_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_container_profile_smoke.py",
            "--profile",
            "docker",
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
    assert (outdir / "container_profile_smoke.tsv").read_text(encoding="utf-8").startswith(
        "check\tprofile\tstatus\texit_code\tcommand\tnote\n"
    )
    assert "missing_runtime" in (outdir / "container_profile_smoke.tsv").read_text(encoding="utf-8")
    assert "Container Profile Smoke" in (outdir / "container_profile_smoke.md").read_text(encoding="utf-8")
