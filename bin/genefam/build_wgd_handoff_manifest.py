#!/usr/bin/env python3
"""Build the standard-to-WGD handoff manifest."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["item", "path", "status", "required_for", "description"]


def _status_for_optional_path(path: str, configured_status: str = "configured") -> str:
    return configured_status if path else "pending_user_preparation"


def build_handoff_manifest(
    family_candidates: str,
    duplicates: str = "",
    kaks_pairs: str = "",
    events_config: str = "",
    ks_bins: str = "",
    wgd_event_args: str = "",
) -> list[dict[str, str]]:
    return [
        {
            "item": "family_members",
            "path": family_candidates,
            "status": "available" if family_candidates else "missing",
            "required_for": "duplication_retention",
            "description": "Family candidate table produced by the standard identification branch",
        },
        {
            "item": "duplicate_types",
            "path": duplicates,
            "status": _status_for_optional_path(duplicates, "available"),
            "required_for": "duplication_retention",
            "description": "Prepared MCScanX or duplicate-classification table",
        },
        {
            "item": "kaks_pairs",
            "path": kaks_pairs,
            "status": _status_for_optional_path(kaks_pairs, "available"),
            "required_for": "wgd_layer_classification",
            "description": "Prepared Ka/Ks pair table with gene_a, gene_b, and ks columns",
        },
        {
            "item": "events_config",
            "path": events_config,
            "status": "configured" if events_config else "missing",
            "required_for": "named_wgd_events",
            "description": "YAML mapping for named WGD events such as gamma, beta, alpha, and theta",
        },
        {
            "item": "ks_bins",
            "path": ks_bins,
            "status": "configured" if ks_bins else "missing",
            "required_for": "wgd_layer_classification",
            "description": "Ks bin boundaries used to assign anonymous WGD layers",
        },
        {
            "item": "wgd_event_args",
            "path": wgd_event_args,
            "status": "configured" if wgd_event_args else "missing",
            "required_for": "named_wgd_events",
            "description": "Layer-to-event command arguments for gamma, beta, alpha, theta, or custom labels",
        },
    ]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True)
    parser.add_argument("--duplicates", default="")
    parser.add_argument("--kaks-pairs", default="")
    parser.add_argument("--events-config", default="")
    parser.add_argument("--ks-bins", default="")
    parser.add_argument("--wgd-event-args", default="")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        build_handoff_manifest(
            family_candidates=args.family_candidates,
            duplicates=args.duplicates,
            kaks_pairs=args.kaks_pairs,
            events_config=args.events_config,
            ks_bins=args.ks_bins,
            wgd_event_args=args.wgd_event_args,
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
