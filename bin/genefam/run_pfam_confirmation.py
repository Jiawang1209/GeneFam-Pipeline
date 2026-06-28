#!/usr/bin/env python3
"""Run or record Reference Step4 Pfam confirmation outputs."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


STATUS_FIELDS = ["status", "hmm_id", "candidate_count", "confirmed_count", "note"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id = ""
    aliases_by_id: dict[str, list[str]] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                raw_id = line[1:].split()[0]
                current_id = raw_id
                aliases = [current_id]
                if "|" in raw_id:
                    aliases.append(raw_id.split("|")[-1])
                aliases_by_id[current_id] = sorted(set(aliases))
                records[current_id] = []
            elif current_id:
                records[current_id].append(line)
    indexed: dict[str, str] = {}
    for record_id, parts in records.items():
        sequence = "".join(parts)
        for alias in aliases_by_id.get(record_id, [record_id]):
            indexed[alias] = sequence
    return indexed


def write_id_list(ids: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(f"{gene_id}\n" for gene_id in ids)
    path.write_text(text, encoding="utf-8")


def write_fasta(records: dict[str, str], ids: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for gene_id in ids:
            sequence = records.get(gene_id)
            if not sequence:
                continue
            handle.write(f">{gene_id}\n")
            for start in range(0, len(sequence), 60):
                handle.write(sequence[start : start + 60] + "\n")


def write_status(path: Path, *, status: str, hmm_id: str, candidate_count: int, confirmed_count: int, note: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATUS_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerow(
            {
                "status": status,
                "hmm_id": hmm_id,
                "candidate_count": str(candidate_count),
                "confirmed_count": str(confirmed_count),
                "note": note,
            }
        )


def candidate_ids(rows: list[dict[str, str]]) -> list[str]:
    ids = sorted({row.get("gene_id", "").strip() for row in rows if row.get("gene_id", "").strip()})
    return ids


def intersection_ids(rows: list[dict[str, str]]) -> list[str]:
    selected = []
    for row in rows:
        sources = {item.strip() for item in row.get("evidence_sources", "").split(",") if item.strip()}
        gene_id = row.get("gene_id", "").strip()
        if gene_id and {"hmmer", "diamond"}.issubset(sources):
            selected.append(gene_id)
    return sorted(set(selected))


def _hmm_matches_hmm_id(target_name: str, accession: str, hmm_id: str) -> bool:
    return target_name == hmm_id or accession == hmm_id or accession.startswith(f"{hmm_id}.")


def parse_hmmscan_domtblout(path: Path, hmm_id: str) -> list[str]:
    confirmed: set[str] = set()
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 4:
                continue
            target_name, accession, query_name = fields[0], fields[1], fields[3]
            if _hmm_matches_hmm_id(target_name, accession, hmm_id):
                confirmed.add(query_name.split("|", 1)[0])
    return sorted(confirmed)


def run_hmmscan(*, executable: str, pfam_db: Path, family_members: Path, domtblout: Path, log_path: Path) -> tuple[int, str]:
    command = [executable, "--domtblout", str(domtblout), str(pfam_db), str(family_members)]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log_path.write_text("$ " + " ".join(command) + "\n\n" + completed.stdout, encoding="utf-8")
    return completed.returncode, completed.stdout


def run_pfam_confirmation(
    *,
    family_candidates: Path,
    family_members: Path,
    hmm_id: str,
    pfam_db: Path | None,
    hmmscan_domtbl: Path | None,
    outdir: Path,
    executable: str,
) -> dict[str, Path]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    candidates = read_tsv(family_candidates)
    records = read_fasta(family_members)
    union = candidate_ids(candidates)
    inter = intersection_ids(candidates)
    outputs = {
        "inter_ids": outdir / "inter.ID",
        "union_ids": outdir / "union.ID",
        "pfam_ids": outdir / "pfam.ID",
        "pfam_scan_ids": outdir / "pfam_scan.id",
        "identify_fasta": outdir / "identify.ID.fa",
        "status": outdir / "pfam_confirmation_status.tsv",
        "domtblout": outdir / "pfam_scan.domtblout",
        "log": outdir / "pfam_scan.log",
    }
    write_id_list(inter, outputs["inter_ids"])
    write_id_list(union, outputs["union_ids"])

    confirmed: list[str] = []
    status = "missing_input"
    note = "No Pfam HMM database or precomputed hmmscan domtblout was provided"
    domtbl_to_parse = hmmscan_domtbl
    if hmmscan_domtbl and Path(hmmscan_domtbl).exists():
        domtbl_to_parse = Path(hmmscan_domtbl)
        status = "available"
        note = "Pfam confirmation completed"
    elif pfam_db and Path(pfam_db).exists():
        if not shutil.which(executable):
            status = "missing_dependency"
            note = f"{executable} is not available in PATH"
        else:
            returncode, _ = run_hmmscan(
                executable=executable,
                pfam_db=Path(pfam_db),
                family_members=family_members,
                domtblout=outputs["domtblout"],
                log_path=outputs["log"],
            )
            if returncode == 0:
                domtbl_to_parse = outputs["domtblout"]
                status = "available"
                note = "Pfam confirmation completed"
            else:
                status = "failed"
                note = f"{executable} exited with status {returncode}"

    if status == "available" and domtbl_to_parse:
        confirmed = [gene_id for gene_id in parse_hmmscan_domtblout(Path(domtbl_to_parse), hmm_id) if gene_id in set(union)]

    write_id_list(confirmed, outputs["pfam_ids"])
    write_id_list(confirmed, outputs["pfam_scan_ids"])
    write_fasta(records, confirmed or union, outputs["identify_fasta"])
    write_status(
        outputs["status"],
        status=status,
        hmm_id=hmm_id,
        candidate_count=len(union),
        confirmed_count=len(confirmed),
        note=note,
    )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--family-members", required=True, type=Path)
    parser.add_argument("--hmm-id", required=True)
    parser.add_argument("--pfam-db", default=None, type=Path)
    parser.add_argument("--hmmscan-domtbl", default=None, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--executable", default="hmmscan")
    args = parser.parse_args()
    run_pfam_confirmation(
        family_candidates=args.family_candidates,
        family_members=args.family_members,
        hmm_id=args.hmm_id,
        pfam_db=args.pfam_db,
        hmmscan_domtbl=args.hmmscan_domtbl,
        outdir=args.outdir,
        executable=args.executable,
    )


if __name__ == "__main__":
    main()
