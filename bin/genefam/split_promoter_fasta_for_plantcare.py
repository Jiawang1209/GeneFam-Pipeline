#!/usr/bin/env python3
"""Split promoter FASTA into PlantCARE submission parts."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


MANIFEST_FIELDS = ["part_id", "path", "record_count", "first_record_id", "last_record_id"]
STATUS_FIELDS = ["status", "total_records", "part_count", "records_per_file", "note"]


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, list[str]]] = []
    current_id = ""
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                records.append((current_id, []))
                continue
            if not current_id:
                raise ValueError(f"FASTA sequence before first header in {path}")
            records[-1][1].append(line)
    return [(record_id, "".join(parts)) for record_id, parts in records]


def write_fasta(records: list[tuple[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8") as handle:
        for record_id, sequence in records:
            handle.write(f">{record_id}\n")
            for start in range(0, len(sequence), 80):
                handle.write(sequence[start : start + 80] + "\n")


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _chunks(records: list[tuple[str, str]], size: int) -> list[list[tuple[str, str]]]:
    return [records[index : index + size] for index in range(0, len(records), size)]


def split_promoter_fasta(
    *,
    promoter_fasta: Path,
    outdir: Path,
    records_per_file: int,
    prefix: str,
) -> dict[str, Path]:
    if records_per_file < 1:
        raise ValueError("records_per_file must be >= 1")
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = outdir / "plantcare_submission_manifest.tsv"
    status = outdir / "plantcare_submission_status.tsv"
    records = read_fasta(promoter_fasta)
    manifest_rows: list[dict[str, str]] = []
    for index, chunk in enumerate(_chunks(records, records_per_file), start=1):
        part_id = f"{prefix}.part{index:03d}"
        part_path = outdir / f"{part_id}.fa"
        write_fasta(chunk, part_path)
        manifest_rows.append(
            {
                "part_id": part_id,
                "path": str(part_path),
                "record_count": str(len(chunk)),
                "first_record_id": chunk[0][0],
                "last_record_id": chunk[-1][0],
            }
        )
    write_tsv(manifest_rows, manifest, MANIFEST_FIELDS)
    status_value = "available" if records else "missing_input"
    note = (
        "PlantCARE submission FASTA parts prepared"
        if records
        else "No promoter FASTA records available for PlantCARE submission"
    )
    write_tsv(
        [
            {
                "status": status_value,
                "total_records": str(len(records)),
                "part_count": str(len(manifest_rows)),
                "records_per_file": str(records_per_file),
                "note": note,
            }
        ],
        status,
        STATUS_FIELDS,
    )
    return {"manifest": manifest, "status": status}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promoter-fasta", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--records-per-file", default=100, type=int)
    parser.add_argument("--prefix", default="promoters")
    args = parser.parse_args()
    split_promoter_fasta(
        promoter_fasta=args.promoter_fasta,
        outdir=args.outdir,
        records_per_file=args.records_per_file,
        prefix=args.prefix,
    )


if __name__ == "__main__":
    main()
