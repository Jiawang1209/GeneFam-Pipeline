import subprocess
import sys
from pathlib import Path


def test_mcscanx_circlize_script_allows_tiny_sectors():
    script = Path("scripts/plot_mcscanx_circlize.R").read_text(encoding="utf-8")

    assert "cell.padding = c(0.02, 0, 0.02, 0)" in script


def test_mcscanx_circlize_script_uses_reference_style_tracks():
    script = Path("scripts/plot_mcscanx_circlize.R").read_text(encoding="utf-8")

    assert "circos.genomicLabels" in script
    assert "circos.genomicTrack(" in script
    assert "circos.genomicTrackPlotRegion" in script
    assert "circos.genomicLink" in script
    assert "ComplexHeatmap::Legend" in script
    assert "Gene Duplicate" in script
    assert "Gene Type" in script


def test_run_mcscanx_circlize_smoke_writes_inputs_and_plots(tmp_path):
    outdir = tmp_path / "mcscanx_circlize"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_mcscanx_circlize_smoke.py",
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
    assert (outdir / "tables" / "circlize_chromosomes.tsv").exists()
    assert (outdir / "tables" / "circlize_links.tsv").exists()
    assert (outdir / "tables" / "circlize_link_density.tsv").exists()
    assert (outdir / "tables" / "circlize_duplicate_type_tracks.tsv").exists()
    assert (outdir / "tables" / "circlize_skipped_links.tsv").exists()
    assert (outdir / "plots" / "mcscanx_circlize.pdf").exists()
    assert (outdir / "plots" / "mcscanx_circlize.png").exists()
    assert (outdir / "plots" / "species" / "Arabidopsis_thaliana" / "circos_Arabidopsis_thaliana.pdf").exists()
    assert (outdir / "plots" / "species" / "Arabidopsis_thaliana" / "circos_Arabidopsis_thaliana.png").exists()
    assert (outdir / "plots" / "species" / "Brassica_rapa" / "circos_Brassica_rapa.pdf").exists()
    assert (outdir / "plots" / "species" / "Brassica_rapa" / "circos_Brassica_rapa.png").exists()
    summary = (outdir / "mcscanx_circlize_smoke.md").read_text(encoding="utf-8")
    assert "MCScanX Circlize Smoke" in summary
    assert "circlize_links.tsv" in summary
    assert "circlize_link_density.tsv" in summary
    assert "circlize_duplicate_type_tracks.tsv" in summary
    assert "mcscanx_circlize.pdf" in summary
    assert "circos_Arabidopsis_thaliana.pdf" in summary
    assert "circos_Brassica_rapa.pdf" in summary
