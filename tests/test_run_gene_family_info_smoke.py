import subprocess
import sys
import csv


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
    assert (outdir / "plots/protein_properties_by_species.pdf").exists()
    assert (outdir / "plots/protein_properties_by_species.png").exists()
    layout = outdir / "plots/protein_properties_by_species.layout.tsv"
    assert layout.exists()
    with layout.open(encoding="utf-8") as handle:
        layout_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert layout_rows[0]["n_species"] == "3"
    assert float(layout_rows[0]["height"]) < 7.2
    with (outdir / "tables/gene_family_species_order.tsv").open(encoding="utf-8") as handle:
        order_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert [row["species_id"] for row in order_rows] == ["Osa", "Ath", "Bra", "Bna"]
    assert order_rows[0]["clade"] == "monocot"
    assert order_rows[0]["order_source"] == "external"
    assert order_rows[-1]["order_source"] == "copy_number_append"
    summary = (outdir / "gene_family_info_smoke.md").read_text(encoding="utf-8")
    assert "gene_family_copy_number.tsv" in summary
    assert "gene_family_species_order.tsv" in summary
    assert "External species order" in summary
    assert "gene_family_copy_number_expansion.tsv" in summary
    assert "gene_family_pangenome_summary.tsv" in summary
    assert "gene_family_info_summary.pdf" in summary
    assert "protein_properties_by_species.pdf" in summary
    assert "protein_properties_by_species.layout.tsv" in summary
