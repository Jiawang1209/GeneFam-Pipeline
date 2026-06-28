import subprocess
import sys


def test_run_feature_summary_smoke_writes_statistics_and_plots(tmp_path):
    outdir = tmp_path / "feature_summary"
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    domains = inputs / "filtered_domains.tsv"
    motifs = inputs / "motif_summary.tsv"
    gene_structures = inputs / "gene_structure_summary.tsv"
    synteny = inputs / "syntenic_pairs.tsv"
    domains.write_text(
        "gene_id\tspecies_id\tdomain_coverage\n"
        "geneA\tsp1\t0.80\n"
        "geneB\tsp1\t0.60\n",
        encoding="utf-8",
    )
    motifs.write_text(
        "motif_id\twidth\tsites\n"
        "motif1\t12\t2\n"
        "motif2\t8\t1\n",
        encoding="utf-8",
    )
    gene_structures.write_text(
        "gene_id\tspecies_id\tgene_length\texon_count\n"
        "geneA\tsp1\t1200\t4\n"
        "geneB\tsp1\t900\t3\n",
        encoding="utf-8",
    )
    synteny.write_text(
        "block_id\tsource\ttarget\n"
        "block1\tgeneA\tgeneB\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_feature_summary_smoke.py",
            "--domains",
            str(domains),
            "--motifs",
            str(motifs),
            "--gene-structures",
            str(gene_structures),
            "--synteny",
            str(synteny),
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
