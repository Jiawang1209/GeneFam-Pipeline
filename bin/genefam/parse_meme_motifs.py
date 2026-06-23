#!/usr/bin/env python3
"""Parse MEME text output into a motif summary table."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


FIELDNAMES = ["family_name", "motif_id", "motif_name", "width", "sites", "evalue"]
MATRIX_RE = re.compile(r"w=\s*(?P<width>\d+)\s+nsites=\s*(?P<sites>\d+)\s+E=\s*(?P<evalue>\S+)")


def parse_meme_text(path: Path, family_name: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    pending_motif: dict[str, str] | None = None

    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("MOTIF "):
                if pending_motif is not None:
                    raise ValueError(f"Missing letter-probability matrix for motif {pending_motif['motif_id']}")
                parts = line.split(maxsplit=2)
                motif_id = parts[1]
                motif_name = parts[2] if len(parts) > 2 else motif_id
                pending_motif = {"motif_id": motif_id, "motif_name": motif_name}
                continue
            if pending_motif and line.startswith("letter-probability matrix:"):
                match = MATRIX_RE.search(line)
                if not match:
                    raise ValueError(f"Could not parse motif matrix metadata for motif {pending_motif['motif_id']}")
                rows.append(
                    {
                        "family_name": family_name,
                        "motif_id": pending_motif["motif_id"],
                        "motif_name": pending_motif["motif_name"],
                        "width": match.group("width"),
                        "sites": match.group("sites"),
                        "evalue": match.group("evalue"),
                    }
                )
                pending_motif = None

    if pending_motif is not None:
        raise ValueError(f"Missing letter-probability matrix for motif {pending_motif['motif_id']}")
    return rows


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meme-txt", required=True, type=Path)
    parser.add_argument("--family-name", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    write_tsv(parse_meme_text(args.meme_txt, args.family_name), args.out)


if __name__ == "__main__":
    main()
