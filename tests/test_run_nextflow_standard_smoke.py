import subprocess
import sys

from bin.genefam.run_nextflow_standard_smoke import (
    build_nextflow_command,
    expected_published_outputs,
    expected_single_tool_outputs,
    load_standard_params,
)


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
        "--use_hmmer",
        "true",
        "--use_diamond",
        "true",
        "--final_rule",
        "intersection",
        "--mock_external_tools",
        "true",
        "--standard_stop_after_family_candidates",
        "false",
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


def test_build_nextflow_command_passes_identification_params():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_smoke/standard",
        use_hmmer=False,
        use_diamond=True,
        final_rule="union",
        mock_external_tools=False,
        stop_after_family_candidates=True,
    )

    assert "--use_hmmer" in command
    assert command[command.index("--use_hmmer") + 1] == "false"
    assert "--use_diamond" in command
    assert command[command.index("--use_diamond") + 1] == "true"
    assert "--final_rule" in command
    assert command[command.index("--final_rule") + 1] == "union"
    assert "--mock_external_tools" in command
    assert command[command.index("--mock_external_tools") + 1] == "false"
    assert "--standard_stop_after_family_candidates" in command
    assert command[command.index("--standard_stop_after_family_candidates") + 1] == "true"


def test_build_nextflow_command_preserves_string_boolean_params():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_smoke/standard",
        use_hmmer="false",
        use_diamond="true",
    )

    assert command[command.index("--use_hmmer") + 1] == "false"
    assert command[command.index("--use_diamond") + 1] == "true"


def test_load_standard_params_reads_yaml_tool_and_mock_flags(tmp_path):
    config = tmp_path / "disabled_hmmer.yaml"
    config.write_text(
        "\n".join(
            [
                "identification:",
                "  use_hmmer: false",
                "  use_diamond: true",
                "  final_rule: union",
                "dev:",
                "  mock_external_tools: false",
            ]
        ),
        encoding="utf-8",
    )

    assert load_standard_params(config) == {
        "use_hmmer": "false",
        "use_diamond": "true",
        "final_rule": "union",
        "mock_external_tools": "false",
    }


def test_expected_published_outputs_cover_standard_user_results(tmp_path):
    standard_outdir = tmp_path / "standard"

    assert expected_published_outputs(standard_outdir) == [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/run_config_snapshot.tsv",
        standard_outdir / "tables/family_candidates.tsv",
        standard_outdir / "tables/family_counts.tsv",
        standard_outdir / "tables/alignment_manifest.tsv",
        standard_outdir / "tables/phylogeny_manifest.tsv",
        standard_outdir / "tables/motif_summary.tsv",
        standard_outdir / "tables/chromosome_locations.tsv",
        standard_outdir / "sequences/family_members.faa",
        standard_outdir / "report/report_index.tsv",
        standard_outdir / "report/plot_manifest.tsv",
        standard_outdir / "report/final_report.md",
        standard_outdir / "plots/family_counts.pdf",
        standard_outdir / "plots/family_counts.png",
    ]


def test_expected_single_tool_outputs_stop_after_family_candidates(tmp_path):
    standard_outdir = tmp_path / "standard"

    assert expected_single_tool_outputs(standard_outdir) == [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/family_candidates.tsv",
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
