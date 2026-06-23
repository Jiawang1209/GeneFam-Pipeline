#!/usr/bin/env python3
"""Build a plot manifest TSV for final report assembly."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["plot_key", "path", "description"]


def build_plot_manifest(plots: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    return [{"plot_key": key, "path": path, "description": description} for key, path, description in plots]


def parse_plot(value: str) -> tuple[str, str, str]:
    parts = value.split("=", 2)
    if len(parts) != 3:
        raise ValueError(f"Plot must be formatted as key=path=description: {value}")
    return parts[0], parts[1], parts[2]


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot", action="append", default=[], help="Plot entry formatted as key=path=description")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(build_plot_manifest([parse_plot(value) for value in args.plot]), args.out)


if __name__ == "__main__":
    main()
