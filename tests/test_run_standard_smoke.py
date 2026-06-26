import subprocess
import sys


def test_run_standard_smoke_writes_standard_branch_outputs(tmp_path):
    outdir = tmp_path / "standard_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    expected = [
        "tables/species_manifest.tsv",
        "tables/run_config_snapshot.tsv",
        "tables/family_candidates.tsv",
        "tables/family_counts.tsv",
        "sequences/family_members.faa",
        "tables/alignment_manifest.tsv",
        "tables/phylogeny_manifest.tsv",
        "tables/motif_summary.tsv",
        "tables/gene_structure_summary.tsv",
        "tables/chromosome_locations.tsv",
        "tables/wgd_handoff_manifest.tsv",
        "report/report_index.tsv",
        "report/final_report.md",
    ]
    for relative_path in expected:
        assert (outdir / relative_path).exists(), relative_path
    assert "standard_final_report" in completed.stdout

    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "run_config_snapshot" in report_index
    assert "run_config_snapshot.tsv\tavailable" in report_index
    assert "chromosome_locations" in report_index
    assert "motif_summary" in report_index
    assert "motif_summary.tsv\tavailable" in report_index
    assert "gene_structure_summary" in report_index
    assert "gene_structure_summary.tsv\tavailable" in report_index
    assert "family_expression" in report_index
    assert "wgd_handoff_manifest" in report_index
    assert "wgd_handoff_manifest.tsv\tavailable" in report_index
    wgd_handoff = (outdir / "tables/wgd_handoff_manifest.tsv").read_text(encoding="utf-8")
    assert wgd_handoff.startswith("item\tpath\tstatus\trequired_for\tdescription\n")
    assert "family_members\t" in wgd_handoff
    assert "family_candidates.tsv\tavailable\tduplication_retention" in wgd_handoff
    assert "duplicate_types\t\tpending_user_preparation\tduplication_retention" in wgd_handoff
    assert "kaks_pairs\t\tpending_user_preparation\twgd_layer_classification" in wgd_handoff
    assert "events_config\tconfigs/wgd_events.brassicaceae.yaml\tconfigured\tnamed_wgd_events" in wgd_handoff
    motif_summary = (outdir / "tables/motif_summary.tsv").read_text(encoding="utf-8")
    assert motif_summary.startswith("family_name\tmotif_id\tmotif_name\twidth\tsites\tevalue\n")
    assert "GDSL_motif_1" in motif_summary
    gene_structure = (outdir / "tables/gene_structure_summary.tsv").read_text(encoding="utf-8")
    assert gene_structure.startswith(
        "species_id\tgene_id\tgene_length\ttranscript_count\texon_count\tcds_count\texon_total_length\tcds_total_length\n"
    )
    assert "Arabidopsis_thaliana\tAT1G01010\t401\t0\t0\t0\t0\t0\n" in gene_structure
    assert "Brassica_rapa\tBraA010001\t701\t0\t0\t0\t0\t0\n" in gene_structure
    run_config = (outdir / "tables/run_config_snapshot.tsv").read_text(encoding="utf-8")
    assert run_config.startswith("key\tvalue\n")
    assert "project.name\tGDSL_demo\n" in run_config
    assert "gene_family.name\tGDSL\n" in run_config
    assert "identification.final_rule\tintersection\n" in run_config
    assert "identification.use_hmmer\tTrue\n" in run_config
    assert "identification.use_diamond\tTrue\n" in run_config
    assert "selected_species\tArabidopsis_thaliana,Brassica_rapa\n" in run_config
    final_report = (outdir / "report/final_report.md").read_text(encoding="utf-8")
    assert "## Run Configuration Snapshot" in final_report
    assert "| runtime.environment | GeneFamilyFlow |" in final_report
    assert "| selected_species | Arabidopsis_thaliana,Brassica_rapa |" in final_report
    assert "| identification.final_rule | intersection |" in final_report


def test_run_standard_smoke_supports_manifest_input_mode(tmp_path):
    outdir = tmp_path / "standard_manifest_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/manifest.example.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    species_manifest = (outdir / "tables/species_manifest.tsv").read_text(encoding="utf-8")
    assert "Arabidopsis_thaliana\ttests/fixtures/species_bank/Arabidopsis_thaliana/Arabidopsis_thaliana.pep.fa" in species_manifest
    assert "Brassica_rapa\ttests/fixtures/species_bank/Brassica_rapa/Brassica_rapa.pep.fa" in species_manifest
    run_config = (outdir / "tables/run_config_snapshot.tsv").read_text(encoding="utf-8")
    assert "input.mode\tmanifest\n" in run_config
    assert "input.root\t\n" in run_config
    final_report = (outdir / "report/final_report.md").read_text(encoding="utf-8")
    assert "| input.mode | manifest |" in final_report


def test_run_standard_smoke_writes_family_expression_when_matrix_is_provided(tmp_path):
    outdir = tmp_path / "standard_smoke"
    expression_matrix = tmp_path / "expression.tsv"
    expression_matrix.write_text(
        "gene_id\tcold_0h\tcold_3h\n"
        "AT1G01010\t1.0\t3.0\n"
        "BraA010001\t2.0\t5.0\n"
        "unrelated\t9.0\t9.0\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--expression-matrix",
            str(expression_matrix),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    family_expression = outdir / "tables/family_expression.tsv"
    assert family_expression.read_text(encoding="utf-8") == (
        "gene_id\tcold_0h\tcold_3h\n"
        "AT1G01010\t1.0\t3.0\n"
        "BraA010001\t2.0\t5.0\n"
    )
    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "family_expression\t" in report_index
    assert "family_expression.tsv\tavailable" in report_index
    assert (outdir / "plots/expression_heatmap.pdf").exists()
    plot_manifest = (outdir / "report/plot_manifest.tsv").read_text(encoding="utf-8")
    assert "expression_heatmap\tplots/expression_heatmap.pdf\tFamily member expression heatmap" in plot_manifest
    final_report = (outdir / "report/final_report.md").read_text(encoding="utf-8")
    assert "| expression_heatmap | plots/expression_heatmap.pdf | Family member expression heatmap |" in final_report


def test_run_standard_smoke_writes_expression_metadata_summary_and_png(tmp_path):
    outdir = tmp_path / "standard_smoke"
    expression_matrix = tmp_path / "expression.tsv"
    expression_metadata = tmp_path / "expression_metadata.tsv"
    expression_matrix.write_text(
        "gene_id\tcold_0h_rep1\tcold_0h_rep2\tcold_6h_rep1\n"
        "AT1G01010\t1.0\t3.0\t7.0\n"
        "BraA010001\t2.0\t4.0\t8.0\n",
        encoding="utf-8",
    )
    expression_metadata.write_text(
        "sample_id\tcondition\ttimepoint\treplicate\tgroup\n"
        "cold_0h_rep1\tcold\t0h\t1\tcold_0h\n"
        "cold_0h_rep2\tcold\t0h\t2\tcold_0h\n"
        "cold_6h_rep1\tcold\t6h\t1\tcold_6h\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_standard_smoke.py",
            "--config",
            "configs/example.config.yaml",
            "--groups",
            "configs/species_groups.yaml",
            "--mock-evidence-dir",
            "tests/fixtures/mock_evidence",
            "--expression-matrix",
            str(expression_matrix),
            "--expression-metadata",
            str(expression_metadata),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "tables/expression_sample_metadata.tsv").exists()
    assert (outdir / "tables/expression_group_matrix.tsv").exists()
    assert (outdir / "tables/expression_gene_summary.tsv").exists()
    assert (outdir / "plots/expression_heatmap.png").exists()
    report_index = (outdir / "report/report_index.tsv").read_text(encoding="utf-8")
    assert "expression_sample_metadata\t" in report_index
    assert "expression_group_matrix\t" in report_index
    assert "expression_gene_summary\t" in report_index
