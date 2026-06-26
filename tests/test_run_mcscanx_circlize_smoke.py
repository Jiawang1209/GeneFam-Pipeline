import subprocess
import sys


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
    summary = (outdir / "mcscanx_circlize_smoke.md").read_text(encoding="utf-8")
    assert "MCScanX Circlize Smoke" in summary
    assert "circlize_links.tsv" in summary
    assert "circlize_link_density.tsv" in summary
    assert "circlize_duplicate_type_tracks.tsv" in summary
    assert "mcscanx_circlize.pdf" in summary
