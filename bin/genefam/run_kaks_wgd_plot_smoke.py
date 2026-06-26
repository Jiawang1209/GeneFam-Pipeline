#!/usr/bin/env python3
"""Run a Ks distribution plot smoke with WGD event annotations."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.build_kaks_plot_annotations import build_kaks_plot_annotations, write_tsv as write_annotations_tsv
from bin.genefam.classify_wgd_layers import classify_pairs, write_pairs


def _ks_pairs() -> list[dict[str, str]]:
    return [
        {"gene_a": "AT_ALPHA1", "gene_b": "AT_ALPHA2", "ks": "0.12"},
        {"gene_a": "BR_BETA1", "gene_b": "BR_BETA2", "ks": "0.55"},
        {"gene_a": "VV_GAMMA1", "gene_b": "VV_GAMMA2", "ks": "1.20"},
        {"gene_a": "BR_THETA1", "gene_b": "BR_THETA2", "ks": "1.80"},
    ]


def _write_pairs(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["gene_a", "gene_b", "ks"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def run_kaks_wgd_plot_smoke(*, r_bin: str, outdir: Path) -> dict[str, Path]:
    tables_dir = outdir / "tables"
    plots_dir = outdir / "plots"
    summary = outdir / "kaks_wgd_plot_smoke.md"
    outputs = {
        "kaks_pairs": tables_dir / "kaks_pairs.tsv",
        "wgd_layers": tables_dir / "wgd_layers.tsv",
        "kaks_wgd_annotations": tables_dir / "kaks_wgd_annotations.tsv",
        "ks_distribution_pdf": plots_dir / "ks_distribution.pdf",
        "ks_distribution_png": plots_dir / "ks_distribution.png",
        "summary": summary,
    }
    event_names = {
        "WGD_layer_1": "alpha",
        "WGD_layer_2": "beta",
        "WGD_layer_3": "gamma",
        "WGD_layer_4": "theta",
    }
    classified = classify_pairs(_ks_pairs(), bins=[0.3, 0.8, 1.5], named_events=event_names)
    annotations = build_kaks_plot_annotations(classified)
    _write_pairs(_ks_pairs(), outputs["kaks_pairs"])
    write_pairs(classified, outputs["wgd_layers"])
    write_annotations_tsv(annotations, outputs["kaks_wgd_annotations"])

    completed = subprocess.run(
        [
            r_bin,
            "--vanilla",
            "--slave",
            "-f",
            str(REPO_ROOT / "scripts/plot_kaks.R"),
            "--args",
            str(outputs["kaks_pairs"]),
            str(outputs["kaks_wgd_annotations"]),
            str(plots_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
        raise RuntimeError(f"Ka/Ks WGD annotation plotting failed with {r_bin}: {output}")

    summary.write_text(
        "\n".join(
            [
                "# Ka/Ks WGD Annotation Plot Smoke",
                "",
                f"Input pairs: {len(_ks_pairs())}",
                f"Annotated WGD layers: {len(annotations)}",
                f"Annotation table: `{outputs['kaks_wgd_annotations']}`",
                f"PDF plot: `{outputs['ks_distribution_pdf']}`",
                f"PNG plot: `{outputs['ks_distribution_png']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    print("output\tpath")
    for key, path in outputs.items():
        print(f"{key}\t{path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", default="/usr/local/bin/R")
    parser.add_argument("--outdir", default=Path("results/kaks_wgd_plot_smoke"), type=Path)
    args = parser.parse_args()
    _print_outputs(run_kaks_wgd_plot_smoke(r_bin=args.r_bin, outdir=args.outdir))


if __name__ == "__main__":
    main()
