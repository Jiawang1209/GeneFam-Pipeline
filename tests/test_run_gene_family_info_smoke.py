import subprocess
import sys


def test_run_gene_family_info_smoke_writes_tables_and_plots(tmp_path):
    outdir = tmp_path / "gene_family_info"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/run_gene_family_info_smoke.py",
            "--r-bin",
            "/usr/local/bin/R",
            "--outdir",
            str(outdir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "gene_family_copy_number" in completed.stdout
    assert (outdir / "tables/gene_family_copy_number.tsv").exists()
    assert (outdir / "tables/gene_family_copy_number_summary.tsv").exists()
    assert (outdir / "tables/gene_family_species_order.tsv").exists()
    assert (outdir / "tables/gene_family_copy_number_expansion.tsv").exists()
    assert (outdir / "tables/gene_family_pangenome_summary.tsv").exists()
    assert (outdir / "tables/gene_family_protein_properties.tsv").exists()
    assert (outdir / "plots/gene_family_info_summary.pdf").exists()
    assert (outdir / "plots/gene_family_info_summary.png").exists()
    summary = (outdir / "gene_family_info_smoke.md").read_text(encoding="utf-8")
    assert "gene_family_copy_number.tsv" in summary
    assert "gene_family_species_order.tsv" in summary
    assert "gene_family_copy_number_expansion.tsv" in summary
    assert "gene_family_pangenome_summary.tsv" in summary
    assert "gene_family_info_summary.pdf" in summary
