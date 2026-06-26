import subprocess
import sys
from pathlib import Path


def test_run_promoter_cis_smoke_writes_tables_and_plots(tmp_path):
    outdir = tmp_path / "promoter_cis_smoke"

    result = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_promoter_cis_smoke.py",
            "--r-bin",
            "/usr/local/bin/R",
            "--outdir",
            str(outdir),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "promoter_cis_elements" in result.stdout
    assert (outdir / "tables/promoter_cis_elements.tsv").exists()
    assert (outdir / "tables/promoter_cis_gene_matrix.tsv").exists()
    assert (outdir / "tables/promoter_cis_category_summary.tsv").exists()
    assert (outdir / "plots/promoter_cis_elements.pdf").exists()
    assert (outdir / "plots/promoter_cis_elements.png").exists()
    summary = (outdir / "promoter_cis_smoke.md").read_text(encoding="utf-8")
    assert "promoter_cis_category_summary.tsv" in summary
    assert "promoter_cis_elements.pdf" in summary
