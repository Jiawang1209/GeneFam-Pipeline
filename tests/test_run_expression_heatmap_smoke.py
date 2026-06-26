import subprocess
import sys


def test_run_expression_heatmap_smoke_writes_annotation_tables_and_plots(tmp_path):
    outdir = tmp_path / "expression_heatmap_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_expression_heatmap_smoke.py",
            "--expression",
            "tests/fixtures/expression/family_expression.tsv",
            "--metadata",
            "tests/fixtures/expression/sample_metadata.tsv",
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
    assert "expression_heatmap_pdf" in completed.stdout
    assert (outdir / "tables/expression_sample_metadata.tsv").exists()
    assert (outdir / "tables/expression_group_matrix.tsv").exists()
    assert (outdir / "tables/expression_gene_summary.tsv").exists()
    assert (outdir / "plots/expression_heatmap.pdf").exists()
    assert (outdir / "plots/expression_heatmap.png").exists()
    summary = (outdir / "expression_heatmap_smoke.md").read_text(encoding="utf-8")
    assert "# Expression Heatmap Smoke" in summary
    assert "Sample metadata:" in summary
