#!/usr/bin/env python3
"""Extract FASTA records by ID."""

from __future__ import annotations

import argparse
from pathlib import Path


def _read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id: str | None = None
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                records[current_id] = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                records[current_id].append(line)
    return {record_id: "".join(seq_parts) for record_id, seq_parts in records.items()}


def extract_fasta_records(path: Path, ids: set[str]) -> list[tuple[str, str]]:
    all_records = _read_fasta(path)
    missing = sorted(ids - set(all_records))
    if missing:
        raise ValueError(f"Missing sequence IDs: {', '.join(missing)}")
    return [(record_id, all_records[record_id]) for record_id in sorted(ids)]


def write_fasta(records: list[tuple[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for record_id, sequence in records:
            handle.write(f">{record_id}\n{sequence}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fasta", required=True, type=Path)
    parser.add_argument("--ids", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    ids = {line.strip() for line in args.ids.read_text(encoding="utf-8").splitlines() if line.strip()}
    write_fasta(extract_fasta_records(args.fasta, ids), args.out)


if __name__ == "__main__":
    main()
