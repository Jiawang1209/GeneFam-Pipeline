#!/usr/bin/env python3
"""Run an offline WGD/named-event smoke test for gamma beta alpha theta evidence."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.annotate_family_wgd_events import annotate_family_wgd_events, write_tsv as write_family_wgd_tsv
from bin.genefam.assemble_report import assemble_report, read_tsv, write_report
from bin.genefam.build_wgd_event_evidence import build_event_evidence, load_event_metadata, write_tsv as write_evidence_tsv
from bin.genefam.classify_wgd_layers import classify_pairs, write_pairs
from bin.genefam.join_family_duplicates import join_family_duplicates, write_tsv as write_joined_tsv
from bin.genefam.normalize_duplicate_types import normalize_duplicate_rows, write_tsv as write_duplicate_tsv
from bin.genefam.retention_enrichment import compute_enrichment, write_tsv as write_enrichment_tsv
from bin.genefam.summarize_family_event_retention import (
    summarize_family_event_retention,
    write_tsv as write_retention_tsv,
)


def _family_rows() -> list[dict[str, str]]:
    return [
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT_ALPHA1"},
        {"species_id": "Arabidopsis_thaliana", "gene_id": "AT_ALPHA2"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_BETA1"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_BETA2"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_THETA1"},
        {"species_id": "Brassica_rapa", "gene_id": "BR_THETA2"},
        {"species_id": "Vitis_vinifera", "gene_id": "VV_GAMMA1"},
        {"species_id": "Vitis_vinifera", "gene_id": "VV_GAMMA2"},
    ]


def _duplicate_rows() -> list[dict[str, str]]:
    family_genes = [row["gene_id"] for row in _family_rows()]
    background = [
        {"gene_id": gene_id, "duplicate_type": "wgd"}
        for gene_id in family_genes
    ]
    background.extend(
        [
            {"gene_id": "BG_TANDEM1", "duplicate_type": "tandem"},
            {"gene_id": "BG_TANDEM2", "duplicate_type": "tandem"},
            {"gene_id": "BG_DISPERSED1", "duplicate_type": "dispersed"},
            {"gene_id": "BG_SINGLETON1", "duplicate_type": "singleton"},
        ]
    )
    return background


def _ks_pairs() -> list[dict[str, str]]:
    return [
        {"gene_a": "AT_ALPHA1", "gene_b": "AT_ALPHA2", "ks": "0.12"},
        {"gene_a": "BR_BETA1", "gene_b": "BR_BETA2", "ks": "0.55"},
        {"gene_a": "VV_GAMMA1", "gene_b": "VV_GAMMA2", "ks": "1.20"},
        {"gene_a": "BR_THETA1", "gene_b": "BR_THETA2", "ks": "1.80"},
    ]


def _write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def run_wgd_smoke(events_config: Path, outdir: Path) -> dict[str, Path]:
    tables_dir = outdir / "tables"
    report_dir = outdir / "report"
    outputs = {
        "family_members": tables_dir / "family_members.tsv",
        "duplicates": tables_dir / "duplicates.tsv",
        "normalized_duplicates": tables_dir / "normalized_duplicate_types.tsv",
        "family_duplicates": tables_dir / "family_duplicate_classification.tsv",
        "kaks_pairs": tables_dir / "kaks_pairs.tsv",
        "wgd_layers": tables_dir / "wgd_layers.tsv",
        "wgd_event_evidence": tables_dir / "wgd_event_evidence.tsv",
        "family_wgd_event_membership": tables_dir / "family_wgd_event_membership.tsv",
        "family_event_retention_summary": tables_dir / "family_event_retention_summary.tsv",
        "retention_enrichment": tables_dir / "retention_enrichment.tsv",
        "report_index": report_dir / "report_index.tsv",
        "wgd_final_report": report_dir / "final_report.md",
    }

    family_rows = _family_rows()
    duplicate_rows = _duplicate_rows()
    normalized_duplicates = normalize_duplicate_rows(duplicate_rows)
    family_duplicates = join_family_duplicates(family_rows, normalized_duplicates)
    classified_pairs = classify_pairs(
        _ks_pairs(),
        bins=[0.3, 0.8, 1.5],
        named_events={
            "WGD_layer_1": "alpha",
            "WGD_layer_2": "beta",
            "WGD_layer_3": "gamma",
            "WGD_layer_4": "theta",
        },
    )
    evidence = build_event_evidence(classified_pairs, load_event_metadata(events_config))
    family_wgd_events = annotate_family_wgd_events(family_duplicates, classified_pairs)
    retention_summary = summarize_family_event_retention(family_wgd_events)
    enrichment = compute_enrichment(family_duplicates, normalized_duplicates)
    report_index = [
        {
            "key": key,
            "path": str(path),
            "status": "available",
            "description": key.replace("_", " "),
        }
        for key, path in outputs.items()
        if key not in {"report_index", "wgd_final_report"}
    ]

    _write_tsv(family_rows, ["species_id", "gene_id"], outputs["family_members"])
    _write_tsv(duplicate_rows, ["gene_id", "duplicate_type"], outputs["duplicates"])
    write_duplicate_tsv(normalized_duplicates, outputs["normalized_duplicates"])
    write_joined_tsv(family_duplicates, outputs["family_duplicates"])
    _write_tsv(_ks_pairs(), ["gene_a", "gene_b", "ks"], outputs["kaks_pairs"])
    write_pairs(classified_pairs, outputs["wgd_layers"])
    write_evidence_tsv(evidence, outputs["wgd_event_evidence"])
    write_family_wgd_tsv(family_wgd_events, outputs["family_wgd_event_membership"])
    write_retention_tsv(retention_summary, outputs["family_event_retention_summary"])
    write_enrichment_tsv(enrichment, outputs["retention_enrichment"])
    _write_tsv(report_index, ["key", "path", "status", "description"], outputs["report_index"])
    write_report(
        assemble_report(
            project_name="WGD smoke",
            gene_family="GDSL",
            report_index_rows=read_tsv(outputs["report_index"]),
            wgd_event_evidence=evidence,
            family_event_retention=retention_summary,
            retention_enrichment=enrichment,
        ),
        outputs["wgd_final_report"],
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events-config", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_wgd_smoke(args.events_config, args.outdir))


if __name__ == "__main__":
    main()
