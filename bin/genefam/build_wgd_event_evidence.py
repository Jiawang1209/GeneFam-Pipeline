#!/usr/bin/env python3
"""Build a layer-level WGD event evidence table."""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


FIELDNAMES = [
    "wgd_layer",
    "pair_count",
    "ks_min",
    "ks_median",
    "ks_max",
    "event_name",
    "interpretation_status",
    "evidence_source",
    "species_scope",
    "expected_relative_age",
]

EVENT_METADATA_REQUIRED_FIELDS = ("name", "scope", "evidence", "expected_relative_age")


def build_event_evidence(
    rows: list[dict[str, str]],
    event_metadata: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    by_layer: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_layer[row["wgd_layer"]].append(row)

    evidence_rows: list[dict[str, str]] = []
    for layer in sorted(by_layer):
        layer_rows = by_layer[layer]
        ks_values = sorted(float(row["ks"]) for row in layer_rows)
        event_names = sorted({row.get("event_name", "unannotated") or "unannotated" for row in layer_rows})
        event_name = event_names[0] if len(event_names) == 1 else "mixed"
        metadata = event_metadata.get(event_name, {})
        if event_name not in {"unannotated", "mixed"} and not metadata:
            raise ValueError(f"No metadata configured for WGD event: {event_name}")
        is_named = event_name not in {"unannotated", "mixed"} and bool(metadata)
        evidence_rows.append(
            {
                "wgd_layer": layer,
                "pair_count": str(len(layer_rows)),
                "ks_min": f"{min(ks_values):.4f}",
                "ks_median": f"{statistics.median(ks_values):.4f}",
                "ks_max": f"{max(ks_values):.4f}",
                "event_name": event_name,
                "interpretation_status": "configured_named_event" if is_named else "inferred_layer_only",
                "evidence_source": metadata.get("evidence", "") if is_named else "",
                "species_scope": metadata.get("scope", "") if is_named else "",
                "expected_relative_age": metadata.get("expected_relative_age", "") if is_named else "",
            }
        )
    return evidence_rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def load_event_metadata(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to read WGD event configuration")
    with Path(path).open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle) or {}
    events = data.get("wgd_events", []) or []
    if not isinstance(events, list):
        raise ValueError("wgd_events must be a list")
    metadata: dict[str, dict[str, str]] = {}
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            raise ValueError(f"WGD event entry {index} must be a mapping")
        name = event.get("name")
        for field in EVENT_METADATA_REQUIRED_FIELDS:
            if not event.get(field):
                if field == "name":
                    raise ValueError(f"WGD event entry {index} is missing required field: name")
                raise ValueError(f"WGD event {name} is missing required field: {field}")
        if name in metadata:
            raise ValueError(f"Duplicate WGD event name: {name}")
        metadata[name] = event
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classified-pairs", required=True, type=Path)
    parser.add_argument("--events-config", default=None, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        build_event_evidence(read_tsv(args.classified_pairs), load_event_metadata(args.events_config)),
        args.out,
    )


if __name__ == "__main__":
    main()
