import subprocess
import sys
from pathlib import Path

from bin.genefam.audit_publication_report import audit_publication_report, summarize_audit


def _write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(["\t".join(header), *["\t".join(row) for row in rows], ""]),
        encoding="utf-8",
    )


def test_publication_report_audit_requires_figure_reading_versions_qc_and_reproducibility(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [
            ["tree_features", "plots/tree_features.pdf", "Tree and feature architecture"],
            ["ppi_ggnetview", "plots/ppi_ggnetview.pdf", "PPI network generated with ggNetView"],
        ],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
            "title",
            "input_data",
            "what_figure_shows",
            "key_observations",
            "biological_interpretation",
            "qc_warnings",
            "qc_tables",
            "method_and_software",
            "reproducibility",
            "result_reading_status",
            "output_path",
        ],
        [
            [
                "tree_features",
                "Tree, motif, gene-structure, and domain composite",
                "tree and feature tables",
                "tree-ordered feature tracks",
                "clades share motif/domain architecture",
                "conserved clade features support structural conservation",
                "review missing feature rows",
                "tables/tree_feature_matrix.tsv",
                "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "template-guided close reading",
                "plots/tree_features.pdf",
            ],
            [
                "ppi_ggnetview",
                "PPI network generated with ggNetView",
                "PPI edges and nodes",
                "network hubs and modules",
                "hub genes are visible",
                "hub genes may identify interaction centers",
                "review interaction evidence",
                "tables/ppi_network_qc.tsv",
                "ggNetView; plot_ppi_ggnetview.R; /usr/local/bin/R",
                "python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
                "template-guided close reading",
                "plots/ppi_ggnetview.pdf",
            ],
        ],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "tool", "2.1.11", "detected", "fasttree -help"],
            ["MAFFT", "tool", "7.520", "detected", "mafft --version"],
            ["ggNetView", "R_package", "0.1.0", "detected", "R packageVersion"],
            ["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "# GeneFam-Pipeline Final Report",
                "### Software Versions",
                "## Figure Result Interpretations",
                "### tree_features: Tree, motif, gene-structure, and domain composite",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "### ppi_ggnetview: PPI network generated with ggNetView",
                "- QC tables: tables/ppi_network_qc.tsv",
                "- Method/software: ggNetView; plot_ppi_ggnetview.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
            ]
        ),
        encoding="utf-8",
    )

    rows = audit_publication_report(
        plot_manifest=plot_manifest,
        figure_interpretations=figure_interpretations,
        software_versions=software_versions,
        final_report=final_report,
    )
    summary = summarize_audit(rows)

    assert summary == {"passed": 4, "failed": 0, "complete": True}
    assert {row["check"] for row in rows} == {
        "figure_interpretation_coverage",
        "figure_interpretation_detail",
        "software_versions_present",
        "final_report_embeds_publication_sections",
    }


def test_publication_report_audit_flags_missing_figure_interpretation(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["tree_features", "plots/tree_features.pdf", "Tree features"]],
    )
    _write_tsv(figure_interpretations, ["figure_key", "qc_tables", "method_and_software", "reproducibility"], [])
    _write_tsv(software_versions, ["component", "kind", "version", "status", "source"], [])
    final_report.write_text("# GeneFam-Pipeline Final Report\n", encoding="utf-8")

    rows = audit_publication_report(
        plot_manifest=plot_manifest,
        figure_interpretations=figure_interpretations,
        software_versions=software_versions,
        final_report=final_report,
    )
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_coverage"]["status"] == "failed"
    assert "tree_features" in by_check["figure_interpretation_coverage"]["note"]


def test_publication_report_audit_cli_writes_markdown_and_tsv(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["family_counts", "plots/family_counts.pdf", "Counts"]])
    _write_tsv(
        figure_interpretations,
        ["figure_key", "qc_tables", "method_and_software", "reproducibility", "result_reading_status", "output_path"],
        [[
            "family_counts",
            "tables/family_counts.tsv",
            "plot_family_counts.R; /usr/local/bin/R",
            "python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
            "template-guided close reading",
            "plots/family_counts.pdf",
        ]],
    )
    _write_tsv(software_versions, ["component", "kind", "version", "status", "source"], [["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"]])
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "## Figure Result Interpretations",
                "### family_counts: Family copy number",
                "- QC tables: tables/family_counts.tsv",
                "- Method/software: plot_family_counts.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
            ]
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_publication_report.py",
            "--plot-manifest",
            str(plot_manifest),
            "--figure-interpretations",
            str(figure_interpretations),
            "--software-versions",
            str(software_versions),
            "--final-report",
            str(final_report),
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
    assert "figure_interpretation_coverage\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "Complete: true" in out_md.read_text(encoding="utf-8")
