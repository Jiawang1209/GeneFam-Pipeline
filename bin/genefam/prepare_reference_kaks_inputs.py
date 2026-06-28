#!/usr/bin/env python3
"""Prepare Reference-style Ka/Ks CDS and peptide inputs from gene-pair tables."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


GENE_PAIR_FIELDS = ["pair_id", "source", "species_a", "species_b", "gene_a", "gene_b", "pair_type"]
STATUS_FIELDS = ["source", "status", "pair_count", "prepared_count", "missing_count", "note"]
MISSING_FIELDS = ["source", "species_a", "species_b", "gene_a", "gene_b", "missing"]
MANIFEST_FIELDS = ["pair_id", "source", "cds_fasta", "pep_fasta", "expected_kaks", "kaks_command"]
STOP_CODONS = {"TAA", "TAG", "TGA"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with Path(out_path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id: str | None = None
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0].split("|", 1)[0]
                records[current_id] = []
            elif current_id is None:
                raise ValueError(f"Sequence found before first FASTA header in {path}")
            else:
                records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def _first(row: dict[str, str], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key, "").strip()
        if value:
            return value
    return ""


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def normalize_cds_for_kaks(sequence: str) -> str:
    normalized = re.sub(r"\s+", "", sequence).upper().replace("U", "T")
    if len(normalized) >= 3 and normalized[-3:] in STOP_CODONS:
        return normalized[:-3]
    return normalized


def normalize_pep_for_kaks(sequence: str) -> str:
    normalized = re.sub(r"\s+", "", sequence)
    return normalized[:-1] if normalized.endswith("*") else normalized


def normalize_pair(source: str, row: dict[str, str]) -> dict[str, str] | None:
    species_a = _first(row, ("species_a", "query_species", "species_id"))
    species_b = _first(row, ("species_b", "subject_species", "species_id"))
    gene_a = _first(row, ("gene_a", "query_gene", "query_id", "gene_id_a"))
    gene_b = _first(row, ("gene_b", "subject_gene", "subject_id", "gene_id_b"))
    pair_type = _first(row, ("type", "pair_type", "duplicate_type")) or "syntenic"
    if not species_a or not species_b or not gene_a or not gene_b:
        return None
    pair_id = "__".join(_safe_id(part) for part in (source, species_a, gene_a, gene_b))
    return {
        "pair_id": pair_id,
        "source": source,
        "species_a": species_a,
        "species_b": species_b,
        "gene_a": gene_a,
        "gene_b": gene_b,
        "pair_type": pair_type,
    }


def _jcvi_pair_context(jcvi_dir: Path) -> dict[str, tuple[str, str]]:
    manifest = Path(jcvi_dir) / "jcvi_pair_manifest.tsv"
    if not manifest.exists():
        return {}
    context: dict[str, tuple[str, str]] = {}
    for row in read_tsv(manifest):
        pair_id = row.get("pair_id", "").strip()
        query_species = row.get("query_species", "").strip()
        subject_species = row.get("subject_species", "").strip()
        if pair_id and query_species and subject_species:
            context[pair_id] = (query_species, subject_species)
    return context


def _parse_jcvi_color2(path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            payload = line.split("*", 1)[1] if "*" in line else line
            fields = payload.split()
            if len(fields) >= 3:
                pairs.append((fields[0], fields[2]))
    return pairs


def _parse_jcvi_anchor_pairs(path: Path) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) >= 2:
                pairs.append((fields[0], fields[1]))
    return pairs


def read_jcvi_gene_pairs(jcvi_dir: Path) -> list[dict[str, str]]:
    """Read Reference Step8.1 gene pairs from JCVI color2 or anchors outputs."""
    jcvi_dir = Path(jcvi_dir)
    context = _jcvi_pair_context(jcvi_dir)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for pair_id, (query_species, subject_species) in sorted(context.items()):
        candidate_files = sorted(jcvi_dir.glob(f"{pair_id}*.color2"))
        if not candidate_files:
            candidate_files = [
                path
                for path in (
                    jcvi_dir / f"{pair_id}.anchors.simple",
                    jcvi_dir / f"{pair_id}.anchors.new",
                    jcvi_dir / f"{pair_id}.anchors",
                )
                if path.exists()
            ]
        for path in candidate_files:
            parser = _parse_jcvi_color2 if path.name.endswith(".color2") else _parse_jcvi_anchor_pairs
            for gene_a, gene_b in parser(path):
                key = (pair_id, gene_a, gene_b)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "query_species": query_species,
                        "subject_species": subject_species,
                        "query_gene": gene_a,
                        "subject_gene": gene_b,
                        "pair_type": "JCVI_collinear",
                    }
                )
    return rows


def load_species_sequences(species_manifest: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    loaded: dict[str, dict[str, dict[str, str]]] = {}
    for row in species_manifest:
        species_id = row.get("species_id", "").strip()
        pep = row.get("pep", "").strip()
        cds = row.get("cds", "").strip()
        if not species_id:
            continue
        loaded[species_id] = {
            "pep": read_fasta(Path(pep)) if pep else {},
            "cds": read_fasta(Path(cds)) if cds else {},
        }
    return loaded


def _missing_for_pair(pair: dict[str, str], sequences: dict[str, dict[str, dict[str, str]]]) -> list[str]:
    missing: list[str] = []
    for side in ("a", "b"):
        species = pair[f"species_{side}"]
        gene = pair[f"gene_{side}"]
        if gene not in sequences.get(species, {}).get("cds", {}):
            missing.append(f"{species}:{gene}:cds")
        if gene not in sequences.get(species, {}).get("pep", {}):
            missing.append(f"{species}:{gene}:pep")
    return missing


def _write_pair_fastas(
    pair: dict[str, str],
    sequences: dict[str, dict[str, dict[str, str]]],
    pair_fastas_dir: Path,
) -> tuple[Path, Path]:
    cds_path = pair_fastas_dir / f"{pair['pair_id']}.cds.fa"
    pep_path = pair_fastas_dir / f"{pair['pair_id']}.pep.fa"
    pair_fastas_dir.mkdir(parents=True, exist_ok=True)
    cds_a = normalize_cds_for_kaks(sequences[pair["species_a"]]["cds"][pair["gene_a"]])
    cds_b = normalize_cds_for_kaks(sequences[pair["species_b"]]["cds"][pair["gene_b"]])
    pep_a = normalize_pep_for_kaks(sequences[pair["species_a"]]["pep"][pair["gene_a"]])
    pep_b = normalize_pep_for_kaks(sequences[pair["species_b"]]["pep"][pair["gene_b"]])
    cds_path.write_text(
        f">{pair['gene_a']}\n{cds_a}\n"
        f">{pair['gene_b']}\n{cds_b}\n",
        encoding="utf-8",
    )
    pep_path.write_text(
        f">{pair['gene_a']}\n{pep_a}\n"
        f">{pair['gene_b']}\n{pep_b}\n",
        encoding="utf-8",
    )
    return cds_path, pep_path


def prepare_reference_kaks_inputs(
    *,
    species_manifest: list[dict[str, str]],
    pair_sources: list[tuple[str, list[dict[str, str]]]],
    outdir: Path,
) -> dict[str, Path]:
    outdir = Path(outdir)
    pair_fastas_dir = outdir / "pair_fastas"
    sequences = load_species_sequences(species_manifest)

    gene_pair_rows: list[dict[str, str]] = []
    status_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []
    manifest_rows: list[dict[str, str]] = []

    for source, rows in pair_sources:
        normalized = [pair for row in rows if (pair := normalize_pair(source, row))]
        prepared_count = 0
        source_missing = 0
        for pair in normalized:
            missing = _missing_for_pair(pair, sequences)
            if missing:
                source_missing += 1
                missing_rows.append({**pair, "missing": ",".join(missing)})
                continue
            cds_path, pep_path = _write_pair_fastas(pair, sequences, pair_fastas_dir)
            expected_kaks = outdir / "expected_kaks" / f"{pair['pair_id']}.kaks.tsv"
            manifest_rows.append(
                {
                    "pair_id": pair["pair_id"],
                    "source": source,
                    "cds_fasta": str(cds_path),
                    "pep_fasta": str(pep_path),
                    "expected_kaks": str(expected_kaks),
                    "kaks_command": f"KaKs_Calculator -i {cds_path} -o {expected_kaks}",
                }
            )
            gene_pair_rows.append(pair)
            prepared_count += 1
        status = "available" if normalized and source_missing == 0 else "missing_sequence" if source_missing else "missing_input"
        note = "ok" if status == "available" else "missing CDS/pep records for at least one pair" if source_missing else "no usable gene pairs"
        status_rows.append(
            {
                "source": source,
                "status": status,
                "pair_count": str(len(normalized)),
                "prepared_count": str(prepared_count),
                "missing_count": str(source_missing),
                "note": note,
            }
        )

    outputs = {
        "gene_pairs": outdir / "KaKs_Gene_Pair.tsv",
        "manifest": outdir / "kaks_input_manifest.tsv",
        "missing": outdir / "kaks_missing_sequences.tsv",
        "status": outdir / "kaks_input_status.tsv",
    }
    write_tsv(gene_pair_rows, outputs["gene_pairs"], GENE_PAIR_FIELDS)
    write_tsv(manifest_rows, outputs["manifest"], MANIFEST_FIELDS)
    write_tsv(missing_rows, outputs["missing"], MISSING_FIELDS)
    write_tsv(status_rows, outputs["status"], STATUS_FIELDS)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--pair-source", action="append", default=[], help="NAME=path/to/pairs.tsv")
    parser.add_argument("--jcvi-dir", action="append", default=[], type=Path, help="JCVI output directory with color2/anchors files")
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    pair_sources = []
    for value in args.pair_source:
        if "=" not in value:
            raise SystemExit(f"--pair-source must be NAME=PATH, got: {value}")
        name, path = value.split("=", 1)
        pair_sources.append((name, read_tsv(Path(path))))
    for jcvi_dir in args.jcvi_dir:
        pair_sources.append(("jcvi", read_jcvi_gene_pairs(jcvi_dir)))
    prepare_reference_kaks_inputs(
        species_manifest=read_tsv(args.species_manifest),
        pair_sources=pair_sources,
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
