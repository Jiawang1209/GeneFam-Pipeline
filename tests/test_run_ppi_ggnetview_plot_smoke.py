import subprocess
import sys


def test_run_ppi_ggnetview_plot_smoke_writes_tables_status_and_plots(tmp_path):
    outdir = tmp_path / "ppi"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_ppi_ggnetview_plot_smoke.py",
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
    assert (outdir / "tables/ppi_edges.tsv").exists()
    assert (outdir / "tables/ppi_nodes.tsv").exists()
    assert (outdir / "tables/ppi_hubs.tsv").exists()
    assert (outdir / "tables/ppi_input_evidence.tsv").exists()
    assert (outdir / "tables/ppi_network_qc.tsv").exists()
    assert (outdir / "tables/ppi_ggnetview_status.tsv").exists()
    assert (outdir / "plots/ppi_ggnetview.pdf").exists()
    assert (outdir / "plots/ppi_ggnetview.png").exists()
    status = (outdir / "tables/ppi_ggnetview_status.tsv").read_text(encoding="utf-8")
    assert "ppi_ggnetview_plot\tready\tggNetView" in status
    summary = (outdir / "ppi_ggnetview_plot_smoke.md").read_text(encoding="utf-8")
    assert "ggNetView PPI Plot Smoke" in summary
    assert "ppi_hubs.tsv" in summary
    assert "ppi_input_evidence.tsv" in summary
    assert "ppi_network_qc.tsv" in summary
