#!/usr/bin/env python3
"""Run an offline mock MVP using prepared evidence TSV files."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from bin.genefam.discover_species import _select_species, discover_species, write_manifest
from bin.genefam.extract_sequences import extract_fasta_records
from bin.genefam.merge_identification_evidence import merge_evidence, read_tsv, write_tsv
from bin.genefam.prepare_alignment_inputs import prepare_alignment_manifest, write_tsv as write_alignment_tsv
from bin.genefam.prepare_phylogeny_inputs import prepare_phylogeny_manifest, write_tsv as write_phylogeny_tsv
from bin.genefam.summarize_family import summarize_candidates, write_tsv as write_summary_tsv


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read YAML configuration files")
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def _write_family_fasta(
    candidates: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
    out_path: Path,
) -> None:
    pep_by_species = {row["species_id"]: row["pep"] for row in manifest_rows}
    ids_by_species: dict[str, set[str]] = {}
    for row in candidates:
        ids_by_species.setdefault(row["species_id"], set()).add(row["gene_id"])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for species_id in sorted(ids_by_species):
            records = extract_fasta_records(Path(pep_by_species[species_id]), ids_by_species[species_id])
            for gene_id, sequence in records:
                handle.write(f">{species_id}|{gene_id}\n{sequence}\n")


def _write_summary_report(
    out_path: Path,
    config: dict[str, Any],
    manifest_rows: list[dict[str, str]],
    candidates: list[dict[str, str]],
    family_counts: list[dict[str, int | str]],
    report_index_rows: list[dict[str, str]],
) -> None:
    project = config.get("project", {}) or {}
    gene_family = config.get("gene_family", {}) or {}
    final_rule = (config.get("identification", {}) or {}).get("final_rule", "")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# GeneFam-Pipeline Mock MVP Summary",
        "",
        f"Project: {project.get('name', 'unnamed')}",
        f"Gene family: {gene_family.get('name', 'unnamed')}",
        f"Final rule: {final_rule}",
        f"Species analyzed: {len(manifest_rows)}",
        f"Family candidates: {len(candidates)}",
        "",
        "## Per-Species Counts",
        "",
        "| species_id | member_count | hmmer_count | diamond_count | intersection_count |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in family_counts:
        lines.append(
            "| {species_id} | {member_count} | {hmmer_count} | {diamond_count} | {intersection_count} |".format(
                **row
            )
        )
    lines.extend(["", "## Available Outputs", ""])
    for row in report_index_rows:
        if row["status"] == "available":
            lines.append(f"- `{row['key']}`: `{row['path']}`")
    lines.extend(["", "## Pending Outputs", ""])
    for row in report_index_rows:
        if row["status"] != "available":
            lines.append(f"- `{row['key']}`: {row['description']}")
    lines.extend(
        [
            "",
            "## Mock Mode",
            "",
            "This report was generated from prepared mock HMMER and DIAMOND evidence TSV files.",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_report_index_rows(outputs: dict[str, Path], outdir: Path) -> list[dict[str, str]]:
    expected_outputs = [
        ("species_manifest", "Selected species manifest"),
        ("family_candidates", "Merged HMMER and DIAMOND candidate table"),
        ("family_counts", "Per-species gene family member counts"),
        ("family_members_faa", "Family member protein FASTA"),
        ("alignment_manifest", "Alignment input manifest for MAFFT or MUSCLE"),
        ("phylogeny_manifest", "Phylogeny input manifest for IQ-TREE or FastTree"),
        ("motif_summary", "MEME motif summary table"),
        ("syntenic_pairs", "MCScanX syntenic gene pairs"),
        ("kaks_pairs", "Ka/Ks pairwise selection pressure table"),
        ("chromosome_locations", "Family member chromosome locations"),
        ("wgd_layers", "Anonymous WGD layer assignments"),
        ("wgd_event_evidence", "Configured WGD event evidence table"),
        ("retention_enrichment", "Duplicate-type retention enrichment"),
        ("family_expression", "Family member expression matrix"),
        ("summary_report", "Markdown run summary"),
        ("report_index", "Report input availability index"),
    ]
    rows: list[dict[str, str]] = []
    for key, description in expected_outputs:
        path = outputs.get(key)
        status = "available" if path and (path.exists() or key in {"summary_report", "report_index"}) else "not_available"
        relative_path = path.relative_to(outdir).as_posix() if path else ""
        rows.append({"key": key, "path": relative_path, "status": status, "description": description})
    return rows


def _write_report_index(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["key", "path", "status", "description"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def run_mock_mvp(
    config_path: Path,
    groups_path: Path,
    mock_evidence_dir: Path,
    outdir: Path,
) -> dict[str, Path]:
    """Run the offline MVP and return standard output paths."""

    config = _load_yaml(config_path)
    groups = _load_yaml(groups_path) if groups_path and Path(groups_path).exists() else {}
    include, exclude = _select_species(config, groups)
    input_config = config.get("input", {}) or {}
    manifest_rows = discover_species(
        root=Path(input_config["root"]),
        include=include,
        exclude=exclude,
        patterns=input_config.get("patterns", {}),
        required=input_config.get("required", {}),
    )

    tables_dir = Path(outdir) / "tables"
    sequences_dir = Path(outdir) / "sequences"
    report_dir = Path(outdir) / "report"
    outputs = {
        "species_manifest": tables_dir / "species_manifest.tsv",
        "family_candidates": tables_dir / "family_candidates.tsv",
        "family_counts": tables_dir / "family_counts.tsv",
        "alignment_manifest": tables_dir / "alignment_manifest.tsv",
        "phylogeny_manifest": tables_dir / "phylogeny_manifest.tsv",
        "family_members_faa": sequences_dir / "family_members.faa",
        "summary_report": report_dir / "summary.md",
        "report_index": report_dir / "report_index.tsv",
    }

    write_manifest(manifest_rows, outputs["species_manifest"])
    hmmer_rows = read_tsv(Path(mock_evidence_dir) / "hmmer.tsv")
    diamond_rows = read_tsv(Path(mock_evidence_dir) / "diamond.tsv")
    final_rule = (config.get("identification", {}) or {}).get("final_rule", "intersection")
    candidates = merge_evidence(hmmer_rows, diamond_rows, final_rule=final_rule)
    write_tsv(candidates, outputs["family_candidates"])

    family_counts = summarize_candidates(candidates)
    write_summary_tsv(family_counts, outputs["family_counts"])
    _write_family_fasta(candidates, manifest_rows, outputs["family_members_faa"])
    alignment_rows = prepare_alignment_manifest(
        family_name=(config.get("gene_family", {}) or {}).get("name", "family"),
        fasta_path=outputs["family_members_faa"],
        outdir=Path(outdir) / "alignment",
        aligner="mafft",
    )
    write_alignment_tsv(alignment_rows, outputs["alignment_manifest"])
    write_phylogeny_tsv(
        prepare_phylogeny_manifest(alignment_rows, outdir=Path(outdir) / "phylogeny", tree_builder="iqtree"),
        outputs["phylogeny_manifest"],
    )
    report_index_rows = _build_report_index_rows(outputs, Path(outdir))
    _write_report_index(report_index_rows, outputs["report_index"])
    _write_summary_report(outputs["summary_report"], config, manifest_rows, candidates, family_counts, report_index_rows)
    return outputs


def _print_outputs(outputs: dict[str, Path]) -> None:
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    writer.writerow(["output", "path"])
    for key in sorted(outputs):
        writer.writerow([key, outputs[key]])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--groups", required=True, type=Path)
    parser.add_argument("--mock-evidence-dir", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    _print_outputs(run_mock_mvp(args.config, args.groups, args.mock_evidence_dir, args.outdir))


if __name__ == "__main__":
    main()
