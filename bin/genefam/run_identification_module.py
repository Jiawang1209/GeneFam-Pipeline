#!/usr/bin/env python3
"""Run 04_identification from two-pass HMM and BLASTP evidence."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.preprocess_species import read_fasta_records, write_fasta


FAMILY_FIELDS = [
    "species_id",
    "gene_id",
    "evidence_sources",
    "hmm_evalue",
    "hmm_bitscore",
    "blastp_evalue",
    "blastp_bitscore",
    "best_reference_hit",
]
SUMMARY_FIELDS = [
    "final_rule",
    "hmm_candidate_count",
    "blastp_candidate_count",
    "intersection_count",
    "union_count",
    "selected_candidate_count",
    "domain_method",
    "domain_confirmed_count",
    "final_count",
    "domain_status",
    "note",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_ids(ids: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{item}\n" for item in ids), encoding="utf-8")


def load_project_config(path: Path | None) -> dict:
    if path is None:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to read project.yaml")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Project config must be a mapping: {path}")
    return data


def config_path(value: str | Path | None, config_dir: Path) -> Path | None:
    if value is None or value == "":
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return config_dir / path


def first_hmm_profile(hmm_dir: Path) -> Path:
    profiles = sorted(hmm_dir.glob("*.hmm"))
    if not profiles:
        raise ValueError(f"No HMM profiles found in {hmm_dir}")
    return profiles[0]


def resolve_args(args: argparse.Namespace) -> dict:
    config = load_project_config(args.config)
    config_dir = args.config.parent if args.config else Path.cwd()
    project_config = config.get("project", {}) or {}
    database_config = config.get("database", {}) or {}
    hmm_config = config.get("hmm", {}) or {}
    identification_config = config.get("identification", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    clean_bank = args.clean_bank or config_path(database_config.get("species_clean_bank"), config_dir)
    if clean_bank is None:
        clean_bank = project_outdir / "01_preprocess/species_clean_bank"
    hmm_candidates = args.hmm_candidates or project_outdir / "02_hmm/tables/hmm_candidates.tsv"
    blastp_candidates = args.blastp_candidates or project_outdir / "03_blastp/tables/blastp_candidates.tsv"
    hmm_profile = args.hmm_profile
    if hmm_profile is None:
        hmm_dir = config_path(hmm_config.get("hmm_dir"), config_dir)
        if hmm_dir is None:
            raise ValueError("HMM profile is required; provide --hmm-profile or hmm.hmm_dir")
        hmm_profile = first_hmm_profile(hmm_dir)
    domain_terms = args.domain_terms or [str(term) for term in (identification_config.get("domain_terms", []) or [])]
    if not domain_terms:
        domain_terms = [hmm_profile.stem]
    return {
        "clean_bank": clean_bank,
        "hmm_candidates": hmm_candidates,
        "blastp_candidates": blastp_candidates,
        "hmm_profile": hmm_profile,
        "domain_terms": domain_terms,
        "domain_evalue": args.domain_evalue if args.domain_evalue is not None else float(identification_config.get("domain_evalue", 1e-5)),
        "domain_method": args.domain_method or identification_config.get("domain_method", "hmmsearch"),
        "pfam_scan_dir": args.pfam_scan_dir or config_path(identification_config.get("pfam_scan_dir"), config_dir),
        "pfam_scan_executable": args.pfam_scan_executable or identification_config.get("pfam_scan_executable", "pfam_scan.pl"),
        "final_rule": args.final_rule or identification_config.get("final_rule", "intersection"),
        "outdir": args.outdir or config_path(identification_config.get("outdir"), config_dir) or project_outdir / "04_identification",
    }


def key(row: dict[str, str]) -> tuple[str, str]:
    return row["species_id"], row["gene_id"]


def build_family_rows(hmm_rows: list[dict[str, str]], blastp_rows: list[dict[str, str]], final_rule: str) -> tuple[list[dict[str, str]], set[tuple[str, str]], set[tuple[str, str]]]:
    if final_rule not in {"intersection", "union", "hmm_only"}:
        raise ValueError("final_rule must be intersection, union, or hmm_only")
    hmm_by_key = {key(row): row for row in hmm_rows}
    blastp_by_key = {key(row): row for row in blastp_rows}
    hmm_keys = set(hmm_by_key)
    blastp_keys = set(blastp_by_key)
    if final_rule == "intersection":
        selected_keys = sorted(hmm_keys & blastp_keys)
    elif final_rule == "hmm_only":
        selected_keys = sorted(hmm_keys)
    else:
        selected_keys = sorted(hmm_keys | blastp_keys)
    rows: list[dict[str, str]] = []
    for species_id, gene_id in selected_keys:
        hmm = hmm_by_key.get((species_id, gene_id), {})
        blastp = blastp_by_key.get((species_id, gene_id), {})
        sources = []
        if blastp:
            sources.append("blastp")
        if hmm:
            sources.append("hmm")
        rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "evidence_sources": ",".join(sources),
                "hmm_evalue": hmm.get("best_evalue", ""),
                "hmm_bitscore": hmm.get("best_bitscore", ""),
                "blastp_evalue": blastp.get("best_evalue", ""),
                "blastp_bitscore": blastp.get("best_bitscore", ""),
                "best_reference_hit": blastp.get("best_subject_id", ""),
            }
        )
    return rows, hmm_keys & blastp_keys, hmm_keys | blastp_keys


def discover_species_peptides(clean_bank: Path) -> dict[str, Path]:
    if not clean_bank.exists():
        raise ValueError(f"Clean bank does not exist: {clean_bank}")
    paths: dict[str, Path] = {}
    for species_dir in sorted(path for path in clean_bank.iterdir() if path.is_dir()):
        matches = sorted((species_dir / "clean").glob("*.protein.clean.fa"))
        if matches:
            paths[species_dir.name] = matches[0]
    if not paths:
        raise ValueError(f"No clean protein FASTA files found in {clean_bank}")
    return paths


def extract_records(rows: list[dict[str, str]], species_peptides: dict[str, Path], out_path: Path) -> int:
    wanted_by_species: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        wanted_by_species[row["species_id"]].add(row["gene_id"])
    records: list[tuple[str, str]] = []
    for species_id, wanted in sorted(wanted_by_species.items()):
        pep = species_peptides.get(species_id)
        if not pep:
            continue
        for record_id, sequence in read_fasta_records(pep):
            clean_id = record_id.split()[0]
            if clean_id in wanted:
                records.append((f"{species_id}|{clean_id}", sequence))
    write_fasta(records, out_path)
    return len(records)


def ensure_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Required command not found: {command}")


def run_domain_hmmsearch(hmm_profile: Path, fasta: Path, outdir: Path) -> Path:
    ensure_command("hmmsearch")
    domtblout = outdir / "domain_confirmation/domain_confirmation.domtblout"
    hmmout = outdir / "domain_confirmation/domain_confirmation.hmmout"
    domtblout.parent.mkdir(parents=True, exist_ok=True)
    with hmmout.open("w", encoding="utf-8") as stdout:
        subprocess.run(["hmmsearch", "--domtblout", str(domtblout), str(hmm_profile), str(fasta)], check=True, stdout=stdout, stderr=subprocess.PIPE, text=True)
    return domtblout


def run_domain_pfam_scan(executable: str, fasta: Path, pfam_scan_dir: Path, outdir: Path) -> Path:
    ensure_command(executable)
    pfam_out = outdir / "domain_confirmation/Pfam_scan.out"
    pfam_log = outdir / "domain_confirmation/Pfam_scan.log"
    pfam_out.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "-fasta", str(fasta), "-dir", str(pfam_scan_dir), "-cpu", "1", "-out", str(pfam_out)]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pfam_log.write_text("$ " + " ".join(command) + "\n\n" + completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"{executable} exited with status {completed.returncode}")
    return pfam_out


def parse_domain_confirmed(domtblout: Path, domain_terms: list[str], max_evalue: float) -> set[tuple[str, str]]:
    terms = {term.casefold() for term in domain_terms}
    confirmed: set[tuple[str, str]] = set()
    with domtblout.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 7:
                continue
            target, query_name, query_accession, evalue = fields[0], fields[3], fields[4], fields[6]
            try:
                parsed_evalue = float(evalue)
            except ValueError:
                continue
            if parsed_evalue > max_evalue:
                continue
            searchable = {query_name.casefold(), query_accession.casefold()}
            if terms and not any(term in item for term in terms for item in searchable):
                continue
            if "|" in target:
                species_id, gene_id = target.split("|", 1)
                confirmed.add((species_id, gene_id))
    return confirmed


def parse_pfam_scan_confirmed(path: Path, domain_terms: list[str]) -> set[tuple[str, str]]:
    terms = {term.casefold() for term in domain_terms}
    confirmed: set[tuple[str, str]] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 2:
                continue
            searchable = {field.casefold() for field in fields[1:]}
            if terms and not any(term in item for term in terms for item in searchable):
                continue
            query_id = fields[0]
            if "|" in query_id:
                species_id, gene_id = query_id.split("|", 1)
                confirmed.add((species_id, gene_id))
    return confirmed


def write_summary(outdir: Path, summary_row: dict[str, str]) -> None:
    write_tsv([summary_row], outdir / "report/identification_summary.tsv", SUMMARY_FIELDS)
    lines = [
        "# 04_identification Summary",
        "",
        f"- HMM candidates: {summary_row['hmm_candidate_count']}",
        f"- BLASTP candidates: {summary_row['blastp_candidate_count']}",
        f"- HMM and BLASTP intersection: {summary_row['intersection_count']}",
        f"- Domain-confirmed final members: {summary_row['final_count']}",
        f"- Domain status: {summary_row['domain_status']}",
    ]
    (outdir / "report/identification_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_module(**kwargs) -> Path:
    outdir: Path = kwargs["outdir"]
    hmm_rows = read_tsv(kwargs["hmm_candidates"])
    blastp_rows = read_tsv(kwargs["blastp_candidates"])
    family_rows, intersection_keys, union_keys = build_family_rows(hmm_rows, blastp_rows, kwargs["final_rule"])
    write_tsv(family_rows, outdir / "tables/family_candidates.tsv", FAMILY_FIELDS)
    write_ids(sorted({gene_id for _species_id, gene_id in intersection_keys}), outdir / "tables/inter.ID")
    write_ids(sorted({gene_id for _species_id, gene_id in union_keys}), outdir / "tables/union.ID")

    species_peptides = discover_species_peptides(kwargs["clean_bank"])
    selected_count = extract_records(family_rows, species_peptides, outdir / "fasta/inter.ID.fa")
    domain_status = "available"
    note = "Domain confirmation completed"
    domain_method = kwargs["domain_method"]
    if domain_method == "hmmsearch":
        domtblout = run_domain_hmmsearch(kwargs["hmm_profile"], outdir / "fasta/inter.ID.fa", outdir)
        confirmed_keys = parse_domain_confirmed(domtblout, kwargs["domain_terms"], kwargs["domain_evalue"])
    elif domain_method == "pfam_scan":
        pfam_scan_dir = kwargs["pfam_scan_dir"]
        if pfam_scan_dir is None:
            raise ValueError("pfam_scan domain confirmation requires --pfam-scan-dir or identification.pfam_scan_dir")
        pfam_out = run_domain_pfam_scan(kwargs["pfam_scan_executable"], outdir / "fasta/inter.ID.fa", Path(pfam_scan_dir), outdir)
        confirmed_keys = parse_pfam_scan_confirmed(pfam_out, kwargs["domain_terms"])
    else:
        raise ValueError("domain_method must be hmmsearch or pfam_scan")
    confirmed_rows = [row for row in family_rows if (row["species_id"], row["gene_id"]) in confirmed_keys]
    if not confirmed_rows:
        domain_status = "empty"
        note = "No candidates passed domain confirmation"
    write_ids(sorted({row["gene_id"] for row in confirmed_rows}), outdir / "tables/domain_confirmed.id")
    extract_records(confirmed_rows, species_peptides, outdir / "fasta/identify.ID.fa")
    write_summary(
        outdir,
        {
            "final_rule": kwargs["final_rule"],
            "hmm_candidate_count": str(len({key(row) for row in hmm_rows})),
            "blastp_candidate_count": str(len({key(row) for row in blastp_rows})),
            "intersection_count": str(len(intersection_keys)),
            "union_count": str(len(union_keys)),
            "selected_candidate_count": str(selected_count),
            "domain_method": domain_method,
            "domain_confirmed_count": str(len(confirmed_rows)),
            "final_count": str(len(confirmed_rows)),
            "domain_status": domain_status,
            "note": note,
        },
    )
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--clean-bank", default=None, type=Path)
    parser.add_argument("--hmm-candidates", default=None, type=Path)
    parser.add_argument("--blastp-candidates", default=None, type=Path)
    parser.add_argument("--hmm-profile", default=None, type=Path)
    parser.add_argument("--domain-terms", nargs="+", default=None)
    parser.add_argument("--domain-evalue", default=None, type=float)
    parser.add_argument("--domain-method", default=None, choices=["hmmsearch", "pfam_scan"])
    parser.add_argument("--pfam-scan-dir", default=None, type=Path)
    parser.add_argument("--pfam-scan-executable", default=None)
    parser.add_argument("--final-rule", default=None, choices=["intersection", "union", "hmm_only"])
    parser.add_argument("--outdir", default=None, type=Path)
    args = parser.parse_args()
    try:
        outdir = run_module(**resolve_args(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"04_identification completed at {outdir.resolve()}")


if __name__ == "__main__":
    main()
