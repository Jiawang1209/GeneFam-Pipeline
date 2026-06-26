import subprocess
import sys


def test_run_kaks_wgd_plot_smoke_writes_annotation_table_and_plots(tmp_path):
    outdir = tmp_path / "kaks_wgd_plot_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_kaks_wgd_plot_smoke.py",
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
    assert "kaks_wgd_annotations" in completed.stdout
    assert (outdir / "tables/kaks_pairs.tsv").exists()
    assert (outdir / "tables/wgd_layers.tsv").exists()
    assert (outdir / "tables/kaks_wgd_annotations.tsv").exists()
    assert (outdir / "plots/ks_distribution.pdf").exists()
    assert (outdir / "plots/ks_distribution.png").exists()

    annotations = (outdir / "tables/kaks_wgd_annotations.tsv").read_text(encoding="utf-8")
    assert "alpha (WGD_layer_1, n=1)" in annotations
    assert "theta (WGD_layer_4, n=1)" in annotations

    summary = (outdir / "kaks_wgd_plot_smoke.md").read_text(encoding="utf-8")
    assert "# Ka/Ks WGD Annotation Plot Smoke" in summary
    assert "Annotated WGD layers: 4" in summary
