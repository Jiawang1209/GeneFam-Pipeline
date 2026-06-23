import csv
import subprocess
import sys


def read_tsv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_run_wgd_smoke_writes_named_event_outputs(tmp_path):
    outdir = tmp_path / "wgd_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_wgd_smoke.py",
            "--events-config",
            "configs/wgd_events.brassicaceae.yaml",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = read_tsv(outdir / "tables/wgd_event_evidence.tsv")
    assert {row["event_name"] for row in evidence} == {"alpha", "beta", "gamma", "theta"}
    assert all(row["interpretation_status"] == "configured_named_event" for row in evidence)
    assert (outdir / "tables/family_event_retention_summary.tsv").exists()
    assert (outdir / "tables/retention_enrichment.tsv").exists()
    assert (outdir / "report/final_report.md").exists()
    assert "wgd_final_report" in completed.stdout
