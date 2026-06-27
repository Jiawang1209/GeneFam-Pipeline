import subprocess
import sys

from bin.genefam.build_wgd_report_index import build_report_index, read_tsv


def test_build_wgd_report_index_points_to_published_outputs():
    rows = build_report_index("results/nextflow_wgd_smoke/wgd")
    by_key = {row["key"]: row for row in rows}

    assert by_key["wgd_run_config_snapshot"] == {
        "key": "wgd_run_config_snapshot",
        "path": "results/nextflow_wgd_smoke/wgd/tables/wgd_run_config_snapshot.tsv",
        "status": "available",
        "description": "WGD run parameters including Ks bins and named event mappings",
    }
    assert by_key["wgd_event_evidence"] == {
        "key": "wgd_event_evidence",
        "path": "results/nextflow_wgd_smoke/wgd/tables/wgd_event_evidence.tsv",
        "status": "available",
        "description": "Named WGD event evidence including gamma beta alpha theta labels",
    }
    assert by_key["kaks_wgd_annotations"] == {
        "key": "kaks_wgd_annotations",
        "path": "results/nextflow_wgd_smoke/wgd/tables/kaks_wgd_annotations.tsv",
        "status": "available",
        "description": "WGD event labels and Ks positions used to annotate the Ks distribution plot",
    }
    assert by_key["family_event_retention_summary"]["path"].endswith(
        "tables/family_event_retention_summary.tsv"
    )
    assert by_key["retention_enrichment"]["path"].endswith("tables/retention_enrichment.tsv")
    assert by_key["ks_distribution_pdf"] == {
        "key": "ks_distribution_pdf",
        "path": "results/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf",
        "status": "available",
        "description": "Ks distribution PDF plot for WGD-layer interpretation",
    }
    assert by_key["ks_distribution_png"]["path"].endswith("plots/ks_distribution.png")
    assert by_key["duplicate_type_kaks_pdf"] == {
        "key": "duplicate_type_kaks_pdf",
        "path": "results/nextflow_wgd_smoke/wgd/plots/duplicate_type_kaks.pdf",
        "status": "available",
        "description": "Duplicate-type grouped Ks and Ka/Ks PDF plot",
    }
    assert by_key["duplicate_type_kaks_summary"]["path"].endswith("tables/duplicate_type_kaks_summary.tsv")
    assert by_key["pangenome_kaks_pdf"] == {
        "key": "pangenome_kaks_pdf",
        "path": "results/nextflow_wgd_smoke/wgd/plots/pangenome_kaks.pdf",
        "status": "available",
        "description": "Pangenome-class grouped Ks and Ka/Ks PDF plot",
    }
    assert by_key["pangenome_kaks_summary"]["path"].endswith("tables/pangenome_kaks_summary.tsv")
    assert by_key["plot_manifest"] == {
        "key": "plot_manifest",
        "path": "results/nextflow_wgd_smoke/wgd/report/plot_manifest.tsv",
        "status": "available",
        "description": "Generated WGD plot inventory",
    }
    assert by_key["software_versions"]["path"] == "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv"
    assert by_key["figure_interpretations"]["path"] == (
        "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.tsv"
    )
    assert by_key["figure_interpretations_md"]["path"] == (
        "results/nextflow_wgd_smoke/wgd/report/figure_interpretations.md"
    )
    assert by_key["final_report"] == {
        "key": "final_report",
        "path": "results/nextflow_wgd_smoke/wgd/report/final_report.md",
        "status": "available",
        "description": "Final WGD Markdown report with methods, software versions, QC, and per-figure result interpretation",
    }
    assert by_key["figure_traceability_matrix"] == {
        "key": "figure_traceability_matrix",
        "path": "results/nextflow_wgd_smoke/wgd/report/final_report.md#figure-traceability-matrix",
        "status": "available",
        "description": "Final WGD report Figure Traceability Matrix linking every WGD plot to close-reading, QC, software, and reproducibility evidence",
    }


def test_build_wgd_report_index_cli_writes_tsv(tmp_path):
    out = tmp_path / "report_index.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_wgd_report_index.py",
            "--published-outdir",
            "results/demo_wgd",
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    rows = {row["key"]: row for row in read_tsv(out)}
    assert rows["wgd_run_config_snapshot"]["path"] == "results/demo_wgd/tables/wgd_run_config_snapshot.tsv"
    assert rows["wgd_layers"]["path"] == "results/demo_wgd/tables/wgd_layers.tsv"
    assert rows["kaks_wgd_annotations"]["path"] == "results/demo_wgd/tables/kaks_wgd_annotations.tsv"
    assert rows["wgd_event_evidence"]["status"] == "available"
    assert rows["ks_distribution_pdf"]["path"] == "results/demo_wgd/plots/ks_distribution.pdf"
    assert rows["duplicate_type_kaks_png"]["path"] == "results/demo_wgd/plots/duplicate_type_kaks.png"
    assert rows["pangenome_kaks_png"]["path"] == "results/demo_wgd/plots/pangenome_kaks.png"
    assert rows["plot_manifest"]["path"] == "results/demo_wgd/report/plot_manifest.tsv"
    assert rows["software_versions"]["path"] == "results/demo_wgd/report/software_versions.tsv"
    assert rows["figure_interpretations"]["path"] == "results/demo_wgd/report/figure_interpretations.tsv"
    assert rows["figure_interpretations_md"]["path"] == "results/demo_wgd/report/figure_interpretations.md"
    assert rows["final_report"]["path"] == "results/demo_wgd/report/final_report.md"
    assert rows["figure_traceability_matrix"]["path"] == (
        "results/demo_wgd/report/final_report.md#figure-traceability-matrix"
    )
