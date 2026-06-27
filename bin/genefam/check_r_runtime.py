#!/usr/bin/env python3
"""Check that the configured R runtime can start before R plotting smoke tests."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path


FIELDNAMES = ["check", "status", "exit_code", "r_bin", "note"]


def _clean_note(text: str) -> str:
    return " | ".join(line.strip() for line in text.splitlines() if line.strip())


def check_r_runtime(r_bin: Path) -> dict[str, str]:
    command = [
        str(r_bin),
        "--vanilla",
        "--slave",
        "-e",
        "cat(R.version.string, '\\n'); cat('R runtime health OK\\n')",
    ]
    if not r_bin.exists():
        return {
            "check": "r_runtime",
            "status": "failed",
            "exit_code": "127",
            "r_bin": str(r_bin),
            "note": f"{r_bin} does not exist",
        }

    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output = _clean_note((completed.stdout or "") + "\n" + (completed.stderr or ""))
    return {
        "check": "r_runtime",
        "status": "passed" if completed.returncode == 0 else "failed",
        "exit_code": str(completed.returncode),
        "r_bin": str(r_bin),
        "note": output or "no output from R runtime probe",
    }


def write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerow(row)


def _escape(value: str) -> str:
    return value.replace("|", "\\|")


def write_markdown(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# R Runtime Health",
        "",
        f"Status: {row['status']}",
        f"Exit code: {row['exit_code']}",
        "",
        "| check | status | exit_code | r_bin | note |",
        "| --- | --- | --- | --- | --- |",
        "| "
        + " | ".join(_escape(row[field]) for field in FIELDNAMES)
        + " |",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-bin", type=Path, default=Path("/usr/local/bin/R"))
    parser.add_argument("--outdir", type=Path, default=Path("results/r_runtime_health"))
    args = parser.parse_args()

    row = check_r_runtime(args.r_bin)
    write_tsv(row, args.outdir / "r_runtime_health.tsv")
    write_markdown(row, args.outdir / "r_runtime_health.md")
    raise SystemExit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
