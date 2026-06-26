import subprocess
import sys


def test_run_pangenome_kaks_smoke_writes_tables_and_plots(tmp_path):
    outdir = tmp_path / "pangenome_kaks_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_pangenome_kaks_smoke.py",
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
    assert "pangenome_kaks_pdf" in completed.stdout
    assert (outdir / "tables/pangenome_kaks.tsv").exists()
    assert (outdir / "tables/pangenome_kaks_summary.tsv").exists()
    assert (outdir / "tables/pangenome_kaks_skipped.tsv").exists()
    assert (outdir / "plots/pangenome_kaks.pdf").exists()
    assert (outdir / "plots/pangenome_kaks.png").exists()

    summary = (outdir / "pangenome_kaks_smoke.md").read_text(encoding="utf-8")
    assert "# Pangenome Ka/Ks Smoke" in summary
    assert "Input pairs: 4" in summary
    assert "Grouped pair rows: 3" in summary
