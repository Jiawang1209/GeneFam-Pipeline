from pathlib import Path


def test_reference_plotting_reuse_tracks_paper_figure_alignment_status():
    text = Path("docs/reference_plotting_reuse.md").read_text(encoding="utf-8")

    required = [
        "Reference Figure Alignment Matrix",
        "5.GeneFamily_Info.R",
        "6.tree.R",
        "8.collinearity_kaks.R",
        "9.mcscanx_KaKs.R",
        "10.promoter.R",
        "11.ppi.R",
        "12.rnaseq.R",
        "ggNetView",
        "Figure result interpretation",
        "Software version table",
        "done / partial / missing",
    ]
    for phrase in required:
        assert phrase in text

    assert "| PPI network | `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R` | `build_ppi_tables.py`; `scripts/plot_ppi_ggnetview.R`; `PLOT_PPI_GGNETVIEW`; `tables/ppi_input_evidence.tsv`; `tables/ppi_network_qc.tsv`; `plots/ppi_ggnetview.pdf/png` | done |" in text
    assert "| Gene family information summary | `Reference/Long_Weixiong_20240323_1_GDSL/R/5.GeneFamily_Info.R` | `bin/genefam/summarize_family.py`; `build_gene_family_info.py`; `scripts/plot_gene_family_info.R`; `PLOT_GENE_FAMILY_INFO`; `tables/gene_family_species_order.tsv`; `tables/gene_family_copy_number_expansion.tsv`; `tables/gene_family_pangenome_summary.tsv`; `plots/gene_family_info_summary.pdf/png` | done |" in text
    assert "combined Ks-by-pangenome-class comparison plots" in text
    assert "| Tree + motif + gene structure + domain | `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R` | `build_tree_feature_matrix.py`; `scripts/plot_tree_features.R`; `PLOT_TREE_FEATURES`; `tables/tree_feature_matrix.tsv`; `plots/tree_features.pdf/png` | done |" in text
    assert "| promoter cis-element | `Reference/Long_Weixiong_20240323_1_GDSL/R/10.promoter.R` | `extract_promoters.py`; `build_promoter_cis_elements.py`; `scripts/plot_promoter_cis_elements.R`; `PLOT_PROMOTER_CIS_ELEMENTS`; `tables/promoter_cis_gene_element_matrix.tsv`; `tables/promoter_cis_element_annotations.tsv`; `plots/promoter_cis_elements.pdf/png` | done |" in text
    assert "| MCScanX/circlize synteny | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.Circos_*.R` | `build_circlize_inputs.py`; `scripts/plot_mcscanx_circlize.R`; `PLOT_MCSCANX_CIRCLIZE`; `tables/circlize_link_density.tsv`; `tables/circlize_duplicate_type_tracks.tsv`; `plots/mcscanx_circlize.pdf/png` | done |" in text
    assert "| JCVI/collinearity Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R` | `bin/genefam/build_kaks_plot_annotations.py`; `scripts/plot_kaks.R`; WGD branch `tables/kaks_wgd_annotations.tsv`; `plots/ks_distribution.pdf/png` | done |" in text
    assert "| MCScanX duplicate type + Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R` | `bin/genefam/build_duplicate_type_kaks.py`; `scripts/plot_duplicate_type_kaks.R`; WGD branch `plots/duplicate_type_kaks.pdf/png` | done |" in text
    assert "| RNA-seq expression heatmap | `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R` | `build_expression_summary.py`; `scripts/plot_expression_heatmap.R`; `PLOT_EXPRESSION_HEATMAP`; `tables/expression_sample_metadata.tsv`; `tables/expression_group_matrix.tsv`; `tables/expression_gene_summary.tsv`; `plots/expression_heatmap.pdf/png` | done |" in text
