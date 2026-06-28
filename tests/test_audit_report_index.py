import subprocess
import sys

from bin.genefam.audit_report_index import audit_report_index, summarize_audit


def _write_tsv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(["\t".join(header)] + ["\t".join(row) for row in rows]) + "\n",
        encoding="utf-8",
    )


def test_report_index_audit_requires_core_standard_report_artifacts(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    for name in [
        "plot_manifest.tsv",
        "software_versions.tsv",
        "figure_interpretations.tsv",
        "figure_interpretations.md",
    ]:
        (report_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (report_dir / name).write_text("ok\n", encoding="utf-8")
    (report_dir / "final_report.md").write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")

    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(report_dir / "final_report.md"), "available", "Final report"],
        ],
    )

    rows = audit_report_index(report_index, profile="standard")
    by_check = {row["check"]: row for row in rows}

    assert by_check["report_index_required_artifacts"]["status"] == "failed"
    assert "figure_traceability_matrix:missing_row" in by_check["report_index_required_artifacts"]["note"]
    assert "reference_mvp_package_audit_tsv:missing_row" in by_check["report_index_required_artifacts"]["note"]
    assert "reference_mvp_package_audit_md:missing_row" in by_check["report_index_required_artifacts"]["note"]
    assert by_check["report_index_available_paths_exist"]["status"] == "passed"
    assert summarize_audit(rows) == {"passed": 3, "failed": 1, "complete": False}


def test_report_index_audit_passes_when_core_wgd_report_artifacts_are_indexed(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    for name in [
        "plot_manifest.tsv",
        "software_versions.tsv",
        "figure_interpretations.tsv",
        "figure_interpretations.md",
        "reference_mvp_package_audit.tsv",
        "reference_mvp_package_audit.md",
    ]:
        (report_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (report_dir / name).write_text("ok\n", encoding="utf-8")
    (report_dir / "final_report.md").write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")

    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated WGD plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(report_dir / "final_report.md"), "available", "Final report"],
            [
                "reference_mvp_package_audit_tsv",
                str(report_dir / "reference_mvp_package_audit.tsv"),
                "available",
                "Reference MVP audit TSV",
            ],
            [
                "reference_mvp_package_audit_md",
                str(report_dir / "reference_mvp_package_audit.md"),
                "available",
                "Reference MVP audit Markdown",
            ],
            [
                "figure_traceability_matrix",
                str(report_dir / "final_report.md") + "#figure-traceability-matrix",
                "available",
                "Figure traceability matrix",
            ],
        ],
    )

    rows = audit_report_index(report_index, profile="wgd")
    by_check = {row["check"]: row for row in rows}

    assert by_check["report_index_required_artifacts"]["status"] == "passed"
    assert by_check["report_index_artifact_files_exist"]["status"] == "passed"
    assert by_check["report_index_available_paths_exist"]["status"] == "passed"
    assert summarize_audit(rows) == {"passed": 4, "failed": 0, "complete": True}


def test_report_index_audit_checks_all_available_paths_not_only_core_artifacts(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    plots = tmp_path / "plots"
    for name in [
        "plot_manifest.tsv",
        "software_versions.tsv",
        "figure_interpretations.tsv",
        "figure_interpretations.md",
        "reference_mvp_package_audit.tsv",
        "reference_mvp_package_audit.md",
    ]:
        (report_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (report_dir / name).write_text("ok\n", encoding="utf-8")
    (report_dir / "final_report.md").write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")

    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(report_dir / "final_report.md"), "available", "Final report"],
            [
                "reference_mvp_package_audit_tsv",
                str(report_dir / "reference_mvp_package_audit.tsv"),
                "available",
                "Reference MVP audit TSV",
            ],
            [
                "reference_mvp_package_audit_md",
                str(report_dir / "reference_mvp_package_audit.md"),
                "available",
                "Reference MVP audit Markdown",
            ],
            [
                "figure_traceability_matrix",
                str(report_dir / "final_report.md") + "#figure-traceability-matrix",
                "available",
                "Figure traceability matrix",
            ],
            ["tree_features_pdf", str(plots / "missing_tree_features.pdf"), "available", "Tree features plot"],
        ],
    )

    rows = audit_report_index(report_index, profile="standard")
    by_check = {row["check"]: row for row in rows}

    assert by_check["report_index_required_artifacts"]["status"] == "passed"
    assert by_check["report_index_artifact_files_exist"]["status"] == "passed"
    assert by_check["report_index_available_paths_exist"]["status"] == "failed"
    assert "tree_features_pdf:missing_file" in by_check["report_index_available_paths_exist"]["note"]
    assert summarize_audit(rows) == {"passed": 3, "failed": 1, "complete": False}


def test_report_index_audit_requires_traceability_anchor_heading(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    for name in [
        "plot_manifest.tsv",
        "software_versions.tsv",
        "figure_interpretations.tsv",
        "figure_interpretations.md",
    ]:
        (report_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (report_dir / name).write_text("ok\n", encoding="utf-8")
    final_report = report_dir / "final_report.md"
    final_report.write_text("# Final Report\n\n## Figure Inventory\n", encoding="utf-8")

    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(final_report), "available", "Final report"],
            [
                "reference_mvp_package_audit_tsv",
                str(report_dir / "reference_mvp_package_audit.tsv"),
                "available",
                "Reference MVP audit TSV",
            ],
            [
                "reference_mvp_package_audit_md",
                str(report_dir / "reference_mvp_package_audit.md"),
                "available",
                "Reference MVP audit Markdown",
            ],
            [
                "figure_traceability_matrix",
                str(final_report) + "#figure-traceability-matrix",
                "available",
                "Figure traceability matrix",
            ],
        ],
    )

    rows = audit_report_index(report_index, profile="standard")
    by_check = {row["check"]: row for row in rows}

    assert by_check["report_index_artifact_files_exist"]["status"] == "failed"
    assert "figure_traceability_matrix:missing_anchor:#figure-traceability-matrix" in (
        by_check["report_index_artifact_files_exist"]["note"]
    )
    assert summarize_audit(rows) == {"passed": 2, "failed": 2, "complete": False}


def test_report_index_audit_requires_traceability_anchor_on_final_report(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    for name in [
        "plot_manifest.tsv",
        "software_versions.tsv",
        "figure_interpretations.tsv",
        "figure_interpretations.md",
        "reference_mvp_package_audit.tsv",
        "reference_mvp_package_audit.md",
    ]:
        (report_dir / name).parent.mkdir(parents=True, exist_ok=True)
        (report_dir / name).write_text("ok\n", encoding="utf-8")
    final_report = report_dir / "final_report.md"
    traceability_report = report_dir / "traceability.md"
    final_report.write_text("# Final Report\n\n## Figure Traceability Matrix\n", encoding="utf-8")
    traceability_report.write_text("# Traceability\n\n## Figure Traceability Matrix\n", encoding="utf-8")

    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(final_report), "available", "Final report"],
            [
                "reference_mvp_package_audit_tsv",
                str(report_dir / "reference_mvp_package_audit.tsv"),
                "available",
                "Reference MVP audit TSV",
            ],
            [
                "reference_mvp_package_audit_md",
                str(report_dir / "reference_mvp_package_audit.md"),
                "available",
                "Reference MVP audit Markdown",
            ],
            [
                "figure_traceability_matrix",
                str(traceability_report) + "#figure-traceability-matrix",
                "available",
                "Figure traceability matrix",
            ],
        ],
    )

    rows = audit_report_index(report_index, profile="standard")
    by_check = {row["check"]: row for row in rows}

    assert by_check["report_index_traceability_anchor"]["status"] == "failed"
    assert "figure_traceability_matrix:not_final_report_anchor" in by_check[
        "report_index_traceability_anchor"
    ]["note"]
    assert summarize_audit(rows) == {"passed": 3, "failed": 1, "complete": False}


def test_report_index_audit_cli_writes_outputs_and_fails_on_missing_files(tmp_path):
    report_index = tmp_path / "report_index.tsv"
    report_dir = tmp_path / "report"
    report_dir.mkdir()
    _write_tsv(
        report_index,
        ["key", "path", "status", "description"],
        [
            ["plot_manifest", str(report_dir / "plot_manifest.tsv"), "available", "Generated plot inventory"],
            ["software_versions", str(report_dir / "software_versions.tsv"), "available", "Software versions"],
            [
                "figure_interpretations",
                str(report_dir / "figure_interpretations.tsv"),
                "available",
                "Figure interpretations",
            ],
            [
                "figure_interpretations_md",
                str(report_dir / "figure_interpretations.md"),
                "available",
                "Figure interpretations Markdown",
            ],
            ["final_report", str(report_dir / "final_report.md"), "available", "Final report"],
        ],
    )
    out_tsv = tmp_path / "audit.tsv"
    out_md = tmp_path / "audit.md"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/audit_report_index.py",
            "--report-index",
            str(report_index),
            "--profile",
            "standard",
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
    assert "report_index_artifact_files_exist" in out_tsv.read_text(encoding="utf-8")
    assert "missing or empty indexed report artifacts" in out_md.read_text(encoding="utf-8")
