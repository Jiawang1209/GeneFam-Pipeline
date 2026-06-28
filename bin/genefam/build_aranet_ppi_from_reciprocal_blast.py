#!/usr/bin/env python3
"""Transfer Arabidopsis AraNet interactions through Reference-style reciprocal BLAST evidence."""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import defaultdict
from pathlib import Path


OUTFMT6_FIELDS = [
    "qseqid",
    "sseqid",
    "pident",
    "length",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "sstart",
    "send",
    "evalue",
    "bitscore",
    "qlen",
    "slen",
]
HOMOLOGY_FIELDS = [
    "species_id",
    "gene_id",
    "arabidopsis_gene_id",
    "forward_evalue",
    "forward_bitscore",
    "reciprocal_target",
    "reciprocal_evalue",
    "reciprocal_bitscore",
    "reciprocal_supported",
]
EDGE_FIELDS = ["source", "target", "weight", "species"]
NODE_FIELDS = ["node", "species", "type", "domain"]
EVIDENCE_FIELDS = ["metric", "value", "description"]
BLAST_MANIFEST_FIELDS = ["species_id", "family_to_arabidopsis", "arabidopsis_to_species"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path, fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def clean_gene_id(value: str) -> str:
    gene_id = value.strip().split()[0].split("|")[0]
    if "." in gene_id and gene_id.upper().startswith("AT"):
        gene_id = gene_id.rsplit(".", 1)[0]
    return gene_id


def read_fasta(path: Path) -> dict[str, str]:
    records: dict[str, list[str]] = {}
    current_id = ""
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                current_id = clean_gene_id(line[1:])
                records.setdefault(current_id, [])
            elif current_id:
                records[current_id].append(line)
    return {record_id: "".join(parts) for record_id, parts in records.items()}


def write_family_fasta(records: dict[str, str], gene_ids: list[str], out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w", encoding="utf-8") as handle:
        for gene_id in sorted(set(gene_ids)):
            sequence = records.get(gene_id)
            if not sequence:
                continue
            handle.write(f">{gene_id}\n")
            for start in range(0, len(sequence), 60):
                handle.write(sequence[start : start + 60] + "\n")
            written += 1
    return written


def read_aranet_edges(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if len(fields) < 2:
                continue
            if fields[0].lower() in {"source", "gene1", "from"}:
                continue
            rows.append(
                {
                    "source": clean_gene_id(fields[0]),
                    "target": clean_gene_id(fields[1]),
                    "weight": fields[2].strip() if len(fields) > 2 and fields[2].strip() else "1",
                }
            )
    return rows


def read_outfmt6(path: Path) -> list[dict[str, str]]:
    if not Path(path).exists():
        return []
    rows: list[dict[str, str]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        for fields in reader:
            if len(fields) < 12:
                continue
            padded = fields + [""] * (len(OUTFMT6_FIELDS) - len(fields))
            rows.append(dict(zip(OUTFMT6_FIELDS, padded)))
    return rows


def best_hits(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        query = clean_gene_id(row.get("qseqid", ""))
        subject = clean_gene_id(row.get("sseqid", ""))
        if not query or not subject:
            continue
        current = best.get(query)
        if current is None or float(row.get("bitscore") or 0) > float(current.get("bitscore") or 0):
            clean_row = dict(row)
            clean_row["qseqid"] = query
            clean_row["sseqid"] = subject
            best[query] = clean_row
    return best


def build_homology_rows(
    family_candidates: list[dict[str, str]],
    forward_hits_by_species: dict[str, list[dict[str, str]]],
    reverse_hits_by_species: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    candidates_by_species: dict[str, list[str]] = defaultdict(list)
    for row in family_candidates:
        species_id = row.get("species_id", "").strip()
        gene_id = clean_gene_id(row.get("gene_id", ""))
        if species_id and gene_id:
            candidates_by_species[species_id].append(gene_id)

    homology_rows: list[dict[str, str]] = []
    for species_id, gene_ids in sorted(candidates_by_species.items()):
        forward_best = best_hits(forward_hits_by_species.get(species_id, []))
        reverse_best = best_hits(reverse_hits_by_species.get(species_id, []))
        for gene_id in sorted(set(gene_ids)):
            forward = forward_best.get(gene_id)
            if not forward:
                continue
            ath_gene = clean_gene_id(forward.get("sseqid", ""))
            reciprocal = reverse_best.get(ath_gene, {})
            reciprocal_target = clean_gene_id(reciprocal.get("sseqid", ""))
            reciprocal_supported = reciprocal_target == gene_id
            homology_rows.append(
                {
                    "species_id": species_id,
                    "gene_id": gene_id,
                    "arabidopsis_gene_id": ath_gene,
                    "forward_evalue": forward.get("evalue", ""),
                    "forward_bitscore": forward.get("bitscore", ""),
                    "reciprocal_target": reciprocal_target,
                    "reciprocal_evalue": reciprocal.get("evalue", ""),
                    "reciprocal_bitscore": reciprocal.get("bitscore", ""),
                    "reciprocal_supported": "true" if reciprocal_supported else "false",
                }
            )
    return homology_rows


def _format_weight(value: str) -> str:
    try:
        return f"{float(value):.4f}"
    except ValueError:
        return "1.0000"


def transfer_aranet_edges(
    homology_rows: list[dict[str, str]],
    aranet_edges: list[dict[str, str]],
) -> dict[str, list[dict[str, str]]]:
    homolog_map: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    reciprocal_supported = 0
    for row in homology_rows:
        species_id = row["species_id"]
        gene_id = row["gene_id"]
        ath_gene = row["arabidopsis_gene_id"]
        if species_id and gene_id and ath_gene:
            homolog_map[species_id][ath_gene].append(gene_id)
        if row.get("reciprocal_supported") == "true":
            reciprocal_supported += 1

    transferred_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    aranet_edges_with_family_homologs = 0
    for aranet_edge in aranet_edges:
        ath_a = aranet_edge["source"]
        ath_b = aranet_edge["target"]
        edge_supported = False
        for species_id, by_ath_gene in sorted(homolog_map.items()):
            genes_a = sorted(set(by_ath_gene.get(ath_a, [])))
            genes_b = sorted(set(by_ath_gene.get(ath_b, [])))
            if not genes_a or not genes_b:
                continue
            edge_supported = True
            for gene_a in genes_a:
                for gene_b in genes_b:
                    if gene_a == gene_b:
                        continue
                    source, target = sorted([gene_a, gene_b])
                    key = (source, target, species_id)
                    if key in seen_edges:
                        continue
                    seen_edges.add(key)
                    transferred_edges.append(
                        {
                            "source": source,
                            "target": target,
                            "weight": _format_weight(aranet_edge.get("weight", "1")),
                            "species": species_id,
                        }
                    )
        if edge_supported:
            aranet_edges_with_family_homologs += 1

    nodes_by_key: dict[tuple[str, str], dict[str, str]] = {}
    for edge in transferred_edges:
        for node in (edge["source"], edge["target"]):
            nodes_by_key[(edge["species"], node)] = {
                "node": node,
                "species": edge["species"],
                "type": "GDSL",
                "domain": "PF00657",
            }

    metrics = {
        "homology_rows": len(homology_rows),
        "reciprocal_supported_homologs": reciprocal_supported,
        "aranet_edges_read": len(aranet_edges),
        "aranet_edges_with_family_homologs": aranet_edges_with_family_homologs,
        "transferred_edges": len(transferred_edges),
        "species_with_transferred_edges": len({edge["species"] for edge in transferred_edges}),
    }
    descriptions = {
        "homology_rows": "Family genes with a best Arabidopsis protein hit from family-to-Arabidopsis DIAMOND",
        "reciprocal_supported_homologs": "Homology rows where the Arabidopsis-to-species best hit returns to the same family gene",
        "aranet_edges_read": "AraNet Arabidopsis network edges read from the configured PPI file",
        "aranet_edges_with_family_homologs": "AraNet edges whose two Arabidopsis endpoints both have selected family homologs",
        "transferred_edges": "Species-level PPI edges transferred from AraNet through DIAMOND homology evidence",
        "species_with_transferred_edges": "Species with at least one transferred PPI edge",
    }
    return {
        "edges": sorted(transferred_edges, key=lambda row: (row["species"], row["source"], row["target"])),
        "nodes": [nodes_by_key[key] for key in sorted(nodes_by_key)],
        "evidence": [
            {"metric": metric, "value": str(value), "description": descriptions.get(metric, "")}
            for metric, value in metrics.items()
        ],
    }


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def run_diamond_pair(
    *,
    diamond: str,
    query: Path,
    db_fasta: Path,
    db_prefix: Path,
    out: Path,
    evalue: str,
    max_target_seqs: int,
    threads: int,
) -> None:
    run_command([diamond, "makedb", "--in", str(db_fasta), "--db", str(db_prefix), "--quiet"])
    run_command(
        [
            diamond,
            "blastp",
            "--query",
            str(query),
            "--db",
            str(db_prefix),
            "--out",
            str(out),
            "--outfmt",
            "6",
            *OUTFMT6_FIELDS,
            "--evalue",
            evalue,
            "--max-target-seqs",
            str(max_target_seqs),
            "--threads",
            str(threads),
            "--quiet",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-candidates", required=True, type=Path)
    parser.add_argument("--species-manifest", required=True, type=Path)
    parser.add_argument("--aranet", required=True, type=Path)
    parser.add_argument("--reference-species", default="Arabidopsis_thaliana")
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--workdir", default=Path("ppi_reciprocal_work"), type=Path)
    parser.add_argument("--diamond", default="diamond")
    parser.add_argument("--evalue", default="1e-10")
    parser.add_argument("--max-target-seqs", default=3, type=int)
    parser.add_argument("--threads", default=4, type=int)
    args = parser.parse_args()

    family_candidates = read_tsv(args.family_candidates)
    manifest_rows = read_tsv(args.species_manifest)
    pep_by_species = {row["species_id"]: Path(row["pep"]) for row in manifest_rows}
    reference_pep = pep_by_species.get(args.reference_species)
    if reference_pep is None:
        raise SystemExit(f"Reference species not found in species manifest: {args.reference_species}")

    family_genes_by_species: dict[str, list[str]] = defaultdict(list)
    for row in family_candidates:
        family_genes_by_species[row["species_id"]].append(clean_gene_id(row["gene_id"]))

    args.workdir.mkdir(parents=True, exist_ok=True)
    reference_db = args.workdir / args.reference_species / "reference"
    forward_hits_by_species: dict[str, list[dict[str, str]]] = {}
    reverse_hits_by_species: dict[str, list[dict[str, str]]] = {}
    manifest: list[dict[str, str]] = []

    for species_id, gene_ids in sorted(family_genes_by_species.items()):
        species_pep = pep_by_species.get(species_id)
        if species_pep is None:
            continue
        species_dir = args.workdir / species_id
        species_dir.mkdir(parents=True, exist_ok=True)
        family_fasta = species_dir / f"{species_id}.family.pep.fa"
        written = write_family_fasta(read_fasta(species_pep), gene_ids, family_fasta)
        forward_out = species_dir / f"{species_id}_to_{args.reference_species}.diamond.tsv"
        reverse_out = species_dir / f"{args.reference_species}_to_{species_id}.diamond.tsv"
        if written > 0:
            run_diamond_pair(
                diamond=args.diamond,
                query=family_fasta,
                db_fasta=reference_pep,
                db_prefix=reference_db,
                out=forward_out,
                evalue=args.evalue,
                max_target_seqs=args.max_target_seqs,
                threads=args.threads,
            )
            run_diamond_pair(
                diamond=args.diamond,
                query=reference_pep,
                db_fasta=species_pep,
                db_prefix=species_dir / "species",
                out=reverse_out,
                evalue=args.evalue,
                max_target_seqs=args.max_target_seqs,
                threads=args.threads,
            )
        forward_hits_by_species[species_id] = read_outfmt6(forward_out)
        reverse_hits_by_species[species_id] = read_outfmt6(reverse_out)
        manifest.append(
            {
                "species_id": species_id,
                "family_to_arabidopsis": str(forward_out),
                "arabidopsis_to_species": str(reverse_out),
            }
        )

    homology_rows = build_homology_rows(family_candidates, forward_hits_by_species, reverse_hits_by_species)
    outputs = transfer_aranet_edges(homology_rows, read_aranet_edges(args.aranet))

    write_tsv(homology_rows, args.outdir / "ppi_homology_best_hits.tsv", HOMOLOGY_FIELDS)
    write_tsv(manifest, args.outdir / "ppi_blast_manifest.tsv", BLAST_MANIFEST_FIELDS)
    write_tsv(outputs["edges"], args.outdir / "ppi_transferred_edges.tsv", EDGE_FIELDS)
    write_tsv(outputs["nodes"], args.outdir / "ppi_transferred_nodes.tsv", NODE_FIELDS)
    write_tsv(outputs["evidence"], args.outdir / "ppi_transfer_evidence.tsv", EVIDENCE_FIELDS)


if __name__ == "__main__":
    main()
