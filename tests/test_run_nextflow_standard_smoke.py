import subprocess
import sys

from bin.genefam.run_nextflow_standard_smoke import build_nextflow_command, expected_published_outputs


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


def test_expected_published_outputs_cover_standard_user_results(tmp_path):
    standard_outdir = tmp_path / "standard"

    assert expected_published_outputs(standard_outdir) == [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/family_candidates.tsv",
        standard_outdir / "tables/family_counts.tsv",
        standard_outdir / "tables/alignment_manifest.tsv",
        standard_outdir / "tables/phylogeny_manifest.tsv",
        standard_outdir / "tables/chromosome_locations.tsv",
        standard_outdir / "sequences/family_members.faa",
        standard_outdir / "report/report_index.tsv",
        standard_outdir / "report/plot_manifest.tsv",
        standard_outdir / "report/final_report.md",
        standard_outdir / "plots/family_counts.pdf",
        standard_outdir / "plots/family_counts.png",
    ]


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
