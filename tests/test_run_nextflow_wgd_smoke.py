import subprocess
import sys

from bin.genefam.run_nextflow_wgd_smoke import build_nextflow_command, expected_published_outputs


def test_build_nextflow_wgd_command_targets_duplication_retention_branch(tmp_path):
    inputs_dir = tmp_path / "inputs"
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        duplicates=str(inputs_dir / "duplicates.tsv"),
        family_members=str(inputs_dir / "family_members.tsv"),
        kaks_pairs=str(inputs_dir / "kaks_pairs.tsv"),
        pangenome_classes=str(inputs_dir / "pangenome_classes.tsv"),
        events_config="configs/wgd_events.brassicaceae.yaml",
        outdir="results/nextflow_wgd_smoke/wgd",
    )

    assert command == [
        "nextflow",
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
        "--config",
        "configs/example.config.yaml",
        "--run_duplication_retention",
        "true",
        "--duplicates",
        str(inputs_dir / "duplicates.tsv"),
        "--family_members",
        str(inputs_dir / "family_members.tsv"),
        "--kaks_pairs",
        str(inputs_dir / "kaks_pairs.tsv"),
        "--pangenome_classes",
        str(inputs_dir / "pangenome_classes.tsv"),
        "--events_config",
        "configs/wgd_events.brassicaceae.yaml",
        "--ks_bins",
        "0.3,0.8,1.5",
        "--wgd_event_args",
        "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta",
        "--outdir",
        "results/nextflow_wgd_smoke/wgd",
    ]


def test_build_nextflow_wgd_command_can_use_raw_mcscanx_kaks_inputs(tmp_path):
    inputs_dir = tmp_path / "inputs"
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        family_members=str(inputs_dir / "family_members.tsv"),
        events_config="configs/wgd_events.brassicaceae.yaml",
        outdir="results/nextflow_wgd_raw_smoke/wgd",
        mcscanx_collinearity="tests/fixtures/mcscanx/sample.collinearity",
        kaks_results="tests/fixtures/kaks/kaks_calculator.tsv",
    )

    assert "--duplicates" not in command
    assert "--kaks_pairs" not in command
    assert "--mcscanx_collinearity" in command
    assert command[command.index("--mcscanx_collinearity") + 1] == "tests/fixtures/mcscanx/sample.collinearity"
    assert "--kaks_results" in command
    assert command[command.index("--kaks_results") + 1] == "tests/fixtures/kaks/kaks_calculator.tsv"


def test_expected_published_outputs_cover_wgd_results(tmp_path):
    outdir = tmp_path / "wgd"

    assert expected_published_outputs(outdir) == [
        outdir / "tables/wgd_run_config_snapshot.tsv",
        outdir / "tables/normalized_duplicate_types.tsv",
        outdir / "tables/family_duplicate_classification.tsv",
        outdir / "tables/wgd_layers.tsv",
        outdir / "tables/wgd_event_evidence.tsv",
        outdir / "tables/family_wgd_event_membership.tsv",
        outdir / "tables/family_event_retention_summary.tsv",
        outdir / "tables/retention_enrichment.tsv",
        outdir / "plots/ks_distribution.pdf",
        outdir / "plots/ks_distribution.png",
        outdir / "tables/pangenome_kaks.tsv",
        outdir / "tables/pangenome_kaks_summary.tsv",
        outdir / "tables/pangenome_kaks_skipped.tsv",
        outdir / "plots/pangenome_kaks.pdf",
        outdir / "plots/pangenome_kaks.png",
        outdir / "report/report_index.tsv",
        outdir / "report/final_report.md",
    ]


def test_expected_published_outputs_can_include_raw_handoff_results(tmp_path):
    outdir = tmp_path / "wgd"

    outputs = expected_published_outputs(outdir, raw_handoff=True)

    assert outdir / "mcscanx_kaks_handoff/tables/syntenic_pairs.tsv" in outputs
    assert outdir / "mcscanx_kaks_handoff/tables/duplicate_types.tsv" in outputs
    assert outdir / "mcscanx_kaks_handoff/tables/kaks_pairs.tsv" in outputs
    assert outdir / "mcscanx_kaks_handoff/mcscanx_kaks_handoff.md" in outputs


def test_run_nextflow_wgd_smoke_cli_reports_missing_nextflow(tmp_path):
    outdir = tmp_path / "nextflow_wgd_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_nextflow_wgd_smoke.py",
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
    assert (outdir / "nextflow_wgd_smoke.tsv").read_text(encoding="utf-8").startswith(
        "check\tstatus\texit_code\tcommand\tnote\n"
    )
    assert "missing_nextflow" in (outdir / "nextflow_wgd_smoke.tsv").read_text(encoding="utf-8")
    assert (
        "--wgd_event_args '--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta'"
        in (outdir / "nextflow_wgd_smoke.tsv").read_text(encoding="utf-8")
    )
    assert "Nextflow WGD Event Smoke" in (outdir / "nextflow_wgd_smoke.md").read_text(encoding="utf-8")
