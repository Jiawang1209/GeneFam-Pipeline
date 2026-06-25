import subprocess
import sys


def test_run_feature_summary_smoke_writes_statistics_and_plots(tmp_path):
    outdir = tmp_path / "feature_summary"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_feature_summary_smoke.py",
            "--domains",
            "results/domain_filter_smoke/tables/filtered_domains.tsv",
            "--motifs",
            "results/motif_smoke/tables/motif_summary.tsv",
            "--gene-structures",
            "results/gene_structure_smoke/tables/gene_structure_summary.tsv",
            "--synteny",
            "results/synteny_smoke/tables/syntenic_pairs.tsv",
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
    assert (outdir / "tables/feature_summary.tsv").exists()
    assert (outdir / "plots/feature_summary.pdf").exists()
    assert (outdir / "plots/feature_summary.png").exists()
    summary = (outdir / "feature_summary_smoke.md").read_text(encoding="utf-8")
    assert "Feature Summary Smoke" in summary
    assert "feature_summary.tsv" in summary
    assert "feature_summary.pdf" in summary
