import subprocess
import sys

from bin.genefam.summarize_feature_tables import summarize_feature_tables


def test_summarize_feature_tables_builds_report_ready_metrics():
    rows = summarize_feature_tables(
        domains=[
            {"species_id": "Ath", "gene_id": "gene1", "hmm_id": "PF1", "domain_coverage": "0.90"},
            {"species_id": "Bra", "gene_id": "gene2", "hmm_id": "PF1", "domain_coverage": "0.80"},
        ],
        motifs=[
            {"family_name": "GDSL", "motif_id": "1", "width": "11", "sites": "18", "evalue": "1e-10"},
            {"family_name": "GDSL", "motif_id": "2", "width": "7", "sites": "12", "evalue": "1e-5"},
        ],
        gene_structures=[
            {"species_id": "Ath", "gene_id": "gene1", "gene_length": "400", "exon_count": "2", "cds_count": "2"},
            {"species_id": "Bra", "gene_id": "gene2", "gene_length": "600", "exon_count": "4", "cds_count": "4"},
        ],
        synteny=[
            {"block_id": "0", "gene_a": "gene1", "gene_b": "gene2"},
            {"block_id": "0", "gene_a": "gene3", "gene_b": "gene4"},
        ],
        promoters=[
            {"species_id": "Ath", "gene_id": "gene1", "promoter_length": "1000", "boundary_clipped": "false"},
            {"species_id": "Bra", "gene_id": "gene2", "promoter_length": "750", "boundary_clipped": "true"},
        ],
    )

    by_key = {(row["feature"], row["metric"], row["group"]): row["value"] for row in rows}
    assert by_key[("domain", "domain_hit_count", "all")] == "2"
    assert by_key[("domain", "genes_with_domain", "all")] == "2"
    assert by_key[("motif", "motif_count", "all")] == "2"
    assert by_key[("motif", "total_sites", "all")] == "30"
    assert by_key[("gene_structure", "mean_gene_length", "all")] == "500.0000"
    assert by_key[("gene_structure", "mean_exon_count", "all")] == "3.0000"
    assert by_key[("synteny", "syntenic_pair_count", "all")] == "2"
    assert by_key[("synteny", "block_count", "all")] == "1"
    assert by_key[("promoter", "mean_promoter_length", "all")] == "875.0000"
    assert by_key[("promoter", "boundary_clipped_count", "all")] == "1"


def test_summarize_feature_tables_cli_writes_tsv(tmp_path):
    domains = tmp_path / "domains.tsv"
    domains.write_text(
        "species_id\tgene_id\thmm_id\tdomain_coverage\nAth\tgene1\tPF1\t0.90\n",
        encoding="utf-8",
    )
    out = tmp_path / "summary.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/summarize_feature_tables.py",
            "--domains",
            str(domains),
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert out.read_text(encoding="utf-8").splitlines() == [
        "feature\tmetric\tgroup\tvalue",
        "domain\tdomain_hit_count\tall\t1",
        "domain\tgenes_with_domain\tall\t1",
        "domain\tmean_domain_coverage\tall\t0.9000",
        "domain\tdomain_hit_count_by_species\tAth\t1",
    ]
