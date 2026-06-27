import subprocess
import sys
from pathlib import Path

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
        "--run_feature_summary",
        "false",
        "--run_mcscanx_circlize",
        "false",
        "--run_promoter",
        "false",
        "--run_promoter_cis",
        "false",
        "--run_ppi",
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


def test_build_nextflow_command_can_enable_standard_visualization_modules():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_feature_smoke/standard",
        run_feature_summary=True,
        run_mcscanx_circlize=True,
        syntenic_pairs="tests/fixtures/mcscanx/syntenic_pairs.tsv",
    )

    assert "--run_feature_summary" in command
    assert command[command.index("--run_feature_summary") + 1] == "true"
    assert "--run_mcscanx_circlize" in command
    assert command[command.index("--run_mcscanx_circlize") + 1] == "true"
    assert "--syntenic_pairs" in command
    assert command[command.index("--syntenic_pairs") + 1] == "tests/fixtures/mcscanx/syntenic_pairs.tsv"


def test_build_nextflow_command_can_enable_promoter_extraction_for_standard_reports():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_feature_smoke/standard",
        run_promoter=True,
    )

    assert "--run_promoter" in command
    assert command[command.index("--run_promoter") + 1] == "true"


def test_build_nextflow_command_can_enable_full_publication_visualization_modules():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_publication_smoke/standard",
        run_feature_summary=True,
        run_mcscanx_circlize=True,
        syntenic_pairs="tests/fixtures/mcscanx/syntenic_pairs.tsv",
        run_promoter_cis=True,
        promoter_cis_elements="tests/fixtures/promoter_cis/plantcare.tsv",
        run_ppi=True,
        ppi_edges="tests/fixtures/ppi/ppi_edges.tsv",
        ppi_nodes="tests/fixtures/ppi/ppi_nodes.tsv",
        expression_matrix="tests/fixtures/expression/family_expression.tsv",
        expression_metadata="tests/fixtures/expression/sample_metadata.tsv",
    )

    assert command[command.index("--run_feature_summary") + 1] == "true"
    assert command[command.index("--run_mcscanx_circlize") + 1] == "true"
    assert command[command.index("--run_promoter_cis") + 1] == "true"
    assert command[command.index("--promoter_cis_elements") + 1] == "tests/fixtures/promoter_cis/plantcare.tsv"
    assert command[command.index("--run_ppi") + 1] == "true"
    assert command[command.index("--ppi_edges") + 1] == "tests/fixtures/ppi/ppi_edges.tsv"
    assert command[command.index("--ppi_nodes") + 1] == "tests/fixtures/ppi/ppi_nodes.tsv"
    assert command[command.index("--expression_matrix") + 1] == "tests/fixtures/expression/family_expression.tsv"
    assert command[command.index("--expression_metadata") + 1] == "tests/fixtures/expression/sample_metadata.tsv"


def test_build_nextflow_command_can_pass_yaml_species_order_for_copy_number_plots():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/example.config.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_smoke/standard",
        gene_family_species_order="tests/fixtures/species_order/species_tree_order.tsv",
    )

    assert "--gene_family_species_order" in command
    assert command[command.index("--gene_family_species_order") + 1] == (
        "tests/fixtures/species_order/species_tree_order.tsv"
    )


def test_build_nextflow_command_supports_manifest_config():
    command = build_nextflow_command(
        nextflow_bin="nextflow",
        config="configs/manifest.example.yaml",
        groups="configs/species_groups.yaml",
        mock_evidence_dir="tests/fixtures/mock_evidence",
        outdir="results/nextflow_standard_manifest_smoke/standard",
    )

    assert command[command.index("--config") + 1] == "configs/manifest.example.yaml"
    assert command[command.index("--outdir") + 1] == "results/nextflow_standard_manifest_smoke/standard"


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

    params = load_standard_params(config)

    assert params["use_hmmer"] == "false"
    assert params["use_diamond"] == "true"
    assert params["final_rule"] == "union"
    assert params["mock_external_tools"] == "false"
    assert params["gene_family_species_order"] == ""


def test_load_standard_params_reads_yaml_species_order_for_copy_number_plots(tmp_path):
    config = tmp_path / "species_order.yaml"
    config.write_text(
        "\n".join(
            [
                "identification:",
                "  final_rule: intersection",
                "plotting:",
                "  gene_family_species_order: tests/fixtures/species_order/species_tree_order.tsv",
                "dev:",
                "  mock_external_tools: true",
            ]
        ),
        encoding="utf-8",
    )

    params = load_standard_params(config)

    assert params["gene_family_species_order"] == str(Path("tests/fixtures/species_order/species_tree_order.tsv").resolve())


def test_load_standard_params_resolves_yaml_species_order_relative_to_repo_root():
    params = load_standard_params(Path("configs/example.config.yaml"))

    assert params["gene_family_species_order"] == str(
        Path("tests/fixtures/species_order/species_tree_order.tsv").resolve()
    )


def test_load_standard_params_reads_yaml_publication_module_inputs(tmp_path):
    config = tmp_path / "publication_modules.yaml"
    config.write_text(
        "\n".join(
            [
                "identification:",
                "  final_rule: intersection",
                "modules:",
                "  feature_summary: true",
                "  synteny: true",
                "  promoter: true",
                "  promoter_cis: true",
                "  ppi: true",
                "  expression: true",
                "promoter:",
                "  cis_elements: tests/fixtures/promoter_cis/plantcare.tsv",
                "ppi:",
                "  edges: tests/fixtures/ppi/ppi_edges.tsv",
                "  nodes: tests/fixtures/ppi/ppi_nodes.tsv",
                "expression:",
                "  matrix: tests/fixtures/expression/family_expression.tsv",
                "  metadata: tests/fixtures/expression/sample_metadata.tsv",
                "plotting:",
                "  syntenic_pairs: tests/fixtures/mcscanx/syntenic_pairs.tsv",
                "dev:",
                "  mock_external_tools: true",
            ]
        ),
        encoding="utf-8",
    )

    params = load_standard_params(config)

    assert params["run_feature_summary"] == "true"
    assert params["run_mcscanx_circlize"] == "true"
    assert params["syntenic_pairs"] == str(Path("tests/fixtures/mcscanx/syntenic_pairs.tsv").resolve())
    assert params["run_promoter"] == "true"
    assert params["run_promoter_cis"] == "true"
    assert params["promoter_cis_elements"] == str(Path("tests/fixtures/promoter_cis/plantcare.tsv").resolve())
    assert params["run_ppi"] == "true"
    assert params["ppi_edges"] == str(Path("tests/fixtures/ppi/ppi_edges.tsv").resolve())
    assert params["ppi_nodes"] == str(Path("tests/fixtures/ppi/ppi_nodes.tsv").resolve())
    assert params["expression_matrix"] == str(Path("tests/fixtures/expression/family_expression.tsv").resolve())
    assert params["expression_metadata"] == str(Path("tests/fixtures/expression/sample_metadata.tsv").resolve())


def test_expected_published_outputs_cover_standard_user_results(tmp_path):
    standard_outdir = tmp_path / "standard"

    assert expected_published_outputs(standard_outdir) == [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/run_config_snapshot.tsv",
        standard_outdir / "tables/family_candidates.tsv",
        standard_outdir / "tables/family_counts.tsv",
        standard_outdir / "tables/gene_family_copy_number.tsv",
        standard_outdir / "tables/gene_family_copy_number_summary.tsv",
        standard_outdir / "tables/gene_family_species_order.tsv",
        standard_outdir / "tables/gene_family_copy_number_expansion.tsv",
        standard_outdir / "tables/gene_family_pangenome_summary.tsv",
        standard_outdir / "tables/gene_family_protein_properties.tsv",
        standard_outdir / "tables/alignment_manifest.tsv",
        standard_outdir / "tables/phylogeny_manifest.tsv",
        standard_outdir / "alignment/GDSL.mafft.aln.faa",
        standard_outdir / "phylogeny/GDSL.fasttree.treefile",
        standard_outdir / "tables/motif_summary.tsv",
        standard_outdir / "tables/gene_structure_summary.tsv",
        standard_outdir / "tables/chromosome_locations.tsv",
        standard_outdir / "tables/wgd_handoff_manifest.tsv",
        standard_outdir / "sequences/family_members.faa",
        standard_outdir / "report/report_index.tsv",
        standard_outdir / "report/plot_manifest.tsv",
        standard_outdir / "report/final_report.md",
        standard_outdir / "plots/family_counts.pdf",
        standard_outdir / "plots/family_counts.png",
        standard_outdir / "plots/gene_family_info_summary.pdf",
        standard_outdir / "plots/gene_family_info_summary.png",
    ]


def test_expected_published_outputs_can_include_standard_visualization_modules(tmp_path):
    standard_outdir = tmp_path / "standard"

    outputs = expected_published_outputs(
        standard_outdir,
        feature_summary=True,
        mcscanx_circlize=True,
    )

    assert standard_outdir / "tables/feature_summary.tsv" in outputs
    assert standard_outdir / "plots/feature_summary.pdf" in outputs
    assert standard_outdir / "plots/feature_summary.png" in outputs
    assert standard_outdir / "tables/circlize_chromosomes.tsv" in outputs
    assert standard_outdir / "tables/circlize_links.tsv" in outputs
    assert standard_outdir / "tables/circlize_skipped_links.tsv" in outputs
    assert standard_outdir / "plots/mcscanx_circlize.pdf" in outputs
    assert standard_outdir / "plots/mcscanx_circlize.png" in outputs


def test_expected_published_outputs_can_include_promoter_extraction_outputs(tmp_path):
    standard_outdir = tmp_path / "standard"

    outputs = expected_published_outputs(
        standard_outdir,
        promoter=True,
    )

    assert standard_outdir / "tables/promoters.bed" in outputs
    assert standard_outdir / "sequences/promoters.fa" in outputs


def test_expected_published_outputs_can_include_full_publication_visualization_modules(tmp_path):
    standard_outdir = tmp_path / "standard"

    outputs = expected_published_outputs(
        standard_outdir,
        feature_summary=True,
        mcscanx_circlize=True,
        promoter_cis=True,
        ppi=True,
        expression=True,
    )

    assert standard_outdir / "tables/promoter_cis_elements.tsv" in outputs
    assert standard_outdir / "tables/promoter_cis_gene_matrix.tsv" in outputs
    assert standard_outdir / "tables/promoter_cis_gene_element_matrix.tsv" in outputs
    assert standard_outdir / "tables/promoter_cis_category_summary.tsv" in outputs
    assert standard_outdir / "tables/promoter_cis_element_annotations.tsv" in outputs
    assert standard_outdir / "plots/promoter_cis_elements.pdf" in outputs
    assert standard_outdir / "plots/promoter_cis_elements.png" in outputs
    assert standard_outdir / "tables/ppi_edges.tsv" in outputs
    assert standard_outdir / "tables/ppi_nodes.tsv" in outputs
    assert standard_outdir / "tables/ppi_hubs.tsv" in outputs
    assert standard_outdir / "tables/ppi_input_evidence.tsv" in outputs
    assert standard_outdir / "tables/ppi_network_qc.tsv" in outputs
    assert standard_outdir / "tables/ppi_ggnetview_status.tsv" in outputs
    assert standard_outdir / "plots/ppi_ggnetview.pdf" in outputs
    assert standard_outdir / "plots/ppi_ggnetview.png" in outputs
    assert standard_outdir / "tables/family_expression.tsv" in outputs
    assert standard_outdir / "tables/expression_sample_metadata.tsv" in outputs
    assert standard_outdir / "tables/expression_group_matrix.tsv" in outputs
    assert standard_outdir / "tables/expression_gene_summary.tsv" in outputs
    assert standard_outdir / "plots/expression_heatmap.pdf" in outputs
    assert standard_outdir / "plots/expression_heatmap.png" in outputs


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
