import subprocess
import sys


def test_run_duplicate_type_kaks_smoke_writes_tables_and_plots(tmp_path):
    outdir = tmp_path / "duplicate_type_kaks_smoke"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_duplicate_type_kaks_smoke.py",
            "--duplicates",
            "examples/prepared_wgd_handoff/duplicate_types.tsv",
            "--kaks-pairs",
            "examples/prepared_wgd_handoff/kaks_pairs.tsv",
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
    assert "duplicate_type_kaks_pdf" in completed.stdout
    assert (outdir / "tables/duplicate_type_kaks.tsv").exists()
    assert (outdir / "tables/duplicate_type_kaks_summary.tsv").exists()
    assert (outdir / "plots/duplicate_type_kaks.pdf").exists()
    assert (outdir / "plots/duplicate_type_kaks.png").exists()

    summary = (outdir / "duplicate_type_kaks_smoke.md").read_text(encoding="utf-8")
    assert "# Duplicate-Type Ka/Ks Smoke" in summary
    assert "Input pairs: 4" in summary
    assert "Grouped pair rows: 4" in summary
