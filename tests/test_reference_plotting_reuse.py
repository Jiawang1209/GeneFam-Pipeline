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

    assert "| PPI network | `Reference/Long_Weixiong_20240323_1_GDSL/R/11.ppi.R`" in text
    assert "| Tree + motif + gene structure + domain |" in text
    assert "| promoter cis-element |" in text
    assert "| MCScanX duplicate type + Ka/Ks | `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R` | `bin/genefam/build_duplicate_type_kaks.py`; `scripts/plot_duplicate_type_kaks.R`; WGD branch `plots/duplicate_type_kaks.pdf/png` | done |" in text
    assert "| RNA-seq expression heatmap | `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R` | `build_expression_summary.py`; `scripts/plot_expression_heatmap.R`; `PLOT_EXPRESSION_HEATMAP`; `tables/expression_sample_metadata.tsv`; `tables/expression_group_matrix.tsv`; `tables/expression_gene_summary.tsv`; `plots/expression_heatmap.pdf/png` | done |" in text
