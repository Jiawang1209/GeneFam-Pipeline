#!/usr/bin/env python3
"""Write a stable key/value snapshot for a WGD/named-event run."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "value"]


def parse_event_args(event_args: str | list[str]) -> dict[str, str]:
    if isinstance(event_args, str):
        raw_parts = event_args.split()
    else:
        raw_parts = event_args
    mapping: dict[str, str] = {}
    index = 0
    while index < len(raw_parts):
        part = raw_parts[index]
        if part == "--event" and index + 1 < len(raw_parts):
            pair = raw_parts[index + 1]
            index += 2
        else:
            pair = part.removeprefix("--event=")
            index += 1
        if "=" not in pair:
            continue
        layer, event_name = pair.split("=", 1)
        if layer and event_name:
            mapping[layer] = event_name
    return mapping


def build_snapshot(
    *,
    events_config: str,
    ks_bins: str,
    event_args: str,
    duplicates: str,
    family_members: str,
    kaks_pairs: str,
) -> list[dict[str, str]]:
    rows = [
        {"key": "events_config", "value": events_config},
        {"key": "ks_bins", "value": ks_bins},
        {"key": "duplicates", "value": duplicates},
        {"key": "family_members", "value": family_members},
        {"key": "kaks_pairs", "value": kaks_pairs},
    ]
    for layer, event_name in sorted(parse_event_args(event_args).items()):
        rows.append({"key": f"event.{layer}", "value": event_name})
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events-config", required=True)
    parser.add_argument("--ks-bins", required=True)
    parser.add_argument("--event-args", default="")
    parser.add_argument("--duplicates", required=True)
    parser.add_argument("--family-members", required=True)
    parser.add_argument("--kaks-pairs", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(
        build_snapshot(
            events_config=args.events_config,
            ks_bins=args.ks_bins,
            event_args=args.event_args,
            duplicates=args.duplicates,
            family_members=args.family_members,
            kaks_pairs=args.kaks_pairs,
        ),
        args.out,
    )


if __name__ == "__main__":
    main()
