import subprocess
import sys

from bin.genefam.build_aranet_ppi_edges import build_aranet_ppi_edges, read_aranet_edges


def test_build_aranet_ppi_edges_transfers_arabidopsis_network_by_best_reference_hit(tmp_path):
    aranet = tmp_path / "AraNet.txt"
    aranet.write_text(
        "AT1G01010\tAT1G01020\t5.5\n"
        "AT1G01020\tAT1G99999\t4.2\n",
        encoding="utf-8",
    )
    candidates = [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010", "best_reference_hit": "AT1G01010"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020", "best_reference_hit": "AT1G01020"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA01g001", "best_reference_hit": "AT1G01010"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA01g002", "best_reference_hit": "AT1G01020"},
        {"species_id": "Capsella_rubella", "gene_id": "Carub001", "best_reference_hit": "AT1G01010"},
    ]

    outputs = build_aranet_ppi_edges(candidates, read_aranet_edges(aranet))

    assert outputs["edges"] == [
        {"source": "AT1G01010", "target": "AT1G01020", "weight": "5.5000", "species": "Arabidopsis_thaliana"},
        {"source": "BraA01g001", "target": "BraA01g002", "weight": "5.5000", "species": "Brassica_rapa"},
    ]
    evidence = {row["metric"]: row["value"] for row in outputs["evidence"]}
    assert evidence["aranet_edges_read"] == "2"
    assert evidence["transferred_edges"] == "2"
    assert evidence["species_with_transferred_edges"] == "2"


def test_build_aranet_ppi_edges_cli_writes_edges_nodes_and_evidence(tmp_path):
    aranet = tmp_path / "AraNet.txt"
    aranet.write_text("AT1G01010\tAT1G01020\t5.5\n", encoding="utf-8")
    candidates = tmp_path / "family_candidates.tsv"
    candidates.write_text(
        "species_id\tgene_id\tbest_reference_hit\n"
        "Brassica_rapa\tBraA01g001\tAT1G01010\n"
        "Brassica_rapa\tBraA01g002\tAT1G01020\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "out"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_aranet_ppi_edges.py",
            "--family-candidates",
            str(candidates),
            "--aranet",
            str(aranet),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "BraA01g001\tBraA01g002\t5.5000\tBrassica_rapa" in (outdir / "ppi_edges.tsv").read_text(encoding="utf-8")
    assert (outdir / "ppi_nodes.tsv").read_text(encoding="utf-8").startswith("node\tspecies\ttype\tdomain")
    assert "transferred_edges\t1" in (outdir / "ppi_transfer_evidence.tsv").read_text(encoding="utf-8")
