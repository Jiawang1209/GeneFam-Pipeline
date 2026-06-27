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
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")
    (tmp_path / "plots/ppi_ggnetview.pdf").write_bytes(b"%PDF ppi")

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
                "figure-specific close reading",
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
                "figure-specific close reading",
                "plots/ppi_ggnetview.pdf",
            ],
        ],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "command", "2.1.11", "detected", "fasttree -help"],
            ["MAFFT", "command", "7.520", "detected", "mafft --version"],
            ["ggNetView", "R_package", "0.1.0", "detected", "R packageVersion"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "# GeneFam-Pipeline Final Report",
                "## Methods Summary",
                "Family members are identified with HMMER and DIAMOND evidence. MCScanX synteny and Ka/Ks evidence support gamma, beta, alpha, and theta WGD interpretations.",
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| FastTree | command | 2.1.11 | detected | fasttree -help |",
                "| MAFFT | command | 7.520 | detected | mafft --version |",
                "| ggNetView | R_package | 0.1.0 | detected | R packageVersion |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Traceability Matrix",
                "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |",
                "| --- | --- | --- | --- | --- | --- |",
                "| tree_features | plots/tree_features.pdf | figure-specific close reading | tables/tree_feature_matrix.tsv | FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R | python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke |",
                "| ppi_ggnetview | plots/ppi_ggnetview.pdf | figure-specific close reading | tables/ppi_network_qc.tsv | ggNetView; plot_ppi_ggnetview.R; /usr/local/bin/R | python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke |",
                "## Figure Result Interpretations",
                "### tree_features: Tree, motif, gene-structure, and domain composite",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share motif/domain architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
                "### ppi_ggnetview: PPI network generated with ggNetView",
                "- Input data: PPI edges and nodes",
                "- What the figure shows: network hubs and modules",
                "- Key observations: hub genes are visible",
                "- Biological interpretation: hub genes may identify interaction centers",
                "- QC warnings / limitations: review interaction evidence",
                "- QC tables: tables/ppi_network_qc.tsv",
                "- Method/software: ggNetView; plot_ppi_ggnetview.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/ppi_ggnetview.pdf`",
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

    assert summary == {"passed": 14, "failed": 0, "complete": True}
    assert {row["check"] for row in rows} == {
        "plot_files_exist",
        "plot_file_format_valid",
        "figure_interpretation_coverage",
        "figure_interpretation_scope",
        "figure_interpretation_detail",
        "figure_output_paths_match_manifest",
        "software_versions_present",
        "software_detected_versions_parseable",
        "software_version_detection_warnings_visible",
        "figure_method_software_versions",
        "final_report_methods_summary",
        "final_report_embeds_publication_sections",
        "final_report_figure_traceability",
        "final_report_placeholder_text",
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


def test_publication_report_audit_requires_figure_traceability_matrix(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["tree_features", "plots/tree_features.pdf", "Tree features"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "command", "2.1.11", "detected", "fasttree -help"],
            ["MAFFT", "command", "7.520", "detected", "mafft --version"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "4.0.3", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| FastTree | command | 2.1.11 | detected | fasttree -help |",
                "| MAFFT | command | 7.520 | detected | mafft --version |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "| ggplot2 | R_package | 4.0.3 | detected | packageVersion(\"ggplot2\") |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["final_report_figure_traceability"]["status"] == "failed"
    assert "missing_section:Figure Traceability Matrix" in by_check["final_report_figure_traceability"]["note"]


def test_publication_report_audit_requires_methods_summary(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/ks_distribution.pdf").write_bytes(b"%PDF ks")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["ks_distribution", "plots/ks_distribution.pdf", "Ks distribution"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "ks_distribution",
            "Ks and WGD event table",
            "Ks peaks and WGD layers",
            "gamma beta alpha theta layers are visible",
            "Ks-supported WGD labels summarize duplication history",
            "review sparse bins",
            "tables/wgd_event_summary.tsv",
            "MCScanX; Ka/Ks; plot_wgd_results.R; /usr/local/bin/R",
            "python bin/genefam/run_wgd_smoke.py --outdir results/wgd_smoke",
            "figure-specific close reading",
            "plots/ks_distribution.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["MCScanX", "command", "1.0", "detected", "MCScanX"],
            ["KaKs_Calculator", "command", "3.0", "detected", "KaKs_Calculator -h"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "4.0.3", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "# GeneFam-Pipeline Final Report",
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| MCScanX | command | 1.0 | detected | MCScanX |",
                "| KaKs_Calculator | command | 3.0 | detected | KaKs_Calculator -h |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "| ggplot2 | R_package | 4.0.3 | detected | packageVersion(\"ggplot2\") |",
                "## Figure Traceability Matrix",
                "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |",
                "| --- | --- | --- | --- | --- | --- |",
                "| ks_distribution | plots/ks_distribution.pdf | figure-specific close reading | tables/wgd_event_summary.tsv | MCScanX; Ka/Ks; plot_wgd_results.R; /usr/local/bin/R | python bin/genefam/run_wgd_smoke.py --outdir results/wgd_smoke |",
                "## Figure Result Interpretations",
                "### ks_distribution: Ks distribution",
                "- Input data: Ks and WGD event table",
                "- What the figure shows: Ks peaks and WGD layers",
                "- Key observations: gamma beta alpha theta layers are visible",
                "- Biological interpretation: Ks-supported WGD labels summarize duplication history",
                "- QC warnings / limitations: review sparse bins",
                "- QC tables: tables/wgd_event_summary.tsv",
                "- Method/software: MCScanX; Ka/Ks; plot_wgd_results.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_wgd_smoke.py --outdir results/wgd_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/ks_distribution.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["final_report_methods_summary"]["status"] == "failed"
    assert "missing_section:Methods Summary" in by_check["final_report_methods_summary"]["note"]


def test_publication_report_audit_flags_missing_or_empty_plot_files(tmp_path):
    plot_manifest = tmp_path / "report/plot_manifest.tsv"
    figure_interpretations = tmp_path / "report/figure_interpretations.tsv"
    software_versions = tmp_path / "report/software_versions.tsv"
    final_report = tmp_path / "report/final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/family_counts.pdf").write_bytes(b"%PDF counts")
    (tmp_path / "plots/empty_plot.pdf").write_bytes(b"")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [
            ["family_counts", "plots/family_counts.pdf", "Counts"],
            ["empty_plot", "plots/empty_plot.pdf", "Empty plot"],
            ["missing_plot", "plots/missing_plot.pdf", "Missing plot"],
        ],
    )
    _write_tsv(
        figure_interpretations,
        ["figure_key", "qc_tables", "method_and_software", "reproducibility", "result_reading_status", "output_path"],
        [
            ["family_counts", "tables/family_counts.tsv", "plot_family_counts.R", "run", "read", "plots/family_counts.pdf"],
            ["empty_plot", "tables/empty.tsv", "plot_empty.R", "run", "read", "plots/empty_plot.pdf"],
            ["missing_plot", "tables/missing.tsv", "plot_missing.R", "run", "read", "plots/missing_plot.pdf"],
        ],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "4.0.3", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "## Figure Result Interpretations",
                "### family_counts: Counts",
                "- QC tables: tables/family_counts.tsv",
                "- Method/software: plot_family_counts.R",
                "- Reproducibility: run",
                "### empty_plot: Empty plot",
                "- QC tables: tables/empty.tsv",
                "- Method/software: plot_empty.R",
                "- Reproducibility: run",
                "### missing_plot: Missing plot",
                "- QC tables: tables/missing.tsv",
                "- Method/software: plot_missing.R",
                "- Reproducibility: run",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["plot_files_exist"]["status"] == "failed"
    assert "empty_plot:empty" in by_check["plot_files_exist"]["note"]
    assert "missing_plot:missing" in by_check["plot_files_exist"]["note"]


def test_publication_report_audit_cli_writes_markdown_and_tsv(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/family_counts.pdf").write_bytes(b"%PDF counts")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["family_counts", "plots/family_counts.pdf", "Counts"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "family_counts",
            "Family member count table",
            "Per-species member totals",
            "Inspect expansion or contraction",
            "High-copy species may indicate expansion",
            "Smoke/demo data caveat",
            "tables/family_counts.tsv",
            "plot_family_counts.R; /usr/local/bin/R",
            "python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
            "figure-specific close reading",
            "plots/family_counts.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "4.0.3", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "## Methods Summary",
                "Family members are identified with HMMER and DIAMOND evidence. MCScanX synteny and Ka/Ks evidence support gamma, beta, alpha, and theta WGD interpretations.",
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "| ggplot2 | R_package | 4.0.3 | detected | packageVersion(\"ggplot2\") |",
                "## Figure Traceability Matrix",
                "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |",
                "| --- | --- | --- | --- | --- | --- |",
                "| family_counts | plots/family_counts.pdf | figure-specific close reading | tables/family_counts.tsv | plot_family_counts.R; /usr/local/bin/R | python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke |",
                "## Figure Result Interpretations",
                "### family_counts: Family copy number",
                "- Input data: Family member count table",
                "- What the figure shows: Per-species member totals",
                "- Key observations: Inspect expansion or contraction",
                "- Biological interpretation: High-copy species may indicate expansion",
                "- QC warnings / limitations: Smoke/demo data caveat",
                "- QC tables: tables/family_counts.tsv",
                "- Method/software: plot_family_counts.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/family_counts.pdf`",
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
    assert "plot_files_exist\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "figure_interpretation_coverage\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "final_report_figure_traceability\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "Complete: true" in out_md.read_text(encoding="utf-8")


def test_publication_report_audit_requires_software_versions_embedded_in_final_report(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["tree_features", "plots/tree_features.pdf", "Tree features"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "command", "2.1.11", "detected", "fasttree -help"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "4.0.3", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["software_versions_present"]["status"] == "passed"
    assert by_check["final_report_embeds_publication_sections"]["status"] == "failed"
    assert "software_version:FastTree:2.1.11" in by_check["final_report_embeds_publication_sections"]["note"]
    assert "software_version:R:4.4.0" in by_check["final_report_embeds_publication_sections"]["note"]
    assert "software_version:ggplot2:4.0.3" in by_check["final_report_embeds_publication_sections"]["note"]


def test_publication_report_audit_requires_non_detected_versions_visible_in_final_report(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/mcscanx_circlize.pdf").write_bytes(b"%PDF mcscanx")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["mcscanx_circlize", "plots/mcscanx_circlize.pdf", "MCScanX circlize"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "mcscanx_circlize",
            "MCScanX syntenic pairs",
            "chromosome-scale links",
            "linked blocks are visible",
            "retained synteny supports duplication context",
            "MCScanX version could not be detected from local binary",
            "tables/circlize_links.tsv",
            "MCScanX; circlize; /usr/local/bin/R",
            "python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke",
            "figure-specific close reading",
            "plots/mcscanx_circlize.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["MCScanX", "command", "version_not_detected", "version_not_detected", "MCScanX"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
            ["circlize", "R_package", "0.4.17", "detected", "packageVersion(\"circlize\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "| circlize | R_package | 0.4.17 | detected | packageVersion(\"circlize\") |",
                "## Figure Traceability Matrix",
                "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |",
                "| --- | --- | --- | --- | --- | --- |",
                "| mcscanx_circlize | plots/mcscanx_circlize.pdf | figure-specific close reading | tables/circlize_links.tsv | MCScanX; circlize; /usr/local/bin/R | python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke |",
                "## Figure Result Interpretations",
                "### mcscanx_circlize: MCScanX circlize",
                "- Input data: MCScanX syntenic pairs",
                "- What the figure shows: chromosome-scale links",
                "- Key observations: linked blocks are visible",
                "- Biological interpretation: retained synteny supports duplication context",
                "- QC warnings / limitations: MCScanX version could not be detected from local binary",
                "- QC tables: tables/circlize_links.tsv",
                "- Method/software: MCScanX; circlize; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/mcscanx_circlize.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["software_version_detection_warnings_visible"]["status"] == "failed"
    assert "software_version_warning:MCScanX:version_not_detected:version_not_detected" in by_check[
        "software_version_detection_warnings_visible"
    ]["note"]


def test_publication_report_audit_rejects_detected_versions_without_numeric_version(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/family_counts.pdf").write_bytes(b"%PDF family")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["family_counts", "plots/family_counts.pdf", "Family counts"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "family_counts",
            "family count table",
            "member counts",
            "copy-number shifts are visible",
            "copy-number shifts suggest expansion candidates",
            "review skipped rows",
            "tables/family_counts.tsv",
            "Nextflow; plot_family_counts.R; /usr/local/bin/R",
            "python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
            "figure-specific close reading",
            "plots/family_counts.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["Nextflow", "command", "N E X T F L O W", "detected", "nextflow -version"],
            ["R", "command", "4.5.1", "detected", "/usr/local/bin/R --version"],
            ["ggplot2", "R_package", "3.5.2", "detected", "packageVersion(\"ggplot2\")"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "## Methods Summary",
                "HMMER DIAMOND MCScanX Ka/Ks gamma beta alpha theta.",
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| Nextflow | command | N E X T F L O W | detected | nextflow -version |",
                "| R | command | 4.5.1 | detected | /usr/local/bin/R --version |",
                "| ggplot2 | R_package | 3.5.2 | detected | packageVersion(\"ggplot2\") |",
                "## Figure Traceability Matrix",
                "| figure_key | plot_path | interpretation_status | qc_tables | method_and_software | reproducibility |",
                "| --- | --- | --- | --- | --- | --- |",
                "| family_counts | plots/family_counts.pdf | figure-specific close reading | tables/family_counts.tsv | Nextflow; plot_family_counts.R; /usr/local/bin/R | python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke |",
                "## Figure Result Interpretations",
                "### family_counts: Family counts",
                "- Input data: family count table",
                "- What the figure shows: member counts",
                "- Key observations: copy-number shifts are visible",
                "- Biological interpretation: copy-number shifts suggest expansion candidates",
                "- QC warnings / limitations: review skipped rows",
                "- QC tables: tables/family_counts.tsv",
                "- Method/software: Nextflow; plot_family_counts.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/family_counts.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["software_detected_versions_parseable"]["status"] == "failed"
    assert "detected_version_without_numeric_value:Nextflow:N E X T F L O W" in by_check[
        "software_detected_versions_parseable"
    ]["note"]


def test_publication_report_audit_requires_close_reading_text_embedded_in_final_report(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/expression_heatmap.pdf").write_bytes(b"%PDF expression")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["expression_heatmap", "plots/expression_heatmap.pdf", "Expression heatmap"]])
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
        [[
            "expression_heatmap",
            "Expression heatmap",
            "Family expression matrix and sample metadata",
            "Expression variation among family members across samples",
            "Co-expression clusters separate cold-response samples",
            "Clustered expression supports candidate regulatory divergence",
            "Review sample metadata and normalization before interpretation",
            "tables/expression_gene_summary.tsv",
            "plot_expression_heatmap.R; /usr/local/bin/R",
            "python bin/genefam/run_expression_heatmap_smoke.py --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke",
            "figure-specific close reading",
            "plots/expression_heatmap.pdf",
        ]],
    )
    _write_tsv(software_versions, ["component", "kind", "version", "status", "source"], [["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"]])
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | runtime | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### expression_heatmap: Expression heatmap",
                "- QC tables: tables/expression_gene_summary.tsv",
                "- Method/software: plot_expression_heatmap.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_expression_heatmap_smoke.py --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/expression_heatmap.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_detail"]["status"] == "passed"
    assert by_check["final_report_embeds_publication_sections"]["status"] == "failed"
    assert "expression_heatmap:what_figure_shows" in by_check["final_report_embeds_publication_sections"]["note"]
    assert "expression_heatmap:key_observations" in by_check["final_report_embeds_publication_sections"]["note"]
    assert "expression_heatmap:biological_interpretation" in by_check["final_report_embeds_publication_sections"]["note"]
    assert "expression_heatmap:qc_warnings" in by_check["final_report_embeds_publication_sections"]["note"]


def test_publication_report_audit_flags_template_guided_reading_status(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["tree_features", "plots/tree_features.pdf", "Tree features"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "template-guided close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(software_versions, ["component", "kind", "version", "status", "source"], [["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"]])
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | runtime | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Output path: `plots/tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_detail"]["status"] == "failed"
    assert "tree_features:result_reading_status:not_figure_specific" in by_check["figure_interpretation_detail"]["note"]


def test_publication_report_audit_flags_placeholder_interpretation_text(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["tree_features", "plots/tree_features.pdf", "Tree features"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "TODO: describe clade-level feature pattern",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "FastTree; ggplot2; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "command", "2.1.11", "detected", "fasttree -help"],
            ["ggplot2", "R_package", "3.5.1", "detected", "R packageVersion"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| FastTree | command | 2.1.11 | detected | fasttree -help |",
                "| ggplot2 | R_package | 3.5.1 | detected | R packageVersion |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: TODO: describe clade-level feature pattern",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; ggplot2; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_detail"]["status"] == "failed"
    assert "tree_features:key_observations:placeholder_text" in by_check["figure_interpretation_detail"]["note"]


def test_publication_report_audit_flags_placeholder_text_in_final_report(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["tree_features", "plots/tree_features.pdf", "Tree features"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "FastTree; ggplot2; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "command", "2.1.11", "detected", "fasttree -help"],
            ["ggplot2", "R_package", "3.5.1", "detected", "R packageVersion"],
            ["R", "command", "4.4.0", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| FastTree | command | 2.1.11 | detected | fasttree -help |",
                "| ggplot2 | R_package | 3.5.1 | detected | R packageVersion |",
                "| R | command | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; ggplot2; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
                "TODO: replace this draft conclusion before publication.",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_detail"]["status"] == "passed"
    assert by_check["final_report_placeholder_text"]["status"] == "failed"
    assert "final_report:todo" in by_check["final_report_placeholder_text"]["note"]


def test_publication_report_audit_requires_reading_status_embedded_in_final_report(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    reading_status = "figure-specific close reading; validate tree topology and feature-table completeness"
    _write_tsv(plot_manifest, ["plot_key", "path", "description"], [["tree_features", "plots/tree_features.pdf", "Tree features"]])
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            reading_status,
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(software_versions, ["component", "kind", "version", "status", "source"], [["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"]])
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | runtime | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Output path: `plots/tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_detail"]["status"] == "passed"
    assert by_check["final_report_embeds_publication_sections"]["status"] == "failed"
    assert "tree_features:result_reading_status" in by_check["final_report_embeds_publication_sections"]["note"]


def test_publication_report_audit_requires_versions_for_figure_method_software(tmp_path):
    plot_manifest = tmp_path / "plot_manifest.tsv"
    figure_interpretations = tmp_path / "figure_interpretations.tsv"
    software_versions = tmp_path / "software_versions.tsv"
    final_report = tmp_path / "final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")
    (tmp_path / "plots/ppi_ggnetview.pdf").write_bytes(b"%PDF ppi")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [
            ["tree_features", "plots/tree_features.pdf", "Tree features"],
            ["ppi_ggnetview", "plots/ppi_ggnetview.pdf", "PPI network"],
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
                "clades share feature architecture",
                "conserved clade features support structural conservation",
                "review missing feature rows",
                "tables/tree_feature_matrix.tsv",
                "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R; GeneFamilyFlow",
                "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "figure-specific close reading",
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
                "build_ppi_tables.py; plot_ppi_ggnetview.R; ggNetView; /usr/local/bin/R; GeneFamilyFlow",
                "python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
                "figure-specific close reading",
                "plots/ppi_ggnetview.pdf",
            ],
        ],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [["R", "runtime", "4.4.0", "detected", "/usr/local/bin/R --version"]],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| component | kind | version | status | source |",
                "| --- | --- | --- | --- | --- |",
                "| R | runtime | 4.4.0 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree, motif, gene-structure, and domain composite",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R; GeneFamilyFlow",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
                "### ppi_ggnetview: PPI network generated with ggNetView",
                "- Input data: PPI edges and nodes",
                "- What the figure shows: network hubs and modules",
                "- Key observations: hub genes are visible",
                "- Biological interpretation: hub genes may identify interaction centers",
                "- QC warnings / limitations: review interaction evidence",
                "- QC tables: tables/ppi_network_qc.tsv",
                "- Method/software: build_ppi_tables.py; plot_ppi_ggnetview.R; ggNetView; /usr/local/bin/R; GeneFamilyFlow",
                "- Reproducibility: python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/ppi_ggnetview.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_method_software_versions"]["status"] == "failed"
    assert "tree_features:FastTree" in by_check["figure_method_software_versions"]["note"]
    assert "tree_features:MAFFT" in by_check["figure_method_software_versions"]["note"]
    assert "ppi_ggnetview:ggNetView" in by_check["figure_method_software_versions"]["note"]


def test_publication_report_audit_rejects_nonempty_invalid_plot_format(tmp_path):
    plot_manifest = tmp_path / "report/plot_manifest.tsv"
    figure_interpretations = tmp_path / "report/figure_interpretations.tsv"
    software_versions = tmp_path / "report/software_versions.tsv"
    final_report = tmp_path / "report/final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"not a real PDF but non-empty")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["tree_features", "plots/tree_features.pdf", "Tree features"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "tool", "2.1.11", "detected", "FastTree -help"],
            ["MAFFT", "tool", "7.526", "detected", "mafft --version"],
            ["R", "runtime", "4.5.1", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| FastTree | tool | 2.1.11 | detected | FastTree -help |",
                "| MAFFT | tool | 7.526 | detected | mafft --version |",
                "| R | runtime | 4.5.1 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["plot_files_exist"]["status"] == "passed"
    assert by_check["plot_file_format_valid"]["status"] == "failed"
    assert "tree_features:invalid_pdf:plots/tree_features.pdf" in by_check["plot_file_format_valid"]["note"]


def test_publication_report_audit_requires_interpretation_output_path_to_match_manifest(tmp_path):
    plot_manifest = tmp_path / "report/plot_manifest.tsv"
    figure_interpretations = tmp_path / "report/figure_interpretations.tsv"
    software_versions = tmp_path / "report/software_versions.tsv"
    final_report = tmp_path / "report/final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["tree_features", "plots/tree_features.pdf", "Tree features"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "tree_features",
            "tree and feature tables",
            "tree-ordered feature tracks",
            "clades share feature architecture",
            "conserved clade features support structural conservation",
            "review missing feature rows",
            "tables/tree_feature_matrix.tsv",
            "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
            "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
            "figure-specific close reading",
            "plots/other_tree_features.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "tool", "2.1.11", "detected", "FastTree -help"],
            ["MAFFT", "tool", "7.526", "detected", "mafft --version"],
            ["R", "runtime", "4.5.1", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| FastTree | tool | 2.1.11 | detected | FastTree -help |",
                "| MAFFT | tool | 7.526 | detected | mafft --version |",
                "| R | runtime | 4.5.1 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/other_tree_features.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["plot_files_exist"]["status"] == "passed"
    assert by_check["figure_output_paths_match_manifest"]["status"] == "failed"
    assert "tree_features:manifest=plots/tree_features.pdf:interpretation=plots/other_tree_features.pdf" in (
        by_check["figure_output_paths_match_manifest"]["note"]
    )


def test_publication_report_audit_rejects_unregistered_figure_interpretations(tmp_path):
    plot_manifest = tmp_path / "report/plot_manifest.tsv"
    figure_interpretations = tmp_path / "report/figure_interpretations.tsv"
    software_versions = tmp_path / "report/software_versions.tsv"
    final_report = tmp_path / "report/final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/tree_features.pdf").write_bytes(b"%PDF tree")
    (tmp_path / "plots/orphan_plot.pdf").write_bytes(b"%PDF orphan")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["tree_features", "plots/tree_features.pdf", "Tree features"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
                "tree and feature tables",
                "tree-ordered feature tracks",
                "clades share feature architecture",
                "conserved clade features support structural conservation",
                "review missing feature rows",
                "tables/tree_feature_matrix.tsv",
                "FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "figure-specific close reading",
                "plots/tree_features.pdf",
            ],
            [
                "orphan_plot",
                "unregistered input",
                "unregistered figure",
                "not in plot manifest",
                "should not appear in delivery report",
                "review plot manifest",
                "tables/orphan.tsv",
                "plot_orphan.R; /usr/local/bin/R",
                "python bin/genefam/run_orphan_smoke.py",
                "figure-specific close reading",
                "plots/orphan_plot.pdf",
            ],
        ],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["FastTree", "tool", "2.1.11", "detected", "FastTree -help"],
            ["MAFFT", "tool", "7.526", "detected", "mafft --version"],
            ["R", "runtime", "4.5.1", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| FastTree | tool | 2.1.11 | detected | FastTree -help |",
                "| MAFFT | tool | 7.526 | detected | mafft --version |",
                "| R | runtime | 4.5.1 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### tree_features: Tree features",
                "- Input data: tree and feature tables",
                "- What the figure shows: tree-ordered feature tracks",
                "- Key observations: clades share feature architecture",
                "- Biological interpretation: conserved clade features support structural conservation",
                "- QC warnings / limitations: review missing feature rows",
                "- QC tables: tables/tree_feature_matrix.tsv",
                "- Method/software: FastTree; MAFFT; plot_tree_features.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/tree_features.pdf`",
                "### orphan_plot: Unregistered figure",
                "- Input data: unregistered input",
                "- What the figure shows: unregistered figure",
                "- Key observations: not in plot manifest",
                "- Biological interpretation: should not appear in delivery report",
                "- QC warnings / limitations: review plot manifest",
                "- QC tables: tables/orphan.tsv",
                "- Method/software: plot_orphan.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_orphan_smoke.py",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/orphan_plot.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_interpretation_coverage"]["status"] == "passed"
    assert by_check["figure_interpretation_scope"]["status"] == "failed"
    assert "orphan_plot" in by_check["figure_interpretation_scope"]["note"]


def test_publication_report_audit_requires_command_and_r_package_versions(tmp_path):
    plot_manifest = tmp_path / "report/plot_manifest.tsv"
    figure_interpretations = tmp_path / "report/figure_interpretations.tsv"
    software_versions = tmp_path / "report/software_versions.tsv"
    final_report = tmp_path / "report/final_report.md"
    (tmp_path / "plots").mkdir()
    (tmp_path / "plots/family_counts.pdf").write_bytes(b"%PDF counts")

    _write_tsv(
        plot_manifest,
        ["plot_key", "path", "description"],
        [["family_counts", "plots/family_counts.pdf", "Family counts"]],
    )
    _write_tsv(
        figure_interpretations,
        [
            "figure_key",
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
        [[
            "family_counts",
            "family count table",
            "member counts by species",
            "copy numbers differ among species",
            "copy-number shifts may indicate expansion or contraction",
            "review selected species and missing candidates",
            "tables/family_counts.tsv",
            "plot_family_counts.R; /usr/local/bin/R",
            "python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
            "figure-specific close reading",
            "plots/family_counts.pdf",
        ]],
    )
    _write_tsv(
        software_versions,
        ["component", "kind", "version", "status", "source"],
        [
            ["Nextflow", "command", "26.04.4", "detected", "nextflow -version"],
            ["R", "command", "4.5.1", "detected", "/usr/local/bin/R --version"],
        ],
    )
    final_report.write_text(
        "\n".join(
            [
                "### Software Versions",
                "| Nextflow | command | 26.04.4 | detected | nextflow -version |",
                "| R | command | 4.5.1 | detected | /usr/local/bin/R --version |",
                "## Figure Result Interpretations",
                "### family_counts: Family counts",
                "- Input data: family count table",
                "- What the figure shows: member counts by species",
                "- Key observations: copy numbers differ among species",
                "- Biological interpretation: copy-number shifts may indicate expansion or contraction",
                "- QC warnings / limitations: review selected species and missing candidates",
                "- QC tables: tables/family_counts.tsv",
                "- Method/software: plot_family_counts.R; /usr/local/bin/R",
                "- Reproducibility: python bin/genefam/run_standard_smoke.py --outdir results/standard_smoke",
                "- Result reading status: figure-specific close reading",
                "- Output path: `plots/family_counts.pdf`",
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
    by_check = {row["check"]: row for row in rows}

    assert by_check["software_versions_present"]["status"] == "failed"
    assert "R_package" in by_check["software_versions_present"]["note"]
