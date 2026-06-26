import subprocess
import sys

from bin.genefam.build_tree_feature_matrix import build_tree_feature_matrix


def test_build_tree_feature_matrix_orders_genes_by_tree_leaves_and_summarizes_tracks():
    rows = build_tree_feature_matrix(
        tree_text="(BraA010001:0.2,(AT1G01010:0.1,AT1G01020:0.1):0.1);",
        family_candidates=[
            {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
            {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020"},
            {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
        ],
        motifs=[
            {"motif_id": "1", "width": "11", "sites": "18"},
            {"motif_id": "2", "width": "7", "sites": "12"},
        ],
        gene_structures=[
            {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010", "gene_length": "501", "exon_count": "3", "cds_count": "3"},
            {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020", "gene_length": "321", "exon_count": "2", "cds_count": "2"},
            {"species_id": "Brassica_rapa", "gene_id": "BraA010001", "gene_length": "700", "exon_count": "4", "cds_count": "4"},
        ],
        domains=[
            {"gene_id": "AT1G01010", "hmm_id": "PF00657", "domain_coverage": "0.90"},
            {"gene_id": "AT1G01010", "hmm_id": "PF00657", "domain_coverage": "0.75"},
            {"gene_id": "BraA010001", "hmm_id": "PF00657", "domain_coverage": "0.88"},
        ],
    )

    assert [row["gene_id"] for row in rows] == ["BraA010001", "AT1G01010", "AT1G01020"]
    assert rows[0]["tree_order"] == "1"
    assert rows[0]["motif_catalog_count"] == "2"
    assert rows[0]["motif_total_sites"] == "30"
    assert rows[0]["motif_mean_width"] == "9.0000"
    assert rows[1]["domain_count"] == "2"
    assert rows[1]["best_domain_coverage"] == "0.9000"
    assert rows[2]["domain_count"] == "0"


def test_build_tree_feature_matrix_cli_writes_tsv(tmp_path):
    tree = tmp_path / "tree.nwk"
    candidates = tmp_path / "family_candidates.tsv"
    motifs = tmp_path / "motif_summary.tsv"
    structures = tmp_path / "gene_structure_summary.tsv"
    domains = tmp_path / "domains.tsv"
    out = tmp_path / "tree_feature_matrix.tsv"
    tree.write_text("(geneA:0.1,geneB:0.2);", encoding="utf-8")
    candidates.write_text("species_id\tgene_id\nsp1\tgeneA\nsp2\tgeneB\n", encoding="utf-8")
    motifs.write_text("motif_id\twidth\tsites\n1\t10\t5\n", encoding="utf-8")
    structures.write_text(
        "species_id\tgene_id\tgene_length\texon_count\tcds_count\nsp1\tgeneA\t100\t2\t2\nsp2\tgeneB\t200\t3\t3\n",
        encoding="utf-8",
    )
    domains.write_text("gene_id\thmm_id\tdomain_coverage\ngeneB\tPF1\t0.5\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_tree_feature_matrix.py",
            "--tree",
            str(tree),
            "--family-candidates",
            str(candidates),
            "--motifs",
            str(motifs),
            "--gene-structures",
            str(structures),
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
    text = out.read_text(encoding="utf-8")
    assert text.startswith("tree_order\tspecies_id\tgene_id\t")
    assert "2\tsp2\tgeneB\t200\t3\t3\t1\t0.5000\t1\t5\t10.0000" in text
