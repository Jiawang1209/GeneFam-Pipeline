from bin.genefam.build_aranet_ppi_from_reciprocal_blast import (
    build_homology_rows,
    read_aranet_edges,
    read_outfmt6,
    transfer_aranet_edges,
)


def test_build_homology_rows_records_reciprocal_blast_support():
    candidates = [
        {"species_id": "Brassica_rapa", "gene_id": "BraA01g001"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA01g002"},
    ]
    forward = {
        "Brassica_rapa": [
            {"qseqid": "BraA01g001", "sseqid": "AT1G01010.1", "evalue": "1e-80", "bitscore": "250"},
            {"qseqid": "BraA01g002", "sseqid": "AT1G01020.1", "evalue": "1e-60", "bitscore": "200"},
        ]
    }
    reverse = {
        "Brassica_rapa": [
            {"qseqid": "AT1G01010.1", "sseqid": "BraA01g001", "evalue": "1e-70", "bitscore": "230"},
            {"qseqid": "AT1G01020.1", "sseqid": "BraA01g999", "evalue": "1e-40", "bitscore": "180"},
        ]
    }

    rows = build_homology_rows(candidates, forward, reverse)

    assert rows == [
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA01g001",
            "arabidopsis_gene_id": "AT1G01010",
            "forward_evalue": "1e-80",
            "forward_bitscore": "250",
            "reciprocal_target": "BraA01g001",
            "reciprocal_evalue": "1e-70",
            "reciprocal_bitscore": "230",
            "reciprocal_supported": "true",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA01g002",
            "arabidopsis_gene_id": "AT1G01020",
            "forward_evalue": "1e-60",
            "forward_bitscore": "200",
            "reciprocal_target": "BraA01g999",
            "reciprocal_evalue": "1e-40",
            "reciprocal_bitscore": "180",
            "reciprocal_supported": "false",
        },
    ]


def test_transfer_aranet_edges_uses_reciprocal_blast_homology_rows(tmp_path):
    aranet = tmp_path / "AraNet.txt"
    aranet.write_text("AT1G01010\tAT1G01020\t5.5\n", encoding="utf-8")
    homology_rows = [
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA01g001",
            "arabidopsis_gene_id": "AT1G01010",
            "reciprocal_supported": "true",
        },
        {
            "species_id": "Brassica_rapa",
            "gene_id": "BraA01g002",
            "arabidopsis_gene_id": "AT1G01020",
            "reciprocal_supported": "false",
        },
    ]

    outputs = transfer_aranet_edges(homology_rows, read_aranet_edges(aranet))

    assert outputs["edges"] == [
        {"source": "BraA01g001", "target": "BraA01g002", "weight": "5.5000", "species": "Brassica_rapa"}
    ]
    evidence = {row["metric"]: row["value"] for row in outputs["evidence"]}
    assert evidence["homology_rows"] == "2"
    assert evidence["reciprocal_supported_homologs"] == "1"
    assert evidence["transferred_edges"] == "1"


def test_reciprocal_blast_cli_accepts_existing_outfmt6_tables_without_diamond(tmp_path):
    forward = tmp_path / "forward.tsv"
    reverse = tmp_path / "reverse.tsv"
    forward.write_text("BraA01g001\tAT1G01010.1\t90\t100\t0\t0\t1\t100\t1\t100\t1e-80\t250\t100\t100\n", encoding="utf-8")
    reverse.write_text("AT1G01010.1\tBraA01g001\t91\t100\t0\t0\t1\t100\t1\t100\t1e-70\t230\t100\t100\n", encoding="utf-8")

    rows = build_homology_rows(
        [{"species_id": "Brassica_rapa", "gene_id": "BraA01g001"}],
        {"Brassica_rapa": read_outfmt6(forward)},
        {"Brassica_rapa": read_outfmt6(reverse)},
    )

    assert rows[0]["arabidopsis_gene_id"] == "AT1G01010"
    assert rows[0]["reciprocal_supported"] == "true"
