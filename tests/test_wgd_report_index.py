import subprocess
import sys

from bin.genefam.build_wgd_report_index import build_report_index, read_tsv


def test_build_wgd_report_index_points_to_published_outputs():
    rows = build_report_index("results/nextflow_wgd_smoke/wgd")
    by_key = {row["key"]: row for row in rows}

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
    assert rows["wgd_layers"]["path"] == "results/demo_wgd/tables/wgd_layers.tsv"
    assert rows["wgd_event_evidence"]["status"] == "available"
