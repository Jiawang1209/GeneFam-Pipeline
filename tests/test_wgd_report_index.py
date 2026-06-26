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
    assert rows["wgd_event_evidence"]["status"] == "available"
    assert rows["ks_distribution_pdf"]["path"] == "results/demo_wgd/plots/ks_distribution.pdf"
    assert rows["duplicate_type_kaks_png"]["path"] == "results/demo_wgd/plots/duplicate_type_kaks.png"
