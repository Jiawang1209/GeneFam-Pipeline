#!/usr/bin/env python3
"""Run the 02_hmm module for HMM-only candidate protein screening."""

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
except ImportError:  # pragma: no cover - minimal installs
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.filter_hmmer_domains import filter_domains
from bin.genefam.parse_hmmer_domtbl import FIELDNAMES as HMMER_FIELDS
from bin.genefam.parse_hmmer_domtbl import parse_domtblout
from bin.genefam.preprocess_species import read_fasta_records, write_fasta


HMM_PROFILE_FIELDS = ["hmm_id", "hmm_profile"]
SPECIES_PEPTIDE_FIELDS = ["species_id", "pep"]
CANDIDATE_FIELDS = [
    "species_id",
    "gene_id",
    "matched_hmm_count",
    "required_hmm_count",
    "matched_hmm_ids",
    "combine_rule",
    "best_evalue",
    "best_bitscore",
]
SUMMARY_FIELDS = [
    "species_id",
    "candidate_count",
    "hmm_profile_count",
    "combine_rule",
    "status",
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
    hmm_config = config.get("hmm", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    clean_bank = args.clean_bank or config_path(database_config.get("species_clean_bank"), config_dir) or Path("results/species_clean_bank")
    hmm_dir = args.hmm_dir or config_path(hmm_config.get("hmm_dir"), config_dir)
    if hmm_dir is None:
        raise ValueError("HMM directory is required; provide --hmm-dir or hmm.hmm_dir in project.yaml")
    outdir = args.outdir or config_path(hmm_config.get("outdir"), config_dir) or project_outdir / "02_hmm"
    return {
        "clean_bank": clean_bank,
        "hmm_dir": hmm_dir,
        "outdir": outdir,
        "combine_rule": args.combine_rule or hmm_config.get("combine_rule", "any"),
        "max_evalue": args.evalue if args.evalue is not None else float(hmm_config.get("evalue", 1e-10)),
        "min_bitscore": args.min_bitscore if args.min_bitscore is not None else float(hmm_config.get("min_bitscore", 0.0)),
        "min_domain_coverage": args.min_domain_coverage
        if args.min_domain_coverage is not None
        else float(hmm_config.get("min_domain_coverage", 0.0)),
        "rebuild_hmm": args.rebuild_hmm if args.rebuild_hmm else bool(hmm_config.get("rebuild_hmm", False)),
        "family_name": args.family_name or hmm_config.get("family_name", project_config.get("name", "family")),
    }


def discover_hmm_profiles(hmm_dir: Path) -> list[dict[str, str]]:
    if not hmm_dir.exists():
        raise ValueError(f"HMM directory does not exist: {hmm_dir}")
    if not hmm_dir.is_dir():
        raise ValueError(f"HMM path is not a directory: {hmm_dir}")
    profiles = [
        {"hmm_id": path.stem, "hmm_profile": str(path)}
        for path in sorted(hmm_dir.glob("*.hmm"))
        if path.is_file()
    ]
    if not profiles:
        raise ValueError(f"No .hmm profiles found in {hmm_dir}")
    return profiles


def discover_species_peptides(clean_bank: Path) -> list[dict[str, str]]:
    if not clean_bank.exists():
        raise ValueError(f"Clean bank does not exist: {clean_bank}")
    rows: list[dict[str, str]] = []
    for species_dir in sorted(path for path in clean_bank.iterdir() if path.is_dir()):
        species_id = species_dir.name
        matches = sorted((species_dir / "clean").glob("*.protein.clean.fa"))
        if not matches:
            continue
        rows.append({"species_id": species_id, "pep": str(matches[0])})
    if not rows:
        raise ValueError(f"No clean protein FASTA files found in {clean_bank}")
    return rows


def ensure_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Required command not found: {command}")


def run_hmmsearch(species_id: str, pep: Path, hmm_id: str, hmm_profile: Path, outdir: Path) -> tuple[Path, Path]:
    domtblout = outdir / "raw" / f"{species_id}.{hmm_id}.domtblout"
    hmmout = outdir / "raw" / f"{species_id}.{hmm_id}.hmmout"
    domtblout.parent.mkdir(parents=True, exist_ok=True)
    with hmmout.open("w", encoding="utf-8") as stdout:
        subprocess.run(
            ["hmmsearch", "--domtblout", str(domtblout), str(hmm_profile), str(pep)],
            check=True,
            stdout=stdout,
            stderr=subprocess.PIPE,
            text=True,
        )
    return domtblout, hmmout


def _float_or_inf(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float("inf")


def _float_or_zero(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0


def candidate_rows(
    filtered_rows: list[dict[str, str]],
    hmm_ids: list[str],
    combine_rule: str,
) -> list[dict[str, str]]:
    by_species_gene: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    required_count = len(set(hmm_ids))
    for row in filtered_rows:
        by_species_gene[(row["species_id"], row["gene_id"])].append(row)

    rows: list[dict[str, str]] = []
    for (species_id, gene_id), hits in sorted(by_species_gene.items()):
        matched_hmms = sorted({hit["hmm_id"] for hit in hits})
        if combine_rule == "all" and len(matched_hmms) < required_count:
            continue
        best_evalue = min(_float_or_inf(hit["evalue"]) for hit in hits)
        best_bitscore = max(_float_or_zero(hit["bitscore"]) for hit in hits)
        rows.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "matched_hmm_count": str(len(matched_hmms)),
                "required_hmm_count": str(required_count),
                "matched_hmm_ids": ",".join(matched_hmms),
                "combine_rule": combine_rule,
                "best_evalue": f"{best_evalue:.3g}",
                "best_bitscore": f"{best_bitscore:.1f}",
            }
        )
    return rows


def write_candidate_fasta(candidates: list[dict[str, str]], species_peptides: list[dict[str, str]], out_path: Path) -> None:
    candidate_ids_by_species: dict[str, set[str]] = defaultdict(set)
    for row in candidates:
        candidate_ids_by_species[row["species_id"]].add(row["gene_id"])
    records: list[tuple[str, str]] = []
    for species in species_peptides:
        species_id = species["species_id"]
        wanted = candidate_ids_by_species.get(species_id, set())
        if not wanted:
            continue
        for record_id, sequence in read_fasta_records(Path(species["pep"])):
            clean_id = record_id.split()[0]
            if clean_id in wanted:
                records.append((f"{species_id}|{clean_id}", sequence))
    write_fasta(records, out_path)


def extract_hit_fasta(filtered_rows: list[dict[str, str]], species_peptides: list[dict[str, str]], out_path: Path) -> int:
    hit_ids_by_species: dict[str, set[str]] = defaultdict(set)
    for row in filtered_rows:
        hit_ids_by_species[row["species_id"]].add(row["gene_id"])
    records: list[tuple[str, str]] = []
    for species in species_peptides:
        species_id = species["species_id"]
        wanted = hit_ids_by_species.get(species_id, set())
        if not wanted:
            continue
        for record_id, sequence in read_fasta_records(Path(species["pep"])):
            clean_id = record_id.split()[0]
            if clean_id in wanted:
                records.append((f"{species_id}|{clean_id}", sequence))
    write_fasta(records, out_path)
    return len(records)


def run_mafft(input_fasta: Path, output_alignment: Path) -> None:
    output_alignment.parent.mkdir(parents=True, exist_ok=True)
    with output_alignment.open("w", encoding="utf-8") as stdout:
        subprocess.run(["mafft", "--auto", str(input_fasta)], check=True, stdout=stdout, stderr=subprocess.PIPE, text=True)


def run_hmmbuild(hmm_out: Path, alignment: Path, log_out: Path) -> None:
    hmm_out.parent.mkdir(parents=True, exist_ok=True)
    with log_out.open("w", encoding="utf-8") as stdout:
        subprocess.run(["hmmbuild", str(hmm_out), str(alignment)], check=True, stdout=stdout, stderr=subprocess.PIPE, text=True)


def write_summary(candidates: list[dict[str, str]], species_peptides: list[dict[str, str]], hmm_count: int, combine_rule: str, outdir: Path) -> None:
    counts: dict[str, int] = defaultdict(int)
    for row in candidates:
        counts[row["species_id"]] += 1
    rows = [
        {
            "species_id": species["species_id"],
            "candidate_count": str(counts.get(species["species_id"], 0)),
            "hmm_profile_count": str(hmm_count),
            "combine_rule": combine_rule,
            "status": "available",
            "note": "HMM candidates selected",
        }
        for species in species_peptides
    ]
    write_tsv(rows, outdir / "report/hmm_summary.tsv", SUMMARY_FIELDS)
    lines = [
        "# 02_hmm Summary",
        "",
        f"HMM profiles: {hmm_count}",
        f"Combine rule: {combine_rule}",
        f"Total candidates: {len(candidates)}",
        "",
        "| species_id | candidate_count |",
        "| --- | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['species_id']} | {row['candidate_count']} |")
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/hmm_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_hmm_module(
    *,
    clean_bank: Path,
    hmm_dir: Path,
    outdir: Path,
    combine_rule: str,
    max_evalue: float,
    min_bitscore: float,
    min_domain_coverage: float,
    rebuild_hmm: bool = False,
    family_name: str = "family",
) -> None:
    ensure_command("hmmsearch")
    if rebuild_hmm:
        ensure_command("mafft")
        ensure_command("hmmbuild")
    hmm_profiles = discover_hmm_profiles(hmm_dir)
    species_peptides = discover_species_peptides(clean_bank)
    write_tsv(hmm_profiles, outdir / "inputs/hmm_profiles.tsv", HMM_PROFILE_FIELDS)
    write_tsv(species_peptides, outdir / "inputs/species_peptides.tsv", SPECIES_PEPTIDE_FIELDS)

    raw_rows: list[dict[str, str]] = []
    filtered_rows: list[dict[str, str]] = []
    for species in species_peptides:
        for profile in hmm_profiles:
            domtblout, _hmmout = run_hmmsearch(
                species["species_id"],
                Path(species["pep"]),
                profile["hmm_id"],
                Path(profile["hmm_profile"]),
                outdir,
            )
            parsed = parse_domtblout(domtblout, species["species_id"])
            raw_rows.extend(parsed)
            filtered = filter_domains(parsed, max_evalue, min_bitscore, min_domain_coverage)
            filtered_rows.extend(filtered)
            write_tsv(parsed, outdir / "tables/per_search" / f"{species['species_id']}.{profile['hmm_id']}.raw.tsv", HMMER_FIELDS)
            write_tsv(filtered, outdir / "tables/per_search" / f"{species['species_id']}.{profile['hmm_id']}.filtered.tsv", HMMER_FIELDS)

    candidate_source_rows = filtered_rows
    candidate_hmm_ids = [profile["hmm_id"] for profile in hmm_profiles]
    if rebuild_hmm:
        rebuilt_dir = outdir / "rebuilt_hmm"
        first_pass_hits = rebuilt_dir / "first_pass_hits.pep.fa"
        hit_count = extract_hit_fasta(filtered_rows, species_peptides, first_pass_hits)
        if hit_count < 2:
            raise RuntimeError(f"Need at least two first-pass HMM hits to rebuild HMM; got {hit_count}")
        alignment = rebuilt_dir / "first_pass_hits.aln.fa"
        rebuilt_hmm = rebuilt_dir / f"{family_name}.rebuilt.hmm"
        run_mafft(first_pass_hits, alignment)
        run_hmmbuild(rebuilt_hmm, alignment, rebuilt_dir / "hmmbuild.log")
        rebuilt_profile = {"hmm_id": f"{family_name}_rebuilt", "hmm_profile": str(rebuilt_hmm)}
        rebuilt_rows: list[dict[str, str]] = []
        for species in species_peptides:
            domtblout, _hmmout = run_hmmsearch(
                species["species_id"],
                Path(species["pep"]),
                rebuilt_profile["hmm_id"],
                Path(rebuilt_profile["hmm_profile"]),
                outdir,
            )
            parsed = parse_domtblout(domtblout, species["species_id"])
            filtered = filter_domains(parsed, max_evalue, min_bitscore, min_domain_coverage)
            rebuilt_rows.extend(filtered)
            write_tsv(parsed, outdir / "tables/per_search" / f"{species['species_id']}.{rebuilt_profile['hmm_id']}.raw.tsv", HMMER_FIELDS)
            write_tsv(filtered, outdir / "tables/per_search" / f"{species['species_id']}.{rebuilt_profile['hmm_id']}.filtered.tsv", HMMER_FIELDS)
        candidate_source_rows = rebuilt_rows
        candidate_hmm_ids = [rebuilt_profile["hmm_id"]]

    candidates = candidate_rows(candidate_source_rows, candidate_hmm_ids, combine_rule if not rebuild_hmm else "any")
    write_tsv(raw_rows, outdir / "tables/hmm_hits.raw.tsv", HMMER_FIELDS)
    write_tsv(filtered_rows, outdir / "tables/hmm_hits.filtered.tsv", HMMER_FIELDS)
    write_tsv(candidates, outdir / "tables/hmm_candidates.tsv", CANDIDATE_FIELDS)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)
    (outdir / "tables/hmm_candidate_ids.txt").write_text(
        "\n".join(row["gene_id"] for row in candidates) + ("\n" if candidates else ""),
        encoding="utf-8",
    )
    write_candidate_fasta(candidates, species_peptides, outdir / "fasta/hmm_candidates.pep.fa")
    write_summary(candidates, species_peptides, len(hmm_profiles), combine_rule, outdir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--clean-bank", default=None, type=Path)
    parser.add_argument("--hmm-dir", default=None, type=Path)
    parser.add_argument("--outdir", default=None, type=Path)
    parser.add_argument("--combine-rule", choices=["any", "all"], default=None)
    parser.add_argument("--evalue", default=None, type=float)
    parser.add_argument("--min-bitscore", default=None, type=float)
    parser.add_argument("--min-domain-coverage", default=None, type=float)
    parser.add_argument("--rebuild-hmm", action="store_true")
    parser.add_argument("--family-name", default=None)
    args = parser.parse_args()
    try:
        resolved = resolve_args(args)
        run_hmm_module(
            clean_bank=resolved["clean_bank"],
            hmm_dir=resolved["hmm_dir"],
            outdir=resolved["outdir"],
            combine_rule=resolved["combine_rule"],
            max_evalue=resolved["max_evalue"],
            min_bitscore=resolved["min_bitscore"],
            min_domain_coverage=resolved["min_domain_coverage"],
            rebuild_hmm=resolved["rebuild_hmm"],
            family_name=resolved["family_name"],
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"02_hmm completed at {resolved['outdir']}")


if __name__ == "__main__":
    main()
