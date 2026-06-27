import subprocess
import sys
from pathlib import Path

from bin.genefam.audit_figure_gallery import audit_figure_gallery, summarize_audit


def _write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(["\t".join(header), *["\t".join(row) for row in rows], ""]),
        encoding="utf-8",
    )


def test_figure_gallery_audit_requires_files_and_traceability_anchor(tmp_path):
    gallery = tmp_path / "figure_gallery.tsv"
    report = tmp_path / "report"
    plots = tmp_path / "plots"
    report.mkdir()
    plots.mkdir()
    (report / "figure_interpretations.md").write_text("# Figure Interpretations\n", encoding="utf-8")
    (report / "software_versions.tsv").write_text("component\tversion\nR\t4.4.0\n", encoding="utf-8")
    (report / "final_report.md").write_text("# Final Report\n\n## Figure Inventory\n", encoding="utf-8")

    _write_tsv(
        gallery,
        [
            "branch",
            "plot_key",
            "plot_path",
            "plot_description",
            "figure_interpretations",
            "software_versions",
            "final_report",
            "traceability_matrix",
        ],
        [
            [
                "standard",
                "tree_features",
                str(plots / "missing_tree_features.pdf"),
                "Tree, motif, gene-structure, and domain composite plot",
                str(report / "figure_interpretations.md"),
                str(report / "software_versions.tsv"),
                str(report / "final_report.md"),
                str(report / "final_report.md") + "#figure-traceability-matrix",
            ],
        ],
    )

    rows = audit_figure_gallery(gallery)
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_gallery_required_columns"]["status"] == "passed"
    assert by_check["figure_gallery_linked_files_exist"]["status"] == "failed"
    assert "tree_features:plot_path:missing_file" in by_check["figure_gallery_linked_files_exist"]["note"]
    assert "tree_features:traceability_matrix:missing_anchor:#figure-traceability-matrix" in (
        by_check["figure_gallery_linked_files_exist"]["note"]
    )
    assert by_check["figure_gallery_manifest_coverage"]["status"] == "passed"
    assert summarize_audit(rows) == {"passed": 2, "failed": 1, "complete": False}


def test_figure_gallery_audit_cli_writes_outputs_when_gallery_is_complete(tmp_path):
    gallery = tmp_path / "figure_gallery.tsv"
    report = tmp_path / "report"
    plots = tmp_path / "plots"
    report.mkdir()
    plots.mkdir()
    (plots / "tree_features.pdf").write_bytes(b"%PDF tree")
    (report / "figure_interpretations.md").write_text("# Figure Interpretations\n", encoding="utf-8")
    (report / "software_versions.tsv").write_text("component\tversion\nR\t4.4.0\n", encoding="utf-8")
    (report / "final_report.md").write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")
    _write_tsv(
        gallery,
        [
            "branch",
            "plot_key",
            "plot_path",
            "plot_description",
            "figure_interpretations",
            "software_versions",
            "final_report",
            "traceability_matrix",
        ],
        [
            [
                "standard",
                "tree_features",
                str(plots / "tree_features.pdf"),
                "Tree, motif, gene-structure, and domain composite plot",
                str(report / "figure_interpretations.md"),
                str(report / "software_versions.tsv"),
                str(report / "final_report.md"),
                str(report / "final_report.md") + "#figure-traceability-matrix",
            ],
        ],
    )
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_figure_gallery.py",
            "--figure-gallery",
            str(gallery),
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
    assert "figure_gallery_linked_files_exist\tpassed" in out_tsv.read_text(encoding="utf-8")
    assert "Complete: true" in out_md.read_text(encoding="utf-8")


def test_figure_gallery_audit_requires_manifest_plot_coverage(tmp_path):
    gallery = tmp_path / "figure_gallery.tsv"
    branch = tmp_path / "standard"
    report = branch / "report"
    plots = branch / "plots"
    report.mkdir(parents=True)
    plots.mkdir()
    (plots / "family_counts.pdf").write_bytes(b"%PDF counts")
    (plots / "gene_family_info_summary.pdf").write_bytes(b"%PDF pangenome")
    (report / "figure_interpretations.md").write_text("# Figure Interpretations\n", encoding="utf-8")
    (report / "software_versions.tsv").write_text("component\tversion\nR\t4.4.0\n", encoding="utf-8")
    (report / "final_report.md").write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")
    _write_tsv(
        report / "plot_manifest.tsv",
        ["plot_key", "path", "description"],
        [
            ["family_counts", "plots/family_counts.pdf", "Family member counts by species"],
            [
                "gene_family_pangenome_summary",
                "plots/gene_family_info_summary.pdf",
                "Gene family pangenome presence and copy-number balance",
            ],
        ],
    )
    _write_tsv(
        gallery,
        [
            "branch",
            "plot_key",
            "plot_path",
            "plot_description",
            "figure_interpretations",
            "software_versions",
            "final_report",
            "traceability_matrix",
        ],
        [
            [
                "standard",
                "family_counts",
                str(plots / "family_counts.pdf"),
                "Family member counts by species",
                str(report / "figure_interpretations.md"),
                str(report / "software_versions.tsv"),
                str(report / "final_report.md"),
                str(report / "final_report.md") + "#figure-traceability-matrix",
            ],
        ],
    )

    rows = audit_figure_gallery(gallery, plot_manifests={"standard": report / "plot_manifest.tsv"})
    by_check = {row["check"]: row for row in rows}

    assert by_check["figure_gallery_manifest_coverage"]["status"] == "failed"
    assert "standard:gene_family_pangenome_summary:missing_gallery_row" in (
        by_check["figure_gallery_manifest_coverage"]["note"]
    )
    assert summarize_audit(rows) == {"passed": 2, "failed": 1, "complete": False}
