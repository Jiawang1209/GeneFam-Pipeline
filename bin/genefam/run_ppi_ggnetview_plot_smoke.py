#!/usr/bin/env python3
"""Run a ggNetView PPI table and plot smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_ppi_tables import (
    EDGE_FIELDS,
    HUB_FIELDS,
    METRIC_FIELDS,
    NODE_FIELDS,
    build_ppi_tables,
    write_tsv,
)


def _demo_edges() -> list[dict[str, str]]:
    return [
        {"source": "AT1G01010", "target": "AT1G01020", "weight": "5", "species": "Arabidopsis_thaliana"},
        {"source": "AT1G01010", "target": "AT1G01030", "weight": "3", "species": "Arabidopsis_thaliana"},
        {"source": "AT1G01020", "target": "AT1G01030", "weight": "2", "species": "Arabidopsis_thaliana"},
        {"source": "BraA010001", "target": "BraA010002", "weight": "4", "species": "Brassica_rapa"},
        {"source": "BraA010001", "target": "BraA010003", "weight": "2", "species": "Brassica_rapa"},
    ]


def _demo_nodes() -> list[dict[str, str]]:
    return [
        {"node": "AT1G01010", "type": "GDSL", "species": "Arabidopsis_thaliana", "domain": "PF00657"},
        {"node": "AT1G01020", "type": "GDSL", "species": "Arabidopsis_thaliana", "domain": "PF00657"},
        {"node": "BraA010001", "type": "GDSL", "species": "Brassica_rapa", "domain": "PF00657"},
    ]


def run_ppi_ggnetview_plot_smoke(r_bin: str, outdir: Path) -> dict[str, Path]:
    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    status = table_dir / "ppi_ggnetview_status.tsv"
    summary = outdir / "ppi_ggnetview_plot_smoke.md"
    outputs = build_ppi_tables(edges=_demo_edges(), node_annotations=_demo_nodes(), top_n=10)
    edge_path = table_dir / "ppi_edges.tsv"
    node_path = table_dir / "ppi_nodes.tsv"
    hub_path = table_dir / "ppi_hubs.tsv"
    evidence_path = table_dir / "ppi_input_evidence.tsv"
    qc_path = table_dir / "ppi_network_qc.tsv"
    write_tsv(outputs["edges"], edge_path, EDGE_FIELDS)
    write_tsv(outputs["nodes"], node_path, NODE_FIELDS)
    write_tsv(outputs["hubs"], hub_path, HUB_FIELDS)
    write_tsv(outputs["input_evidence"], evidence_path, METRIC_FIELDS)
    write_tsv(outputs["network_qc"], qc_path, METRIC_FIELDS)
    completed = subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_ppi_ggnetview.R"),
            "--args",
            str(edge_path),
            str(node_path),
            str(plot_dir),
            str(status),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise RuntimeError(f"ggNetView PPI plotting failed with {r_bin}: {output}")
    summary.write_text(
        "\n".join(
            [
                "# ggNetView PPI Plot Smoke",
                "",
                f"Edges: `{edge_path}`",
                f"Nodes: `{node_path}`",
                f"Hubs: `{hub_path}`",
                f"Input evidence: `{evidence_path}`",
                f"Network QC: `{qc_path}`",
                f"Status: `{status}`",
                f"PDF plot: `{plot_dir / 'ppi_ggnetview.pdf'}`",
                f"PNG plot: `{plot_dir / 'ppi_ggnetview.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "ppi_edges": edge_path,
        "ppi_nodes": node_path,
        "ppi_hubs": hub_path,
        "ppi_input_evidence": evidence_path,
        "ppi_network_qc": qc_path,
        "ppi_status": status,
        "ppi_pdf": plot_dir / "ppi_ggnetview.pdf",
        "ppi_png": plot_dir / "ppi_ggnetview.png",
        "summary": summary,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/ppi_ggnetview_plot_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_ppi_ggnetview_plot_smoke(args.r_bin, args.outdir))


if __name__ == "__main__":
    main()
