import subprocess
import sys


def test_run_tree_feature_smoke_writes_matrix_and_plots(tmp_path):
    outdir = tmp_path / "tree_features"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_tree_feature_smoke.py",
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
    matrix = (outdir / "tables/tree_feature_matrix.tsv")
    assert matrix.exists()
    matrix_text = matrix.read_text(encoding="utf-8")
    assert "motif_architecture" in matrix_text
    assert "domain_architecture" in matrix_text
    assert (outdir / "plots/tree_features.pdf").exists()
    assert (outdir / "plots/tree_features.png").exists()
    summary = (outdir / "tree_feature_smoke.md").read_text(encoding="utf-8")
    assert "Tree Feature Smoke" in summary
    assert "tree_feature_matrix.tsv" in summary
    assert "tree_features.pdf" in summary
