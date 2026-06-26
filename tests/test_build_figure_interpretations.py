from bin.genefam.build_figure_interpretations import build_figure_interpretations


def test_build_figure_interpretations_creates_reading_notes_for_each_plot():
    plots = [
        {"plot_key": "family_counts", "path": "results/standard_smoke/plots/family_counts.pdf", "description": "Counts"},
        {"plot_key": "tree_features", "path": "results/demo/plots/tree_features.pdf", "description": "Tree features"},
        {"plot_key": "mcscanx_circlize", "path": "results/demo/plots/mcscanx_circlize.pdf", "description": "MCScanX links"},
        {"plot_key": "gene_family_pangenome_summary", "path": "results/demo/plots/gene_family_info_summary.pdf", "description": "Pangenome"},
        {"plot_key": "ppi_ggnetview", "path": "results/demo/plots/ppi_ggnetview.pdf", "description": "PPI"},
    ]

    rows = build_figure_interpretations(plots)
    by_key = {row["figure_key"]: row for row in rows}

    assert by_key["family_counts"]["title"] == "Family copy number and member count overview"
    assert "expansion or contraction" in by_key["family_counts"]["biological_interpretation"]
    assert "smoke/demo" in by_key["family_counts"]["qc_warnings"]
    assert by_key["tree_features"]["title"] == "Tree, motif, gene-structure, and domain composite"
    assert "feature tracks" in by_key["tree_features"]["what_figure_shows"]
    assert by_key["mcscanx_circlize"]["title"] == "MCScanX syntenic relationship overview"
    assert "syntenic block" in by_key["mcscanx_circlize"]["what_figure_shows"]
    assert by_key["gene_family_pangenome_summary"]["title"] == "Gene family pangenome and copy-number balance"
    assert "core" in by_key["gene_family_pangenome_summary"]["key_observations"]
    assert "dispensable" in by_key["gene_family_pangenome_summary"]["biological_interpretation"]
    assert by_key["ppi_ggnetview"]["title"] == "PPI network generated with ggNetView"
    assert "hub" in by_key["ppi_ggnetview"]["key_observations"]
