#!/usr/bin/env python3
"""Run 07_domain_motif_genestructure: MEME motifs, domain tracks, gene structures, and composite plotting."""

from __future__ import annotations

import argparse
import csv
import re
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[2]
PLOT_SCRIPT = REPO_ROOT / "scripts/plot_domain_motif_genestructure.R"
MOTIF_FIELDS = ["gene_id", "motif_id", "start", "end", "width", "pvalue", "sequence"]
DOMAIN_FIELDS = ["species_id", "gene_id", "domain_id", "start", "end", "domain_coverage", "evalue", "bitscore"]
STRUCTURE_FIELDS = ["species_id", "gene_id", "feature", "start", "end", "strand", "seqid"]
COMMAND_FIELDS = ["step", "tool", "command", "stdout", "stderr", "status"]


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


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def read_tsv(path: Path | None) -> list[dict[str, str]]:
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fasta_records(path: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    header: str | None = None
    chunks: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(chunks)))
                header = line[1:].split()[0]
                chunks = []
            else:
                chunks.append(line)
    if header is not None:
        records.append((header, "".join(chunks)))
    return records


def split_member_id(identifier: str) -> tuple[str, str]:
    if "|" in identifier:
        species_id, gene_id = identifier.split("|", 1)
        return species_id, gene_id
    return "Unknown", identifier


def write_clean_fasta(input_fasta: Path, output_fasta: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    output_fasta.parent.mkdir(parents=True, exist_ok=True)
    with output_fasta.open("w", encoding="utf-8") as out:
        for original_id, sequence in fasta_records(input_fasta):
            species_id, gene_id = split_member_id(original_id)
            rows.append({"original_id": original_id, "species_id": species_id, "gene_id": gene_id})
            out.write(f">{gene_id}\n{sequence}\n")
    return rows


def run_meme(input_fasta: Path, meme_dir: Path, executable: str, nmotifs: int, minw: int, maxw: int, log_dir: Path) -> dict[str, str]:
    found = shutil.which(executable)
    if found is None:
        raise RuntimeError(f"Required command not found: {executable}")
    meme_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    command = [found, str(input_fasta), "-oc", str(meme_dir), "-mod", "anr", "-protein", "-nmotifs", str(nmotifs), "-minw", str(minw), "-maxw", str(maxw)]
    stdout_path = log_dir / "meme.stdout.log"
    stderr_path = log_dir / "meme.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {"step": "meme", "tool": Path(found).name, "command": shell_join(command), "stdout": str(stdout_path), "stderr": str(stderr_path), "status": "completed"}


def _xml_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_meme_xml(path: Path) -> list[dict[str, str]]:
    tree = ET.parse(path)
    root = tree.getroot()
    motifs: dict[str, str] = {}
    sequences: dict[str, str] = {}
    for elem in root.iter():
        name = _xml_local_name(elem.tag)
        if name == "motif":
            motif_id = elem.attrib.get("id") or elem.attrib.get("name") or elem.attrib.get("alt", "motif")
            motifs[motif_id] = elem.attrib.get("alt") or elem.attrib.get("name") or motif_id
        elif name == "sequence":
            seq_id = elem.attrib.get("id", "")
            seq_name = elem.attrib.get("name", seq_id)
            if seq_id:
                sequences[seq_id] = seq_name

    rows: list[dict[str, str]] = []
    for scanned in root.iter():
        if _xml_local_name(scanned.tag) != "scanned_site":
            continue
        sequence_id = scanned.attrib.get("sequence_id", "")
        gene_id = sequences.get(sequence_id, scanned.attrib.get("sequence_name", sequence_id))
        pvalue = scanned.attrib.get("pvalue", "")
        for site in scanned:
            if _xml_local_name(site.tag) != "site":
                continue
            motif_id = site.attrib.get("motif_id", "")
            start = int(site.attrib.get("position", "0")) + 1
            width = int(site.attrib.get("width", "0") or "0")
            sequence = site.attrib.get("match", "")
            if width == 0 and sequence:
                width = len(sequence)
            rows.append(
                {
                    "gene_id": gene_id,
                    "motif_id": motifs.get(motif_id, motif_id),
                    "start": str(start),
                    "end": str(start + max(width, 1) - 1),
                    "width": str(width),
                    "pvalue": pvalue,
                    "sequence": sequence,
                }
            )
    return rows


def parse_meme_text_locations(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    motif_name = ""
    motif_header = re.compile(r"Motif.*Description")
    site_line = re.compile(r"^[A-Za-z0-9_.|:+-]+\s+\d+\s+\S+\s+\S+")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if motif_header.match(text):
                parts = text.split()
                if len(parts) >= 3:
                    motif_name = parts[2]
                continue
            if motif_name and site_line.match(text):
                parts = text.split()
                gene_id = parts[0].split("|")[-1]
                start = int(parts[1])
                sequence = parts[-1]
                rows.append(
                    {
                        "gene_id": gene_id,
                        "motif_id": motif_name,
                        "start": str(start),
                        "end": str(start + len(sequence) - 1),
                        "width": str(len(sequence)),
                        "pvalue": parts[2] if len(parts) > 2 else "",
                        "sequence": sequence,
                    }
                )
    return rows


def parse_meme_locations(meme_dir: Path) -> list[dict[str, str]]:
    xml_path = meme_dir / "meme.xml"
    if xml_path.exists():
        rows = parse_meme_xml(xml_path)
        if rows:
            return rows
    text_path = meme_dir / "meme.txt"
    if text_path.exists():
        return parse_meme_text_locations(text_path)
    return []


def normalize_domain_rows(rows: list[dict[str, str]], allowed_genes: set[str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in rows:
        gene_id = row.get("gene_id", "")
        if gene_id not in allowed_genes:
            continue
        output.append(
            {
                "species_id": row.get("species_id", ""),
                "gene_id": gene_id,
                "domain_id": row.get("hmm_id", row.get("domain_id", "domain")),
                "start": row.get("ali_from", row.get("start", "")),
                "end": row.get("ali_to", row.get("end", "")),
                "domain_coverage": row.get("domain_coverage", ""),
                "evalue": row.get("evalue", ""),
                "bitscore": row.get("bitscore", ""),
            }
        )
    return output


def parse_attrs(value: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for item in value.split(";"):
        if "=" in item:
            key, val = item.split("=", 1)
            attrs[key] = val
    return attrs


def normalize_gene_id(value: str) -> str:
    value = value.split("|")[-1]
    for pattern in (r"\.CDS.*$", r"\.cds.*$", r"\.\d+$"):
        value = re.sub(pattern, "", value)
    return value


def parse_gff_gene_structures(gff_path: Path, species_id: str, allowed_genes: set[str]) -> list[dict[str, str]]:
    gene_ids: dict[str, str] = {}
    transcript_to_gene: dict[str, str] = {}
    feature_rows: list[dict[str, str]] = []
    with gff_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9:
                continue
            seqid, _source, feature, start, end, _score, strand, _phase, attr_text = parts
            attrs = parse_attrs(attr_text)
            feature_id = attrs.get("ID", "")
            parent = attrs.get("Parent", "")
            name = attrs.get("Name", "")
            if feature == "gene":
                gene = normalize_gene_id(name or feature_id)
                gene_ids[feature_id] = gene
            elif feature in {"mRNA", "transcript"}:
                gene = normalize_gene_id(attrs.get("Parent", "") or name or feature_id)
                if gene not in allowed_genes and name:
                    gene = normalize_gene_id(name)
                transcript_to_gene[feature_id] = gene
            elif feature in {"CDS", "exon", "five_prime_UTR", "three_prime_UTR", "UTR"}:
                gene = transcript_to_gene.get(parent) or gene_ids.get(parent) or normalize_gene_id(parent or feature_id)
                if gene in allowed_genes:
                    feature_rows.append(
                        {
                            "species_id": species_id,
                            "gene_id": gene,
                            "feature": "UTR" if "UTR" in feature else feature,
                            "start": start,
                            "end": end,
                            "strand": strand,
                            "seqid": seqid,
                        }
                    )

    by_gene: dict[str, list[dict[str, str]]] = {}
    for row in feature_rows:
        by_gene.setdefault(row["gene_id"], []).append(row)
    scaled: list[dict[str, str]] = []
    for gene_id, rows in by_gene.items():
        starts = [int(row["start"]) for row in rows]
        ends = [int(row["end"]) for row in rows]
        strand = rows[0]["strand"]
        if strand == "-":
            anchor = max(ends)
            for row in rows:
                scaled.append({**row, "start": str(anchor - int(row["end"])), "end": str(anchor - int(row["start"]))})
        else:
            anchor = min(starts)
            for row in rows:
                scaled.append({**row, "start": str(int(row["start"]) - anchor), "end": str(int(row["end"]) - anchor)})
    return scaled


def collect_gene_structures(clean_bank: Path, species_by_gene: dict[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    allowed_by_species: dict[str, set[str]] = {}
    for gene_id, species_id in species_by_gene.items():
        allowed_by_species.setdefault(species_id, set()).add(gene_id)
    for species_id, genes in allowed_by_species.items():
        gff_path = clean_bank / species_id / "clean" / f"{species_id}.gff3"
        if gff_path.exists():
            rows.extend(parse_gff_gene_structures(gff_path, species_id, genes))
    return rows


def run_plot(treefile: Path, label_map: Path, motifs: Path, domains: Path, structures: Path, outdir: Path, r_bin: str, log_dir: Path) -> dict[str, str]:
    found = shutil.which(r_bin)
    if found is None:
        raise RuntimeError(f"Required command not found: {r_bin}")
    log_dir.mkdir(parents=True, exist_ok=True)
    command = [found, str(PLOT_SCRIPT), str(treefile), str(label_map), str(motifs), str(domains), str(structures), str(outdir)]
    if Path(found).name == "R":
        command = [found, "--vanilla", "--slave", "-f", str(PLOT_SCRIPT), "--args", str(treefile), str(label_map), str(motifs), str(domains), str(structures), str(outdir)]
    stdout_path = log_dir / "plot.stdout.log"
    stderr_path = log_dir / "plot.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {"step": "plot", "tool": Path(found).name, "command": shell_join(command), "stdout": str(stdout_path), "stderr": str(stderr_path), "status": "completed"}


def resolve_args(args: argparse.Namespace) -> dict:
    config = load_project_config(args.config)
    config_dir = args.config.parent if args.config else Path.cwd()
    project_config = config.get("project", {}) or {}
    module_config = config.get("domain_motif_genestructure", {}) or {}
    phylogeny_config = config.get("phylogeny", {}) or {}
    database_config = config.get("database", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    family_name = args.family_name or module_config.get("family_name") or phylogeny_config.get("family_name") or project_config.get("family_name") or "family"
    treefile = args.treefile or config_path(module_config.get("treefile"), config_dir)
    if treefile is None:
        manifest_rows = read_tsv(project_outdir / "06_phylogeny/tables/phylogeny_manifest.tsv")
        treefile = Path(manifest_rows[0]["treefile"]) if manifest_rows else project_outdir / f"06_phylogeny/phylogeny/{family_name}.fasttree.treefile"
    return {
        "family_name": family_name,
        "input_fasta": args.input_fasta or config_path(module_config.get("input_fasta"), config_dir) or project_outdir / "04_identification/fasta/identify.ID.fa",
        "family_candidates": config_path(module_config.get("family_candidates"), config_dir) or project_outdir / "04_identification/tables/family_candidates.tsv",
        "treefile": treefile,
        "label_map": config_path(module_config.get("label_map"), config_dir) or project_outdir / "06_phylogeny/tables/phylogeny_label_map.tsv",
        "domains": config_path(module_config.get("domains"), config_dir) or project_outdir / "02_hmm/tables/hmm_hits.filtered.tsv",
        "species_clean_bank": config_path(database_config.get("species_clean_bank"), config_dir) or project_outdir / "01_preprocess/species_clean_bank",
        "outdir": args.outdir or config_path(module_config.get("outdir"), config_dir) or project_outdir / "07_domain_motif_genestructure",
        "meme_executable": str(module_config.get("meme_executable", "meme")),
        "r_bin": str(module_config.get("r_bin", "/usr/local/bin/R")),
        "nmotifs": int(module_config.get("nmotifs", 10)),
        "minw": int(module_config.get("minw", 20)),
        "maxw": int(module_config.get("maxw", 150)),
    }


def run_module(**kwargs) -> Path:
    outdir: Path = kwargs["outdir"]
    tables_dir = outdir / "tables"
    logs_dir = outdir / "logs"
    meme_dir = outdir / "meme"
    clean_fasta = outdir / "inputs/identify.ID.clean.fa"
    commands: list[dict[str, str]] = []

    if not kwargs["input_fasta"].exists():
        raise ValueError(f"Input FASTA does not exist: {kwargs['input_fasta']}")
    clean_rows = write_clean_fasta(kwargs["input_fasta"], clean_fasta)
    species_by_gene = {row["gene_id"]: row["species_id"] for row in clean_rows}
    allowed_genes = set(species_by_gene)

    commands.append(run_meme(clean_fasta, meme_dir, kwargs["meme_executable"], kwargs["nmotifs"], kwargs["minw"], kwargs["maxw"], logs_dir))
    motif_rows = [row for row in parse_meme_locations(meme_dir) if row["gene_id"] in allowed_genes]
    domain_rows = normalize_domain_rows(read_tsv(kwargs["domains"]), allowed_genes)
    structure_rows = collect_gene_structures(kwargs["species_clean_bank"], species_by_gene)

    motif_path = tables_dir / "motif_locations.tsv"
    domain_path = tables_dir / "domain_locations.tsv"
    structure_path = tables_dir / "gene_structure_tracks.tsv"
    write_tsv(motif_rows, motif_path, MOTIF_FIELDS)
    write_tsv(domain_rows, domain_path, DOMAIN_FIELDS)
    write_tsv(structure_rows, structure_path, STRUCTURE_FIELDS)

    commands.append(run_plot(kwargs["treefile"], kwargs["label_map"], motif_path, domain_path, structure_path, outdir, kwargs["r_bin"], logs_dir))
    write_tsv(commands, tables_dir / "domain_motif_genestructure_commands.tsv", COMMAND_FIELDS)

    report = [
        "# 07_domain_motif_genestructure Summary",
        "",
        f"- Input FASTA: `{kwargs['input_fasta']}`",
        f"- Clean MEME FASTA: `{clean_fasta}`",
        f"- Treefile: `{kwargs['treefile']}`",
        f"- Motif locations: `{motif_path}` ({len(motif_rows)} rows)",
        f"- Domain locations: `{domain_path}` ({len(domain_rows)} rows)",
        f"- Gene structure tracks: `{structure_path}` ({len(structure_rows)} rows)",
        f"- Composite plot: `{outdir / 'plots/tree_domain_motif_genestructure.pdf'}`",
        f"- MEME command: `{commands[0]['command']}`",
        f"- Plot command: `{commands[1]['command']}`",
    ]
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/domain_motif_genestructure_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--input-fasta", default=None, type=Path)
    parser.add_argument("--treefile", default=None, type=Path)
    parser.add_argument("--outdir", default=None, type=Path)
    parser.add_argument("--family-name", default=None)
    args = parser.parse_args()
    try:
        outdir = run_module(**resolve_args(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"07_domain_motif_genestructure completed at {outdir.resolve()}")


if __name__ == "__main__":
    main()
