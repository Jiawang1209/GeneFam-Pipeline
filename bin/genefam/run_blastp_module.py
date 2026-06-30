#!/usr/bin/env python3
"""Run the 03_blastp module using reusable domain annotations and clean-bank peptides."""

from __future__ import annotations

import argparse
import csv
import re
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


REFERENCE_SOURCE_FIELDS = ["species_id", "domain_annotation"]
SEED_MANIFEST_FIELDS = ["species_id", "domain_annotation", "seed_ids", "seed_peptides", "seed_count", "missing_ids", "missing_count"]
REFERENCE_MANIFEST_FIELDS = ["species_id", "domain_annotation", "reference_ids", "reference_peptides", "reference_count", "missing_ids", "missing_count"]
SPECIES_PEPTIDE_FIELDS = ["species_id", "pep"]
BLAST_FIELDS = ["qseqid", "sseqid", "pident", "length", "mismatch", "gapopen", "qstart", "qend", "sstart", "send", "evalue", "bitscore"]
CANDIDATE_FIELDS = [
    "species_id",
    "gene_id",
    "best_subject_id",
    "best_reference_species",
    "best_evalue",
    "best_bitscore",
    "matched_subject_count",
]
SUMMARY_FIELDS = ["species_id", "candidate_count", "status", "note"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def resolve_args(args: argparse.Namespace) -> dict:
    config = load_project_config(args.config)
    config_dir = args.config.parent if args.config else Path.cwd()
    project_config = config.get("project", {}) or {}
    database_config = config.get("database", {}) or {}
    blastp_config = config.get("blastp", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    clean_bank = args.clean_bank or config_path(database_config.get("species_clean_bank"), config_dir)
    if clean_bank is None:
        clean_bank = Path("results/species_clean_bank")
    reference_sources = args.reference_sources or config_path(blastp_config.get("reference_sources"), config_dir)
    if reference_sources is None:
        raise ValueError("BLASTP reference sources are required; provide --reference-sources or blastp.reference_sources")
    domain_terms = args.domain_terms or [str(term) for term in (blastp_config.get("domain_terms", []) or [])]
    if not domain_terms:
        raise ValueError("At least one domain term is required; provide --domain-terms or blastp.domain_terms")
    return {
        "clean_bank": clean_bank,
        "reference_sources": reference_sources,
        "domain_terms": domain_terms,
        "outdir": args.outdir or config_path(blastp_config.get("outdir"), config_dir) or project_outdir / "03_blastp",
        "evalue": args.evalue if args.evalue is not None else float(blastp_config.get("evalue", 1e-10)),
        "num_threads": args.num_threads if args.num_threads is not None else int(blastp_config.get("num_threads", 1)),
        "num_alignments": args.num_alignments if args.num_alignments is not None else int(blastp_config.get("num_alignments", 10)),
    }


def ensure_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Required command not found: {command}")


def normalize_model_id(value: str) -> str:
    model = value.strip().split()[0].split("|", 1)[0]
    return re.sub(r"\.\d+[A-Za-z]*$", "", model)


def domain_ids_for_terms(path: Path, terms: list[str]) -> list[str]:
    normalized_terms = [term.casefold() for term in terms if term.strip()]
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            row = line.split("\t")
            if not row or row[0].casefold() in {"model", "protein_id"}:
                continue
            searchable = "\t".join(row).casefold()
            if any(term in searchable for term in normalized_terms):
                ids.add(normalize_model_id(row[0]))
    if not ids:
        raise ValueError(f"No domain annotation rows matched {','.join(terms)} in {path}")
    return sorted(ids)


def discover_species_peptides(clean_bank: Path) -> list[dict[str, str]]:
    if not clean_bank.exists():
        raise ValueError(f"Clean bank does not exist: {clean_bank}")
    rows: list[dict[str, str]] = []
    for species_dir in sorted(path for path in clean_bank.iterdir() if path.is_dir()):
        matches = sorted((species_dir / "clean").glob("*.protein.clean.fa"))
        if matches:
            rows.append({"species_id": species_dir.name, "pep": str(matches[0])})
    if not rows:
        raise ValueError(f"No clean protein FASTA files found in {clean_bank}")
    return rows


def species_peptide_path(species_peptides: list[dict[str, str]], species_id: str) -> Path:
    for row in species_peptides:
        if row["species_id"] == species_id:
            return Path(row["pep"])
    raise ValueError(f"Reference species not found in clean bank: {species_id}")


def select_reference_records(species_id: str, peptides: Path, wanted_ids: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    wanted = set(wanted_ids)
    selected: list[tuple[str, str]] = []
    matched: set[str] = set()
    for record_id, sequence in read_fasta_records(peptides):
        clean_id = normalize_model_id(record_id)
        if clean_id in wanted:
            selected.append((f"{species_id}|{clean_id}", sequence))
            matched.add(clean_id)
    return selected, sorted(wanted - matched)


def write_ids(ids: list[str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{item}\n" for item in ids), encoding="utf-8")


def build_reference_package(reference_sources: Path, species_peptides: list[dict[str, str]], terms: list[str], outdir: Path) -> tuple[Path, list[dict[str, str]]]:
    source_rows = read_tsv(reference_sources)
    if not source_rows:
        raise ValueError(f"No reference source rows found: {reference_sources}")
    seed_manifest_rows: list[dict[str, str]] = []
    reference_manifest_rows: list[dict[str, str]] = []
    combined_records: list[tuple[str, str]] = []
    seed_dir = outdir / "seed"
    reference_dir = outdir / "reference"
    for source in source_rows:
        species_id = source["species_id"]
        domain_annotation = Path(source["domain_annotation"])
        ids = domain_ids_for_terms(domain_annotation, terms)
        records, missing = select_reference_records(species_id, species_peptide_path(species_peptides, species_id), ids)
        species_seed = seed_dir / f"{species_id}.seed.pep.fa"
        seed_ids_out = seed_dir / f"{species_id}.seed.ids.txt"
        seed_missing_out = seed_dir / f"{species_id}.seed.missing_ids.txt"
        species_ref = reference_dir / f"{species_id}.reference.pep.fa"
        reference_ids_out = reference_dir / f"{species_id}.reference.ids.txt"
        reference_missing_out = reference_dir / f"{species_id}.reference.missing_ids.txt"
        write_fasta(records, species_seed)
        write_ids(ids, seed_ids_out)
        write_ids(missing, seed_missing_out)
        write_fasta(records, species_ref)
        write_ids(ids, reference_ids_out)
        write_ids(missing, reference_missing_out)
        combined_records.extend(records)
        seed_manifest_rows.append(
            {
                "species_id": species_id,
                "domain_annotation": str(domain_annotation),
                "seed_ids": str(seed_ids_out),
                "seed_peptides": str(species_seed),
                "seed_count": str(len(records)),
                "missing_ids": str(seed_missing_out),
                "missing_count": str(len(missing)),
            }
        )
        reference_manifest_rows.append(
            {
                "species_id": species_id,
                "domain_annotation": str(domain_annotation),
                "reference_ids": str(reference_ids_out),
                "reference_peptides": str(species_ref),
                "reference_count": str(len(records)),
                "missing_ids": str(reference_missing_out),
                "missing_count": str(len(missing)),
            }
        )
    if not combined_records:
        raise ValueError("No reference peptide records were selected")
    combined_seed_fasta = seed_dir / "combined_seed.pep.fa"
    write_fasta(combined_records, combined_seed_fasta)
    write_tsv(seed_manifest_rows, seed_dir / "seed_manifest.tsv", SEED_MANIFEST_FIELDS)
    write_fasta(combined_records, reference_dir / "blastp_reference.pep.fa")
    write_tsv(reference_manifest_rows, reference_dir / "reference_manifest.tsv", REFERENCE_MANIFEST_FIELDS)
    return combined_seed_fasta, seed_manifest_rows


def run_makeblastdb(reference_fasta: Path, db_prefix: Path) -> None:
    db_prefix.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["makeblastdb", "-in", str(reference_fasta), "-dbtype", "prot", "-out", str(db_prefix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def run_blastp(species_id: str, query: Path, db_prefix: Path, outdir: Path, evalue: float, threads: int, num_alignments: int) -> Path:
    out = outdir / "raw" / f"{species_id}.blastp.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "blastp",
            "-query",
            str(query),
            "-db",
            str(db_prefix),
            "-out",
            str(out),
            "-evalue",
            str(evalue),
            "-num_threads",
            str(threads),
            "-num_alignments",
            str(num_alignments),
            "-outfmt",
            "6 " + " ".join(BLAST_FIELDS),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return out


def read_blast_rows(path: Path, species_id: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            values = line.split("\t")
            if len(values) < len(BLAST_FIELDS):
                continue
            row = dict(zip(BLAST_FIELDS, values))
            row["species_id"] = species_id
            rows.append(row)
    return rows


def _float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except ValueError:
        return default


def best_candidate_rows(blast_rows: list[dict[str, str]], max_evalue: float) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in blast_rows:
        if _float(row["evalue"], float("inf")) <= max_evalue:
            grouped[(row["species_id"], row["qseqid"])].append(row)
    candidates: list[dict[str, str]] = []
    for (species_id, gene_id), hits in sorted(grouped.items()):
        best = sorted(hits, key=lambda row: (-_float(row["bitscore"]), _float(row["evalue"], float("inf")), row["sseqid"]))[0]
        ref_species = best["sseqid"].split("|", 1)[0] if "|" in best["sseqid"] else ""
        candidates.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "best_subject_id": best["sseqid"],
                "best_reference_species": ref_species,
                "best_evalue": best["evalue"],
                "best_bitscore": best["bitscore"],
                "matched_subject_count": str(len({hit["sseqid"] for hit in hits})),
            }
        )
    return candidates


def write_summary(candidates: list[dict[str, str]], species_peptides: list[dict[str, str]], outdir: Path) -> None:
    counts: dict[str, int] = defaultdict(int)
    for row in candidates:
        counts[row["species_id"]] += 1
    rows = [
        {
            "species_id": species["species_id"],
            "candidate_count": str(counts.get(species["species_id"], 0)),
            "status": "available" if counts.get(species["species_id"], 0) else "empty",
            "note": "BLASTP candidates selected" if counts.get(species["species_id"], 0) else "No BLASTP candidates selected",
        }
        for species in species_peptides
    ]
    write_tsv(rows, outdir / "report/blastp_summary.tsv", SUMMARY_FIELDS)
    lines = ["# 03_blastp Summary", "", "| species_id | candidate_count | status |", "| --- | ---: | --- |"]
    for row in rows:
        lines.append(f"| {row['species_id']} | {row['candidate_count']} | {row['status']} |")
    (outdir / "report/blastp_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_module(**kwargs) -> Path:
    clean_bank: Path = kwargs["clean_bank"]
    reference_sources: Path = kwargs["reference_sources"]
    outdir: Path = kwargs["outdir"]
    ensure_command("makeblastdb")
    ensure_command("blastp")
    species_peptides = discover_species_peptides(clean_bank)
    write_tsv(species_peptides, outdir / "inputs/species_peptides.tsv", SPECIES_PEPTIDE_FIELDS)
    write_tsv(read_tsv(reference_sources), outdir / "inputs/reference_sources.tsv", REFERENCE_SOURCE_FIELDS)
    reference_fasta, _manifest = build_reference_package(reference_sources, species_peptides, kwargs["domain_terms"], outdir)
    db_prefix = outdir / "database/blastp_reference"
    run_makeblastdb(reference_fasta, db_prefix)
    all_rows: list[dict[str, str]] = []
    for species in species_peptides:
        blast_out = run_blastp(species["species_id"], Path(species["pep"]), db_prefix, outdir, kwargs["evalue"], kwargs["num_threads"], kwargs["num_alignments"])
        all_rows.extend(read_blast_rows(blast_out, species["species_id"]))
    raw_fields = ["species_id"] + BLAST_FIELDS
    write_tsv(all_rows, outdir / "tables/blastp_hits.raw.tsv", raw_fields)
    filtered = [row for row in all_rows if _float(row["evalue"], float("inf")) <= kwargs["evalue"]]
    write_tsv(filtered, outdir / "tables/blastp_hits.filtered.tsv", raw_fields)
    candidates = best_candidate_rows(all_rows, kwargs["evalue"])
    write_tsv(candidates, outdir / "tables/blastp_candidates.tsv", CANDIDATE_FIELDS)
    (outdir / "tables/blastp_candidate_ids.txt").write_text("".join(f"{row['species_id']}\t{row['gene_id']}\n" for row in candidates), encoding="utf-8")
    write_summary(candidates, species_peptides, outdir)
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--clean-bank", default=None, type=Path)
    parser.add_argument("--reference-sources", default=None, type=Path)
    parser.add_argument("--domain-terms", nargs="+", default=None)
    parser.add_argument("--outdir", default=None, type=Path)
    parser.add_argument("--evalue", default=None, type=float)
    parser.add_argument("--num-threads", default=None, type=int)
    parser.add_argument("--num-alignments", default=None, type=int)
    args = parser.parse_args()
    try:
        outdir = run_module(**resolve_args(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"03_blastp completed at {outdir.resolve()}")


if __name__ == "__main__":
    main()
