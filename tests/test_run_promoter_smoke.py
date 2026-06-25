import subprocess
import sys


def test_run_promoter_smoke_writes_promoters_and_plots(tmp_path):
    outdir = tmp_path / "promoter_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_promoter_smoke.py",
            "--r-bin",
            "/usr/local/bin/R",
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "tables" / "promoters.bed").exists()
    assert (outdir / "sequences" / "promoters.fa").exists()
    assert (outdir / "tables" / "feature_summary.tsv").exists()
    assert (outdir / "plots" / "feature_summary.pdf").exists()
    assert (outdir / "plots" / "feature_summary.png").exists()
    summary = (outdir / "promoter_smoke.md").read_text(encoding="utf-8")
    assert "Promoter Smoke" in summary
    assert "promoters.bed" in summary
    assert "feature_summary.pdf" in summary
