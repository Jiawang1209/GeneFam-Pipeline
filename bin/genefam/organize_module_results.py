#!/usr/bin/env python3
"""Organize a standard GeneFam result directory into per-module folders."""

from __future__ import annotations

import argparse
import csv
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModuleSpec:
    key: str
    title: str
    patterns: tuple[str, ...]
    required_any: tuple[str, ...] = ()


MODULES = [
    ModuleSpec(
        "00_preprocess",
        "Input Cleaning And Run Configuration",
        (
            "tables/species_manifest.tsv",
            "tables/run_config_snapshot.tsv",
            "tables/all_transcript_gene_map.tsv",
            "tables/all_representative_transcripts.tsv",
            "tables/all_preprocess_warnings.tsv",
            "species_bank_clean/**/*",
        ),
        ("tables/species_manifest.tsv",),
    ),
    ModuleSpec(
        "01_gene_identification",
        "Family Member Identification",
        (
            "tables/family_candidates.tsv",
            "tables/pfam_confirmation/*",
            "tables/family_counts.tsv",
            "sequences/family_members.faa",
            "plots/family_counts.pdf",
            "plots/family_counts.png",
        ),
        ("tables/family_candidates.tsv",),
    ),
    ModuleSpec(
        "02_domain_filtering",
        "HMMER DIAMOND Domain Filtering",
        ("tables/domain_filter/*.tsv", "two_pass_hmmer/**/*"),
        ("tables/domain_filter/*.tsv",),
    ),
    ModuleSpec(
        "03_alignment",
        "Multiple Sequence Alignment",
        ("tables/alignment_manifest.tsv", "alignment/*"),
        ("alignment/*",),
    ),
    ModuleSpec(
        "04_phylogeny",
        "Phylogenetic Tree",
        ("tables/phylogeny_manifest.tsv", "phylogeny/*"),
        ("phylogeny/*",),
    ),
    ModuleSpec(
        "05_motif_analysis",
        "Motif Analysis",
        ("tables/motif_summary.tsv", "meme/**/*"),
        ("tables/motif_summary.tsv",),
    ),
    ModuleSpec(
        "06_gene_structure",
        "Gene Structure",
        ("tables/gene_structure_summary.tsv",),
        ("tables/gene_structure_summary.tsv",),
    ),
    ModuleSpec(
        "07_chromosome_location",
        "Chromosome Location",
        ("tables/chromosome_locations.tsv",),
        ("tables/chromosome_locations.tsv",),
    ),
    ModuleSpec(
        "08_promoter",
        "Promoter Extraction",
        ("tables/promoters.bed", "sequences/promoters.fa", "plantcare_submission/**/*"),
        ("tables/promoters.bed", "sequences/promoters.fa"),
    ),
    ModuleSpec(
        "09_promoter_cis",
        "Promoter Cis Element",
        (
            "tables/promoter_cis*.tsv",
            "tables/promoter_cis_status.tsv",
            "plots/promoter_cis_elements.pdf",
            "plots/promoter_cis_elements.png",
            "plots/promoter1.pdf",
            "plots/promoter1.png",
            "plots/species_promoter2.pdf",
            "plots/species_promoter2.png",
        ),
        ("tables/promoter_cis_elements.tsv", "tables/promoter_cis_status.tsv"),
    ),
    ModuleSpec(
        "10_synteny_jcvi",
        "JCVI Collinearity And Karyotype",
        (
            "jcvi_collinearity/**/*.bed",
            "jcvi_collinearity/**/*.pep",
            "jcvi_collinearity/**/*.tsv",
            "jcvi_collinearity/seqids",
            "jcvi_collinearity/layout",
            "jcvi_collinearity/commands/*.sh",
            "jcvi_collinearity/*.pdf",
            "jcvi_collinearity/*.png",
        ),
        ("jcvi_collinearity/jcvi_pair_manifest.tsv",),
    ),
    ModuleSpec(
        "11_mcscanx",
        "MCScanX Self Duplication And Circos",
        (
            "mcscanx_self_circos/**/*.bed",
            "mcscanx_self_circos/**/*.csv",
            "mcscanx_self_circos/**/*.gff",
            "mcscanx_self_circos/**/*.blast",
            "mcscanx_self_circos/**/*.collinearity",
            "mcscanx_self_circos/**/*.tandem",
            "mcscanx_self_circos/**/*.html",
            "mcscanx_self_circos/**/*.tsv",
            "mcscanx_self_circos/**/*.log",
            "mcscanx_self_circos/commands/*.sh",
            "mcscanx_self_circos/**/*.pdf",
            "mcscanx_self_circos/**/*.png",
            "tables/circlize*.tsv",
            "plots/mcscanx_circlize.pdf",
            "plots/mcscanx_circlize.png",
            "plots/species/**/*.pdf",
            "plots/species/**/*.png",
        ),
        ("mcscanx_self_circos/mcscanx_self_status.tsv", "plots/mcscanx_circlize.pdf", "tables/circlize_links.tsv"),
    ),
    ModuleSpec(
        "12_ppi",
        "PPI AraNet Transfer And ggNetView",
        (
            "tables/ppi*.tsv",
            "tables/node_annotation.tsv",
            "tables/species_ppi_annotation.tsv",
            "tables/ppi_blast/**/*.tsv",
            "plots/ppi.pdf",
            "plots/ppi.png",
            "plots/ppi_ggnetview.pdf",
            "plots/ppi_ggnetview.png",
        ),
        ("tables/ppi_edges.tsv", "plots/ppi_ggnetview.pdf"),
    ),
    ModuleSpec(
        "13_expression",
        "RNA Seq Expression Integration",
        ("tables/expression*.tsv", "tables/family_expression.tsv", "plots/expression_heatmap.pdf", "plots/expression_heatmap.png"),
        ("plots/expression_heatmap.pdf", "tables/expression_group_matrix.tsv", "tables/expression_status.tsv"),
    ),
    ModuleSpec(
        "14_duplication_retention_kaks",
        "Duplication Retention KaKs WGD Events",
        (
            "tables/wgd*.tsv",
            "tables/mcscanx_duplicate_types.tsv",
            "tables/*kaks*.tsv",
            "kaks_inputs/**/*.tsv",
            "kaks_inputs/**/*.fa",
            "plots/*kaks*.pdf",
            "plots/*kaks*.png",
            "plots/*wgd*.pdf",
            "plots/*wgd*.png",
            "plots/ks_distribution.pdf",
            "plots/ks_distribution.png",
        ),
        ("tables/wgd_handoff_manifest.tsv",),
    ),
    ModuleSpec(
        "15_gene_family_summary",
        "Gene Family Statistics And Feature Summary",
        (
            "tables/gene_family*.tsv",
            "tables/feature_summary.tsv",
            "tables/tree_feature_matrix.tsv",
            "plots/gene_family_info_summary.pdf",
            "plots/gene_family_info_summary.png",
            "plots/feature_summary.pdf",
            "plots/feature_summary.png",
            "plots/tree_features.pdf",
            "plots/tree_features.png",
        ),
        ("tables/gene_family_copy_number.tsv", "tables/feature_summary.tsv"),
    ),
]

REPORT_PATTERNS = (
    "report/*.md",
    "report/*.tsv",
)
PLOT_SUFFIXES = {".pdf", ".png", ".svg"}


def find_matches(source: Path, patterns: tuple[str, ...]) -> list[Path]:
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(path for path in source.glob(pattern) if path.is_file())
    return sorted(set(matches))


def relative_destination(module_dir: Path, source: Path, path: Path) -> Path:
    relative = path.relative_to(source)
    if relative.parts and relative.parts[0] == "plantcare_submission":
        return module_dir.joinpath(*relative.parts)
    if relative.parts and relative.parts[0] == "plots" and len(relative.parts) > 2:
        return module_dir.joinpath(*relative.parts)
    if relative.parts and relative.parts[0] in {"tables", "plots", "sequences", "alignment", "phylogeny", "report", "jcvi_collinearity", "mcscanx_self_circos", "kaks_inputs", "meme"}:
        return module_dir.joinpath(*relative.parts[1:])
    return module_dir / relative


def copy_matches(source: Path, module_dir: Path, matches: list[Path]) -> list[str]:
    copied: list[str] = []
    for path in matches:
        destination = relative_destination(module_dir, source, path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied.append(str(destination.relative_to(module_dir)))
    return copied


def copy_top_level_plots(source: Path, outdir: Path) -> list[str]:
    plot_dir = source / "plots"
    if not plot_dir.exists():
        return []
    copied: list[str] = []
    for path in sorted(plot_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in PLOT_SUFFIXES:
            continue
        destination = outdir / "plots" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        copied.append(str(destination.relative_to(outdir)))
    return copied


def _module_package_plot_path(source: Path, module_root: Path, value: str) -> str:
    if not value.strip():
        return value
    path = Path(value.split("#", 1)[0])
    if path.suffix.lower() not in PLOT_SUFFIXES:
        return value
    if path.is_absolute():
        try:
            relative = path.relative_to(source)
        except ValueError:
            relative = None
        if relative and relative.parts and relative.parts[0] == "plots":
            return f"../plots/{path.name}"
        return value
    if path.parts and path.parts[0] == "plots":
        return f"../plots/{path.name}"
    if "plots" in path.parts:
        return f"../plots/{path.name}"
    return value


def rewrite_report_index_for_module_package(source: Path, module_root: Path, report_index: Path) -> None:
    if not report_index.exists():
        return
    with report_index.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = list(reader)
        fieldnames = reader.fieldnames or ["key", "path", "status", "description"]
    for row in rows:
        row["path"] = _module_package_plot_path(source, module_root, row.get("path", ""))
    with report_index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def module_status(source: Path, spec: ModuleSpec) -> str:
    if spec.key == "10_synteny_jcvi":
        dependency_status = source / "jcvi_collinearity" / "jcvi_dependency_status.tsv"
        if dependency_status.exists() and "missing_dependency" in dependency_status.read_text(encoding="utf-8"):
            return "prepared_missing_dependency"
    if spec.key == "11_mcscanx":
        circlize_status = source / "mcscanx_self_circos" / "mcscanx_circlize_status.tsv"
        if circlize_status.exists() and "available" in circlize_status.read_text(encoding="utf-8"):
            return "available"
        status_path = source / "mcscanx_self_circos" / "mcscanx_self_status.tsv"
        if status_path.exists():
            text = status_path.read_text(encoding="utf-8")
            if "missing_input" in text:
                return "missing_input"
            if "available" in text:
                return "available"
    if spec.key == "09_promoter_cis":
        status_path = source / "tables" / "promoter_cis_status.tsv"
        if status_path.exists() and "missing_input" in status_path.read_text(encoding="utf-8"):
            return "missing_input"
    if spec.key == "14_duplication_retention_kaks":
        for status_path in (
            source / "kaks_inputs" / "kaks_calculator_status.tsv",
            source / "kaks_inputs" / "kaks_input_status.tsv",
        ):
            if status_path.exists():
                text = status_path.read_text(encoding="utf-8")
                if "missing_input" in text:
                    return "missing_input"
                if "missing_dependency" in text:
                    return "prepared_missing_dependency"
                if "partial" in text:
                    return "partial"
                if "available" in text:
                    return "available"
    if spec.key == "13_expression":
        status_path = source / "tables" / "expression_status.tsv"
        if status_path.exists():
            text = status_path.read_text(encoding="utf-8")
            if "skipped_optional" in text:
                return "skipped_optional"
            if "missing_input" in text:
                return "missing_input"
            if "available" in text:
                return "available"
    if not spec.required_any:
        return "available" if find_matches(source, spec.patterns) else "missing"
    return "available" if any(find_matches(source, (pattern,)) for pattern in spec.required_any) else "missing"


def _first_status_note(path: Path, note_fields: tuple[str, ...] = ("note", "detail")) -> str:
    if not path.exists():
        return ""
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in note_fields:
            value = row.get(field, "").strip()
            if value:
                return value
    return ""


def module_note(source: Path, spec: ModuleSpec, copied: list[str]) -> str:
    status_note_paths = {
        "10_synteny_jcvi": (
            source / "jcvi_collinearity" / "jcvi_run_status.tsv",
            source / "jcvi_collinearity" / "jcvi_dependency_status.tsv",
        ),
        "11_mcscanx": (
            source / "mcscanx_self_circos" / "mcscanx_execution_status.tsv",
            source / "mcscanx_self_circos" / "mcscanx_circlize_status.tsv",
            source / "mcscanx_self_circos" / "mcscanx_self_status.tsv",
        ),
        "09_promoter_cis": (source / "tables" / "promoter_cis_status.tsv",),
        "13_expression": (source / "tables" / "expression_status.tsv",),
        "14_duplication_retention_kaks": (
            source / "kaks_inputs" / "kaks_calculator_status.tsv",
            source / "kaks_inputs" / "kaks_input_status.tsv",
        ),
        "01_gene_identification": (source / "tables" / "pfam_confirmation" / "pfam_confirmation_status.tsv",),
    }
    for path in status_note_paths.get(spec.key, ()):
        note = _first_status_note(path)
        if note:
            return note
    return "ok" if copied else "no matching files in current result package"


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["module", "title", "status", "file_count", "folder", "note"]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_readme(rows: list[dict[str, str]], out_path: Path) -> None:
    lines = [
        "# GeneFam-Pipeline Module Result Package",
        "",
        "This directory reorganizes the standard result files into one folder per analysis module.",
        "",
        "| Module | Status | Files | Folder |",
        "| --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['module']} - {row['title']} | {row['status']} | {row['file_count']} | `{row['folder']}` |")
    lines.extend(
        [
            "",
            "The top-level `report/` folder contains the final report, software versions, plot manifest, and reproducibility code.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def module_status_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        "## Module Execution Status",
        "",
        "This table records which Reference-style analysis modules produced outputs and which modules need extra inputs or software.",
        "",
        "| Module | Title | Status | Files | Folder | Note |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['module']} | {row['title']} | {row['status']} | {row['file_count']} | `{row['folder']}` | {row['note']} |"
        )
    lines.append("")
    return "\n".join(lines)


def append_module_status_to_report(final_report: Path, rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = Path(final_report).read_text(encoding="utf-8")
    summary = module_status_markdown(rows)
    if "## Module Execution Status" in text:
        out_path.write_text(text, encoding="utf-8")
    else:
        out_path.write_text(text.rstrip() + "\n\n" + summary, encoding="utf-8")


def organize(source: Path, outdir: Path, final_report: Path | None = None) -> list[dict[str, str]]:
    if not source.exists():
        raise FileNotFoundError(source)
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for spec in MODULES:
        module_dir = outdir / spec.key
        module_dir.mkdir(parents=True, exist_ok=True)
        matches = find_matches(source, spec.patterns)
        copied = copy_matches(source, module_dir, matches)
        status = module_status(source, spec)
        note = module_note(source, spec, copied)
        rows.append(
            {
                "module": spec.key,
                "title": spec.title,
                "status": status,
                "file_count": str(len(copied)),
                "folder": spec.key,
                "note": note,
            }
        )

    report_dir = outdir / "report"
    report_matches = find_matches(source, REPORT_PATTERNS)
    copied_report = copy_matches(source, report_dir, report_matches)
    copy_top_level_plots(source, outdir)
    rewrite_report_index_for_module_package(source, outdir, report_dir / "report_index.tsv")
    rows.append(
        {
            "module": "report",
            "title": "Final Report And Reproducibility",
            "status": "available" if copied_report else "missing",
            "file_count": str(len(copied_report)),
            "folder": "report",
            "note": "ok" if copied_report else "no report files found",
        }
    )

    write_tsv(rows, outdir / "module_manifest.tsv")
    write_readme(rows, outdir / "README.md")
    (outdir / "module_status_summary.md").write_text(module_status_markdown(rows), encoding="utf-8")
    if final_report:
        append_module_status_to_report(final_report, rows, outdir / "report" / "final_report.md")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--final-report", default=None, type=Path)
    args = parser.parse_args()
    organize(args.source, args.outdir, final_report=args.final_report)


if __name__ == "__main__":
    main()
