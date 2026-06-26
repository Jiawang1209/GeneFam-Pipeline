#!/usr/bin/env python3
"""Run a tree/motif/gene-structure/domain composite visualization smoke."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_tree_feature_matrix import build_tree_feature_matrix, read_tsv, write_tsv


def _default_tree_text() -> str:
    return "(BraA010001:0.2,(AT1G01010:0.1,AT1G01020:0.1):0.1);"


def _default_candidates() -> list[dict[str, str]]:
    return [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001"},
    ]


def _default_motifs() -> list[dict[str, str]]:
    return [
        {"motif_id": "1", "width": "11", "sites": "18"},
        {"motif_id": "2", "width": "7", "sites": "12"},
    ]


def _default_structures() -> list[dict[str, str]]:
    return [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01010", "gene_length": "501", "exon_count": "3", "cds_count": "3"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT1G01020", "gene_length": "321", "exon_count": "2", "cds_count": "2"},
        {"species_id": "Brassica_rapa", "gene_id": "BraA010001", "gene_length": "700", "exon_count": "4", "cds_count": "4"},
    ]


def _default_domains() -> list[dict[str, str]]:
    return [
        {"gene_id": "AT1G01010", "hmm_id": "PF00657", "domain_coverage": "0.90"},
        {"gene_id": "BraA010001", "hmm_id": "PF00657", "domain_coverage": "0.88"},
    ]


def _run_plot(matrix_path: Path, plot_dir: Path, r_bin: str) -> None:
    completed = subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_tree_features.R"),
            "--args",
            str(matrix_path),
            str(plot_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise RuntimeError(f"Tree feature plotting failed with {r_bin}: {output}")


def run_tree_feature_smoke(
    *,
    tree: Path | None,
    family_candidates: Path | None,
    motifs: Path | None,
    gene_structures: Path | None,
    domains: Path | None,
    r_bin: str,
    outdir: Path,
) -> dict[str, Path]:
    table_dir = outdir / "tables"
    plot_dir = outdir / "plots"
    matrix_path = table_dir / "tree_feature_matrix.tsv"
    summary_path = outdir / "tree_feature_smoke.md"
    rows = build_tree_feature_matrix(
        tree_text=tree.read_text(encoding="utf-8") if tree else _default_tree_text(),
        family_candidates=read_tsv(family_candidates) if family_candidates else _default_candidates(),
        motifs=read_tsv(motifs) if motifs else _default_motifs(),
        gene_structures=read_tsv(gene_structures) if gene_structures else _default_structures(),
        domains=read_tsv(domains) if domains else _default_domains(),
    )
    write_tsv(rows, matrix_path)
    _run_plot(matrix_path, plot_dir, r_bin)
    summary_path.write_text(
        "\n".join(
            [
                "# Tree Feature Smoke",
                "",
                f"Rows: {len(rows)}",
                f"Matrix: `{matrix_path}`",
                f"PDF plot: `{plot_dir / 'tree_features.pdf'}`",
                f"PNG plot: `{plot_dir / 'tree_features.png'}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "tree_feature_matrix": matrix_path,
        "tree_features_pdf": plot_dir / "tree_features.pdf",
        "tree_features_png": plot_dir / "tree_features.png",
        "summary": summary_path,
    }


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", default=None, type=Path)
    parser.add_argument("--family-candidates", default=None, type=Path)
    parser.add_argument("--motifs", default=None, type=Path)
    parser.add_argument("--gene-structures", default=None, type=Path)
    parser.add_argument("--domains", default=None, type=Path)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/tree_feature_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(
        run_tree_feature_smoke(
            tree=args.tree,
            family_candidates=args.family_candidates,
            motifs=args.motifs,
            gene_structures=args.gene_structures,
            domains=args.domains,
            r_bin=args.r_bin,
            outdir=args.outdir,
        )
    )


if __name__ == "__main__":
    main()
