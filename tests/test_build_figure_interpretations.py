import shlex
from pathlib import Path

from bin.genefam.build_figure_interpretations import build_figure_interpretations


def test_build_figure_interpretations_creates_reading_notes_for_each_plot():
    plots = [
        {"plot_key": "family_counts", "path": "results/standard_smoke/plots/family_counts.pdf", "description": "Counts"},
        {"plot_key": "tree_features", "path": "results/demo/plots/tree_features.pdf", "description": "Tree features"},
        {"plot_key": "mcscanx_circlize", "path": "results/demo/plots/mcscanx_circlize.pdf", "description": "MCScanX links"},
        {"plot_key": "ks_wgd_layers", "path": "results/demo/plots/ks_wgd_layers.pdf", "description": "Ks layers"},
        {"plot_key": "gene_family_pangenome_summary", "path": "results/demo/plots/gene_family_info_summary.pdf", "description": "Pangenome"},
        {"plot_key": "ppi_ggnetview", "path": "results/demo/plots/ppi_ggnetview.pdf", "description": "PPI"},
    ]

    rows = build_figure_interpretations(plots)
    by_key = {row["figure_key"]: row for row in rows}

    assert by_key["family_counts"]["title"] == "Family member count overview"
    assert "member totals" in by_key["family_counts"]["what_figure_shows"]
    assert "expansion or contraction" in by_key["family_counts"]["biological_interpretation"]
    assert "smoke/demo" in by_key["family_counts"]["qc_warnings"]
    assert by_key["tree_features"]["title"] == "Tree, motif, gene-structure, and domain composite"
    assert "feature tracks" in by_key["tree_features"]["what_figure_shows"]
    assert "tables/tree_feature_matrix.tsv" in by_key["tree_features"]["qc_tables"]
    assert "plot_tree_features.R" in by_key["tree_features"]["method_and_software"]
    assert by_key["mcscanx_circlize"]["title"] == "MCScanX syntenic relationship overview"
    assert "syntenic block" in by_key["mcscanx_circlize"]["what_figure_shows"]
    assert "tables/circlize_link_density.tsv" in by_key["mcscanx_circlize"]["qc_tables"]
    assert "plot_mcscanx_circlize.R" in by_key["mcscanx_circlize"]["method_and_software"]
    assert "WGD" in by_key["ks_wgd_layers"]["qc_tables"]
    assert "classify_wgd_layers.py" in by_key["ks_wgd_layers"]["method_and_software"]
    assert by_key["gene_family_pangenome_summary"]["title"] == "Gene family pangenome and copy-number balance"
    assert "core" in by_key["gene_family_pangenome_summary"]["key_observations"]
    assert "dispensable" in by_key["gene_family_pangenome_summary"]["biological_interpretation"]
    assert "tables/gene_family_pangenome_summary.tsv" in by_key["gene_family_pangenome_summary"]["qc_tables"]
    assert "plot_gene_family_info.R" in by_key["gene_family_pangenome_summary"]["method_and_software"]
    assert "run_gene_family_info_smoke.py" in by_key["gene_family_pangenome_summary"]["reproducibility"]
    assert by_key["ppi_ggnetview"]["title"] == "PPI network generated with ggNetView"
    assert "hub" in by_key["ppi_ggnetview"]["key_observations"]
    assert "tables/ppi_network_qc.tsv" in by_key["ppi_ggnetview"]["qc_tables"]
    assert "ggNetView" in by_key["ppi_ggnetview"]["method_and_software"]
    assert "template-guided close reading" in by_key["ppi_ggnetview"]["result_reading_status"]


def test_figure_interpretation_reproducibility_scripts_exist():
    plots = [
        {"plot_key": "family_counts", "path": "plots/family_counts.pdf"},
        {"plot_key": "tree_features", "path": "plots/tree_features.pdf"},
        {"plot_key": "mcscanx_circlize", "path": "plots/mcscanx_circlize.pdf"},
        {"plot_key": "ks_wgd_layers", "path": "plots/ks_wgd_layers.pdf"},
        {"plot_key": "expression_heatmap", "path": "plots/expression_heatmap.pdf"},
        {"plot_key": "promoter_cis_elements", "path": "plots/promoter_cis_elements.pdf"},
        {"plot_key": "gene_family_pangenome_summary", "path": "plots/gene_family_info_summary.pdf"},
        {"plot_key": "feature_summary", "path": "plots/feature_summary.pdf"},
        {"plot_key": "ppi_ggnetview", "path": "plots/ppi_ggnetview.pdf"},
    ]

    for row in build_figure_interpretations(plots):
        command = shlex.split(row["reproducibility"])
        script = command[1]
        assert Path(script).exists(), row


def test_wgd_kaks_plots_have_figure_specific_close_reading_templates():
    plots = [
        {"plot_key": "ks_distribution", "path": "plots/ks_distribution.pdf"},
        {"plot_key": "duplicate_type_kaks", "path": "plots/duplicate_type_kaks.pdf"},
        {"plot_key": "pangenome_kaks", "path": "plots/pangenome_kaks.pdf"},
    ]

    rows = build_figure_interpretations(plots)
    by_key = {row["figure_key"]: row for row in rows}

    assert by_key["ks_distribution"]["title"] == "Ks distribution and named WGD-layer support"
    assert "gamma/beta/alpha/theta" in by_key["ks_distribution"]["biological_interpretation"]
    assert "run_kaks_wgd_plot_smoke.py" in by_key["ks_distribution"]["reproducibility"]

    assert by_key["duplicate_type_kaks"]["title"] == "Duplicate-type grouped Ka/Ks selection overview"
    assert "WGD, tandem, proximal, transposed, or dispersed" in by_key["duplicate_type_kaks"]["what_figure_shows"]
    assert "tables/duplicate_type_kaks_summary.tsv" in by_key["duplicate_type_kaks"]["qc_tables"]
    assert "run_duplicate_type_kaks_smoke.py" in by_key["duplicate_type_kaks"]["reproducibility"]

    assert by_key["pangenome_kaks"]["title"] == "Pangenome-class grouped Ka/Ks selection overview"
    assert "core, soft-core, dispensable, and private" in by_key["pangenome_kaks"]["what_figure_shows"]
    assert "tables/pangenome_kaks_summary.tsv" in by_key["pangenome_kaks"]["qc_tables"]
    assert "run_pangenome_kaks_smoke.py" in by_key["pangenome_kaks"]["reproducibility"]

    titles = {row["title"] for row in rows}
    assert len(titles) == 3


def test_standard_family_count_and_gene_family_info_have_distinct_close_readings():
    plots = [
        {"plot_key": "family_counts", "path": "plots/family_counts.pdf"},
        {"plot_key": "gene_family_info_summary", "path": "plots/gene_family_info_summary.pdf"},
    ]

    rows = build_figure_interpretations(plots)
    by_key = {row["figure_key"]: row for row in rows}

    assert by_key["family_counts"]["title"] == "Family member count overview"
    assert "member totals" in by_key["family_counts"]["what_figure_shows"]
    assert "tables/gene_family_copy_number_summary.tsv" in by_key["family_counts"]["qc_tables"]

    assert by_key["gene_family_info_summary"]["title"] == "Gene family information and dosage-balance summary"
    assert "copy-number balance" in by_key["gene_family_info_summary"]["what_figure_shows"]
    assert "protein-property" in by_key["gene_family_info_summary"]["key_observations"]
    assert "tables/gene_family_species_order.tsv" in by_key["gene_family_info_summary"]["qc_tables"]
    assert "plot_gene_family_info.R" in by_key["gene_family_info_summary"]["method_and_software"]

    assert by_key["family_counts"]["title"] != by_key["gene_family_info_summary"]["title"]
