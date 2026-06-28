#!/usr/bin/env python3
"""Run or plan KaKs_Calculator jobs from Reference-style Ka/Ks input manifests."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


STATUS_FIELDS = ["status", "pair_count", "succeeded_count", "failed_count", "note"]
COMMAND_FIELDS = ["pair_id", "command"]
RESULT_FIELDS = ["pair_id", "source", "kaks_result", "status", "note"]
FAILURE_SUMMARY_FIELDS = [
    "source",
    "calculator_status",
    "calculator_note",
    "qc_flags",
    "pair_count",
    "example_pair_ids",
    "interpretation",
]
QC_FIELDS = [
    "pair_id",
    "source",
    "cds_fasta",
    "sequence_count",
    "gene_a",
    "gene_b",
    "gene_a_length",
    "gene_a_mod3",
    "gene_a_terminal_stop",
    "gene_a_internal_stop_count",
    "gene_a_ambiguous_base_count",
    "gene_b_length",
    "gene_b_mod3",
    "gene_b_terminal_stop",
    "gene_b_internal_stop_count",
    "gene_b_ambiguous_base_count",
    "length_delta",
    "qc_flags",
    "calculator_status",
    "calculator_note",
]
STOP_CODONS = {"TAA", "TAG", "TGA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _command(executable: str, cds_fasta: str, out_path: Path) -> str:
    return f"{executable} -i {cds_fasta} -o {out_path}"


def _write_status(out_path: Path, status: str, pair_count: int, succeeded_count: int, failed_count: int, note: str) -> None:
    write_tsv(
        [
            {
                "status": status,
                "pair_count": str(pair_count),
                "succeeded_count": str(succeeded_count),
                "failed_count": str(failed_count),
                "note": note,
            }
        ],
        out_path,
        STATUS_FIELDS,
    )


def read_fasta(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    name = ""
    parts: list[str] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(">"):
            if name:
                records.append((name, "".join(parts).upper()))
            name = line[1:].split()[0]
            parts = []
        else:
            parts.append(line.strip())
    if name:
        records.append((name, "".join(parts).upper()))
    return records


def _sequence_qc(sequence: str) -> dict[str, str]:
    codons = [sequence[i : i + 3] for i in range(0, len(sequence) - 2, 3)]
    terminal_stop = bool(codons and codons[-1] in STOP_CODONS)
    internal_stop_count = sum(1 for codon in codons[:-1] if codon in STOP_CODONS)
    ambiguous_count = sum(1 for base in sequence if base not in {"A", "C", "G", "T"})
    return {
        "length": str(len(sequence)),
        "mod3": str(len(sequence) % 3),
        "terminal_stop": str(terminal_stop),
        "internal_stop_count": str(internal_stop_count),
        "ambiguous_base_count": str(ambiguous_count),
    }


def build_pair_qc(row: dict[str, str], status: str = "", note: str = "") -> dict[str, str]:
    cds_fasta = row.get("cds_fasta", "")
    records = read_fasta(Path(cds_fasta))
    first = records[0] if len(records) > 0 else ("", "")
    second = records[1] if len(records) > 1 else ("", "")
    first_qc = _sequence_qc(first[1])
    second_qc = _sequence_qc(second[1])
    flags: list[str] = []
    if len(records) != 2:
        flags.append("not_two_sequences")
    if first_qc["mod3"] != "0" or second_qc["mod3"] != "0":
        flags.append("length_not_multiple_of_3")
    if first_qc["internal_stop_count"] != "0" or second_qc["internal_stop_count"] != "0":
        flags.append("internal_stop")
    if first_qc["ambiguous_base_count"] != "0" or second_qc["ambiguous_base_count"] != "0":
        flags.append("ambiguous_base")
    length_delta = abs(len(first[1]) - len(second[1])) if len(records) >= 2 else 0
    if length_delta:
        flags.append("length_mismatch")
    if first_qc["terminal_stop"] == "True" or second_qc["terminal_stop"] == "True":
        flags.append("terminal_stop")
    return {
        "pair_id": row.get("pair_id", ""),
        "source": row.get("source", ""),
        "cds_fasta": cds_fasta,
        "sequence_count": str(len(records)),
        "gene_a": first[0],
        "gene_b": second[0],
        "gene_a_length": first_qc["length"],
        "gene_a_mod3": first_qc["mod3"],
        "gene_a_terminal_stop": first_qc["terminal_stop"],
        "gene_a_internal_stop_count": first_qc["internal_stop_count"],
        "gene_a_ambiguous_base_count": first_qc["ambiguous_base_count"],
        "gene_b_length": second_qc["length"],
        "gene_b_mod3": second_qc["mod3"],
        "gene_b_terminal_stop": second_qc["terminal_stop"],
        "gene_b_internal_stop_count": second_qc["internal_stop_count"],
        "gene_b_ambiguous_base_count": second_qc["ambiguous_base_count"],
        "length_delta": str(length_delta),
        "qc_flags": ",".join(flags) if flags else "clean_basic_qc",
        "calculator_status": status,
        "calculator_note": note,
    }


def _interpret_failure(status: str, note: str, qc_flags: str) -> str:
    if status == "missing_dependency" or status == "missing_input":
        return "Ka/Ks was not calculated because the required executable or input was unavailable."
    if note == "empty KaKs output":
        if qc_flags and qc_flags != "clean_basic_qc":
            if "terminal_stop" in qc_flags:
                return "KaKs_Calculator finished without a usable result file; CDS QC flags suggest checking terminal stop codons before rerunning."
            return "KaKs_Calculator finished without a usable result file; CDS QC flags suggest checking sequence length, stop codons, ambiguous bases, or pair alignment before rerunning."
        return "KaKs_Calculator finished without a usable result file; inspect the pair CDS alignment and calculator log/output."
    if status == "planned":
        return "Ka/Ks command was planned but not executed in this run."
    return "Ka/Ks did not produce an available result; inspect the pair CDS FASTA and calculator output."


def build_failure_summary(qc_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str], list[str]] = {}
    for row in qc_rows:
        status = row.get("calculator_status", "")
        if not status or status == "available":
            continue
        key = (
            row.get("source", ""),
            status,
            row.get("calculator_note", ""),
            row.get("qc_flags", ""),
        )
        grouped.setdefault(key, []).append(row.get("pair_id", ""))

    summary_rows: list[dict[str, str]] = []
    for source, status, note, qc_flags in sorted(grouped):
        pair_ids = [pair_id for pair_id in grouped[(source, status, note, qc_flags)] if pair_id]
        summary_rows.append(
            {
                "source": source,
                "calculator_status": status,
                "calculator_note": note,
                "qc_flags": qc_flags,
                "pair_count": str(len(pair_ids)),
                "example_pair_ids": ",".join(pair_ids[:5]),
                "interpretation": _interpret_failure(status, note, qc_flags),
            }
        )
    return summary_rows


def plan_or_run_kaks(
    *,
    manifest: list[dict[str, str]],
    outdir: Path,
    executable: str = "KaKs_Calculator",
    run: bool = True,
) -> dict[str, Path]:
    outdir = Path(outdir)
    results_dir = outdir / "kaks_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "status": outdir / "kaks_calculator_status.tsv",
        "commands": outdir / "kaks_calculator_commands.tsv",
        "results": outdir / "kaks_calculator_results.tsv",
        "qc": outdir / "kaks_calculator_qc.tsv",
        "failure_summary": outdir / "kaks_failure_summary.tsv",
    }

    command_rows: list[dict[str, str]] = []
    result_rows: list[dict[str, str]] = []
    qc_rows: list[dict[str, str]] = []
    for row in manifest:
        pair_id = row.get("pair_id", "").strip()
        if not pair_id:
            continue
        out_path = results_dir / f"{pair_id}.kaks.tsv"
        command_rows.append({"pair_id": pair_id, "command": _command(executable, row.get("cds_fasta", ""), out_path)})

    if not command_rows:
        write_tsv(command_rows, outputs["commands"], COMMAND_FIELDS)
        write_tsv(result_rows, outputs["results"], RESULT_FIELDS)
        write_tsv(qc_rows, outputs["qc"], QC_FIELDS)
        write_tsv(build_failure_summary(qc_rows), outputs["failure_summary"], FAILURE_SUMMARY_FIELDS)
        _write_status(outputs["status"], "missing_input", 0, 0, 0, "No Ka/Ks input pairs were prepared")
        return outputs

    executable_path = shutil.which(executable)
    if not executable_path:
        qc_rows = [build_pair_qc(row, "missing_dependency", f"KaKs executable not found: {executable}") for row in manifest if row.get("pair_id", "").strip()]
        write_tsv(command_rows, outputs["commands"], COMMAND_FIELDS)
        write_tsv(result_rows, outputs["results"], RESULT_FIELDS)
        write_tsv(qc_rows, outputs["qc"], QC_FIELDS)
        write_tsv(build_failure_summary(qc_rows), outputs["failure_summary"], FAILURE_SUMMARY_FIELDS)
        _write_status(outputs["status"], "missing_dependency", len(command_rows), 0, 0, f"KaKs executable not found: {executable}")
        return outputs

    succeeded = 0
    failed = 0
    for row, command_row in zip(manifest, command_rows, strict=False):
        pair_id = command_row["pair_id"]
        out_path = results_dir / f"{pair_id}.kaks.tsv"
        if not run:
            result_rows.append({"pair_id": pair_id, "source": row.get("source", ""), "kaks_result": str(out_path), "status": "planned", "note": "run disabled"})
            qc_rows.append(build_pair_qc(row, "planned", "run disabled"))
            continue
        completed = subprocess.run(
            [executable_path, "-i", row.get("cds_fasta", ""), "-o", str(out_path)],
            check=False,
            text=True,
            capture_output=True,
        )
        if completed.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
            status = "available"
            note = "ok"
            succeeded += 1
        else:
            status = "failed"
            if completed.returncode == 0 and out_path.exists() and out_path.stat().st_size == 0:
                note = "empty KaKs output"
            else:
                note = (completed.stderr or completed.stdout or f"exit {completed.returncode}").strip().replace("\n", " ")[:500]
            failed += 1
        result_rows.append({"pair_id": pair_id, "source": row.get("source", ""), "kaks_result": str(out_path), "status": status, "note": note})
        qc_rows.append(build_pair_qc(row, status, note))

    write_tsv(command_rows, outputs["commands"], COMMAND_FIELDS)
    write_tsv(result_rows, outputs["results"], RESULT_FIELDS)
    write_tsv(qc_rows, outputs["qc"], QC_FIELDS)
    write_tsv(build_failure_summary(qc_rows), outputs["failure_summary"], FAILURE_SUMMARY_FIELDS)
    overall_status = "available" if succeeded and failed == 0 else "partial" if succeeded else "failed"
    _write_status(outputs["status"], overall_status, len(command_rows), succeeded, failed, "ok" if failed == 0 else "Some Ka/Ks jobs failed")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--executable", default="KaKs_Calculator")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    plan_or_run_kaks(
        manifest=read_tsv(args.manifest),
        outdir=args.outdir,
        executable=args.executable,
        run=not args.plan_only,
    )


if __name__ == "__main__":
    main()
