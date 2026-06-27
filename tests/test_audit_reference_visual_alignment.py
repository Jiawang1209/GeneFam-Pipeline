import subprocess
import sys
from pathlib import Path


def _write_tsv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def _standard_plot_rows() -> list[str]:
    return [
        "family_counts\tplots/family_counts.pdf\tFamily member counts by species",
        "gene_family_info_summary\tplots/gene_family_info_summary.pdf\tGene family copy-number and protein-property summary",
        "gene_family_pangenome_summary\tplots/gene_family_info_summary.pdf\tGene family pangenome presence and copy-number balance",
        "tree_features\tplots/tree_features.pdf\tTree, motif, gene-structure, and domain composite plot",
        "feature_summary\tplots/feature_summary.pdf\tIntegrated feature summary",
        "mcscanx_circlize\tplots/mcscanx_circlize.pdf\tMCScanX synteny and chromosome-scale circlize plot",
        "promoter_cis_elements\tplots/promoter_cis_elements.pdf\tPromoter cis-element category matrix",
        "ppi_ggnetview\tplots/ppi_ggnetview.pdf\tPPI network generated with ggNetView",
        "expression_heatmap\tplots/expression_heatmap.pdf\tFamily member expression heatmap",
    ]


def _wgd_plot_rows() -> list[str]:
    return [
        "ks_distribution\tplots/ks_distribution.pdf\tKs distribution for duplicated pairs and WGD layer interpretation",
        "duplicate_type_kaks\tplots/duplicate_type_kaks.pdf\tDuplicate-type grouped Ks and Ka/Ks selection overview",
        "pangenome_kaks\tplots/pangenome_kaks.pdf\tPangenome-class grouped Ks and Ka/Ks selection overview",
    ]


def _interpretation_rows(keys: list[str]) -> list[str]:
    return [
        f"{key}\t{key} title\tinput\tshows\tobservations\tinterpretation\tqc\ttables\tsoftware\treproduce\tready\tplots/{key}.pdf"
        for key in keys
    ]


def test_reference_visual_alignment_audit_cli_passes_for_complete_standard_and_wgd_figures(tmp_path):
    standard_manifest = tmp_path / "standard_plot_manifest.tsv"
    wgd_manifest = tmp_path / "wgd_plot_manifest.tsv"
    standard_interpretations = tmp_path / "standard_figure_interpretations.tsv"
    wgd_interpretations = tmp_path / "wgd_figure_interpretations.tsv"
    out_tsv = tmp_path / "reference_visual_alignment.tsv"
    out_md = tmp_path / "reference_visual_alignment.md"

    _write_tsv(standard_manifest, "plot_key\tpath\tdescription", _standard_plot_rows())
    _write_tsv(wgd_manifest, "plot_key\tpath\tdescription", _wgd_plot_rows())
    _write_tsv(
        standard_interpretations,
        "figure_key\ttitle\tinput_data\twhat_figure_shows\tkey_observations\tbiological_interpretation\tqc_warnings\tqc_tables\tmethod_and_software\treproducibility\tresult_reading_status\toutput_path",
        _interpretation_rows([row.split("\t", 1)[0] for row in _standard_plot_rows()]),
    )
    _write_tsv(
        wgd_interpretations,
        "figure_key\ttitle\tinput_data\twhat_figure_shows\tkey_observations\tbiological_interpretation\tqc_warnings\tqc_tables\tmethod_and_software\treproducibility\tresult_reading_status\toutput_path",
        _interpretation_rows([row.split("\t", 1)[0] for row in _wgd_plot_rows()]),
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_reference_visual_alignment.py",
            "--standard-plot-manifest",
            str(standard_manifest),
            "--standard-figure-interpretations",
            str(standard_interpretations),
            "--wgd-plot-manifest",
            str(wgd_manifest),
            "--wgd-figure-interpretations",
            str(wgd_interpretations),
            "--out-tsv",
            str(out_tsv),
            "--out-md",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    audit_text = out_tsv.read_text(encoding="utf-8")
    assert "standard_reference_visual_modules\tpassed" in audit_text
    assert "wgd_reference_visual_modules\tpassed" in audit_text
    assert "reference_visual_interpretations\tpassed" in audit_text
    assert "tree_features, motif, gene structure, domain" in audit_text
    assert "MCScanX/synteny/circlize" in audit_text
    assert "Ka/Ks/WGD gamma beta alpha theta" in audit_text
    assert "Complete: true" in out_md.read_text(encoding="utf-8")


def test_reference_visual_alignment_audit_cli_fails_when_required_plot_is_missing(tmp_path):
    standard_manifest = tmp_path / "standard_plot_manifest.tsv"
    wgd_manifest = tmp_path / "wgd_plot_manifest.tsv"
    standard_interpretations = tmp_path / "standard_figure_interpretations.tsv"
    wgd_interpretations = tmp_path / "wgd_figure_interpretations.tsv"
    out_tsv = tmp_path / "reference_visual_alignment.tsv"
    out_md = tmp_path / "reference_visual_alignment.md"

    standard_rows = [row for row in _standard_plot_rows() if not row.startswith("ppi_ggnetview\t")]
    _write_tsv(standard_manifest, "plot_key\tpath\tdescription", standard_rows)
    _write_tsv(wgd_manifest, "plot_key\tpath\tdescription", _wgd_plot_rows())
    _write_tsv(
        standard_interpretations,
        "figure_key\ttitle\tinput_data\twhat_figure_shows\tkey_observations\tbiological_interpretation\tqc_warnings\tqc_tables\tmethod_and_software\treproducibility\tresult_reading_status\toutput_path",
        _interpretation_rows([row.split("\t", 1)[0] for row in standard_rows]),
    )
    _write_tsv(
        wgd_interpretations,
        "figure_key\ttitle\tinput_data\twhat_figure_shows\tkey_observations\tbiological_interpretation\tqc_warnings\tqc_tables\tmethod_and_software\treproducibility\tresult_reading_status\toutput_path",
        _interpretation_rows([row.split("\t", 1)[0] for row in _wgd_plot_rows()]),
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_reference_visual_alignment.py",
            "--standard-plot-manifest",
            str(standard_manifest),
            "--standard-figure-interpretations",
            str(standard_interpretations),
            "--wgd-plot-manifest",
            str(wgd_manifest),
            "--wgd-figure-interpretations",
            str(wgd_interpretations),
            "--out-tsv",
            str(out_tsv),
            "--out-md",
            str(out_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    audit_text = out_tsv.read_text(encoding="utf-8")
    assert "standard_reference_visual_modules\tfailed" in audit_text
    assert "ppi_ggnetview:missing_plot" in audit_text
    assert "Complete: false" in out_md.read_text(encoding="utf-8")
