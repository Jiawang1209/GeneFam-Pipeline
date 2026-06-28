#!/usr/bin/env python3
"""Normalize many Reference KaKs_Calculator outputs into one WGD-ready pair table."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


PAIR_FIELDS = ["gene_a", "gene_b", "ks", "ka", "ka_ks", "p_value", "selection_category", "source", "pair_id", "method"]
SKIPPED_FIELDS = ["pair_id", "source", "kaks_result", "reason", "note"]
SUMMARY_FIELDS = ["status", "input_count", "available_count", "skipped_count", "note"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _selection_category(value: str) -> str:
    ratio = float(value)
    if ratio < 1:
        return "purifying"
    if ratio > 1:
        return "positive"
    return "neutral"


def _genes_from_pair_id(pair_id: str) -> tuple[str, str]:
    parts = pair_id.split("__")
    if len(parts) < 4:
        raise ValueError(f"Could not parse pair_id into genes: {pair_id}")
    return parts[-2], parts[-1]


def _first_kaks_row(path: Path) -> dict[str, str] | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    rows = read_tsv(path)
    return rows[0] if rows else None


def normalize_reference_kaks_results(*, results: list[dict[str, str]], outdir: Path) -> dict[str, Path]:
    outdir = Path(outdir)
    outputs = {
        "pairs": outdir / "kaks_pairs.tsv",
        "skipped": outdir / "kaks_pairs_skipped.tsv",
        "summary": outdir / "kaks_pairs_summary.tsv",
    }
    pair_rows: list[dict[str, str]] = []
    skipped_rows: list[dict[str, str]] = []

    for row in results:
        pair_id = row.get("pair_id", "")
        source = row.get("source", "")
        result_path = Path(row.get("kaks_result", ""))
        if row.get("status") != "available":
            skipped_rows.append(
                {
                    "pair_id": pair_id,
                    "source": source,
                    "kaks_result": str(result_path),
                    "reason": "calculator_failed",
                    "note": row.get("note", ""),
                }
            )
            continue
        kaks_row = _first_kaks_row(result_path)
        if not kaks_row:
            skipped_rows.append(
                {
                    "pair_id": pair_id,
                    "source": source,
                    "kaks_result": str(result_path),
                    "reason": "empty_result",
                    "note": "empty or unreadable KaKs result",
                }
            )
            continue
        gene_a, gene_b = _genes_from_pair_id(pair_id)
        ka_ks = kaks_row.get("Ka/Ks", kaks_row.get("ka_ks", ""))
        pair_rows.append(
            {
                "gene_a": gene_a,
                "gene_b": gene_b,
                "ks": kaks_row.get("Ks", kaks_row.get("ks", "")),
                "ka": kaks_row.get("Ka", kaks_row.get("ka", "")),
                "ka_ks": ka_ks,
                "p_value": kaks_row.get("P-Value(Fisher)", kaks_row.get("p_value", "")),
                "selection_category": _selection_category(ka_ks),
                "source": source,
                "pair_id": pair_id,
                "method": kaks_row.get("Method", ""),
            }
        )

    status = "available" if pair_rows else "missing_input"
    note = "ok" if pair_rows else "No non-empty KaKs results were available"
    write_tsv(pair_rows, outputs["pairs"], PAIR_FIELDS)
    write_tsv(skipped_rows, outputs["skipped"], SKIPPED_FIELDS)
    write_tsv(
        [
            {
                "status": status,
                "input_count": str(len(results)),
                "available_count": str(len(pair_rows)),
                "skipped_count": str(len(skipped_rows)),
                "note": note,
            }
        ],
        outputs["summary"],
        SUMMARY_FIELDS,
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calculator-results", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    normalize_reference_kaks_results(results=read_tsv(args.calculator_results), outdir=args.outdir)


if __name__ == "__main__":
    main()
