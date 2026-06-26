import subprocess
import sys

from bin.genefam.build_ppi_tables import build_ppi_tables


def test_build_ppi_tables_normalizes_edges_nodes_and_hubs():
    outputs = build_ppi_tables(
        edges=[
            {"source": "geneA", "target": "geneB", "weight": "5", "species": "sp1"},
            {"source": "geneA", "target": "geneC", "weight": "3", "species": "sp1"},
            {"source": "geneB", "target": "geneB", "weight": "9", "species": "sp1"},
        ],
        node_annotations=[
            {"node": "geneA", "type": "GDSL", "species": "sp1", "domain": "PF00657"},
            {"node": "geneB", "type": "GDSL", "species": "sp1", "domain": "PF00657"},
        ],
        top_n=2,
    )

    assert outputs["edges"] == [
        {"source": "geneA", "target": "geneB", "weight": "5.0000", "species": "sp1"},
        {"source": "geneA", "target": "geneC", "weight": "3.0000", "species": "sp1"},
    ]
    by_node = {row["node"]: row for row in outputs["nodes"]}
    assert by_node["geneA"]["degree"] == "2"
    assert by_node["geneA"]["weighted_degree"] == "8.0000"
    assert by_node["geneC"]["type"] == "Others"
    assert outputs["hubs"][0]["node"] == "geneA"
    assert outputs["hubs"][0]["rank"] == "1"
    evidence = {row["metric"]: row["value"] for row in outputs["input_evidence"]}
    assert evidence["raw_edge_rows"] == "3"
    assert evidence["normalized_edge_rows"] == "2"
    assert evidence["skipped_self_loops"] == "1"
    assert evidence["duplicate_edge_rows"] == "0"
    qc = {row["metric"]: row["value"] for row in outputs["network_qc"]}
    assert qc["node_count"] == "3"
    assert qc["edge_count"] == "2"
    assert qc["missing_annotation_nodes"] == "1"


def test_build_ppi_tables_cli_writes_outputs(tmp_path):
    edges = tmp_path / "edges.tsv"
    nodes = tmp_path / "nodes.tsv"
    outdir = tmp_path / "out"
    edges.write_text("source\ttarget\tweight\tspecies\ngeneA\tgeneB\t5\tsp1\n", encoding="utf-8")
    nodes.write_text("node\ttype\tspecies\tdomain\ngeneA\tGDSL\tsp1\tPF00657\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_ppi_tables.py",
            "--edges",
            str(edges),
            "--nodes",
            str(nodes),
            "--outdir",
            str(outdir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert (outdir / "ppi_edges.tsv").read_text(encoding="utf-8").startswith("source\ttarget\tweight\tspecies")
    assert (outdir / "ppi_nodes.tsv").read_text(encoding="utf-8").startswith("node\tspecies\ttype\tdomain")
    assert (outdir / "ppi_hubs.tsv").read_text(encoding="utf-8").startswith("rank\tnode\tspecies")
    assert (outdir / "ppi_input_evidence.tsv").read_text(encoding="utf-8").startswith("metric\tvalue\tdescription")
    assert (outdir / "ppi_network_qc.tsv").read_text(encoding="utf-8").startswith("metric\tvalue\tdescription")
