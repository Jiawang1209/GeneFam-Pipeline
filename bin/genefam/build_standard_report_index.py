#!/usr/bin/env python3
"""Build a report index for the standard identification branch."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["key", "path", "status", "description"]
DESCRIPTIONS = {
    "species_manifest": "Selected species and input files",
    "run_config_snapshot": "Run configuration and selected species snapshot",
    "family_candidates": "Merged family candidate members",
    "family_counts": "Per-species family member counts",
    "family_counts_pdf": "Family member counts PDF plot",
    "family_counts_png": "Family member counts PNG plot",
    "family_members_faa": "Family member peptide FASTA",
    "gene_family_copy_number": "Gene family copy-number table with per-species classes",
    "gene_family_copy_number_summary": "Gene family copy-number class summary",
    "gene_family_species_order": "Gene family species plotting order from external species-tree order or copy-number rank",
    "gene_family_copy_number_expansion": "Gene family copy-number expansion and contraction status relative to the median",
    "gene_family_pangenome_summary": "Gene family pan-genome presence summary with core, soft-core, dispensable, or absent classification",
    "gene_family_protein_properties": "Gene family protein length, molecular weight, pI, and GRAVY table",
    "gene_family_info_pdf": "Gene family information summary PDF plot",
    "gene_family_info_png": "Gene family information summary PNG plot",
    "alignment_manifest": "Alignment preparation manifest",
    "alignment_file": "Multiple sequence alignment FASTA",
    "phylogeny_manifest": "Phylogeny preparation manifest",
    "phylogeny_tree": "Phylogenetic tree file",
    "motif_summary": "MEME motif summary table",
    "gene_structure_summary": "Gene structure summary from GFF3 annotation",
    "tree_feature_matrix": "Tree-ordered motif, gene-structure, and domain feature matrix",
    "tree_features_pdf": "Tree, motif, gene-structure, and domain composite PDF plot",
    "tree_features_png": "Tree, motif, gene-structure, and domain composite PNG plot",
    "chromosome_locations": "Family member chromosome coordinates",
    "promoters_bed": "Promoter coordinate BED table",
    "promoters_fasta": "Promoter sequence FASTA",
    "plantcare_submission_manifest": "PlantCARE submission FASTA part manifest for promoter cis-element analysis handoff",
    "plantcare_submission_status": "PlantCARE submission preparation status and split-file counts",
    "promoter_cis_elements": "Normalized promoter cis-element occurrence table",
    "promoter_cis_gene_matrix": "Promoter cis-element gene-by-category count matrix",
    "promoter_cis_gene_element_matrix": "Promoter cis-element gene-by-element count matrix",
    "promoter_cis_category_summary": "Promoter cis-element category and element summary table",
    "promoter_cis_element_annotations": "Promoter cis-element per-element biological annotation and position summary table",
    "promoter_cis_pdf": "Promoter cis-element PDF plot",
    "promoter_cis_png": "Promoter cis-element PNG plot",
    "promoter1_pdf": "Reference-style promoter1 PDF plot with gene-level cis-element category and element matrices",
    "promoter1_png": "Reference-style promoter1 PNG plot with gene-level cis-element category and element matrices",
    "species_promoter2_pdf": "Reference-style species_promoter2 PDF plot with species-level promoter cis-element summary",
    "species_promoter2_png": "Reference-style species_promoter2 PNG plot with species-level promoter cis-element summary",
    "feature_summary": "Combined domain, motif, gene-structure, synteny, and promoter feature statistics",
    "feature_summary_pdf": "Feature summary PDF plot",
    "feature_summary_png": "Feature summary PNG plot",
    "circlize_link_density": "MCScanX circlize linked-gene density windows",
    "circlize_duplicate_type_tracks": "MCScanX circlize duplicate-type track rows",
    "mcscanx_circlize_pdf": "MCScanX syntenic-link circlize PDF plot",
    "mcscanx_circlize_png": "MCScanX syntenic-link circlize PNG plot",
    "ppi_edges": "Normalized PPI edge table for ggNetView",
    "ppi_nodes": "PPI node annotation and degree table",
    "ppi_hubs": "Top PPI hub table ranked by weighted degree",
    "ppi_input_evidence": "PPI input evidence table documenting edge cleaning and normalization",
    "ppi_network_qc": "PPI network QC table with node, edge, hub, species, and annotation coverage metrics",
    "ppi_node_annotation": "Reference-style PPI node annotation table with ID, Domain, species, Type, degree, and weighted degree",
    "ppi_species_annotation": "Reference-style species PPI edge annotation table with source and target domain assignments",
    "ppi_overview_status": "PPI overview plotting status table recording whether Reference-style ggraph or ggplot2 fallback was used",
    "ppi_ggnetview_status": "ggNetView PPI plotting status table",
    "ppi_pdf": "Reference-style PPI network overview PDF plot",
    "ppi_png": "Reference-style PPI network overview PNG plot",
    "ppi_ggnetview_pdf": "PPI network PDF plot generated with ggNetView",
    "ppi_ggnetview_png": "PPI network PNG plot generated with ggNetView",
    "family_expression": "Family member RNA-seq expression matrix",
    "expression_sample_metadata": "RNA-seq sample metadata used for heatmap labels and grouping",
    "expression_group_matrix": "Family expression matrix averaged by sample group",
    "expression_gene_summary": "Per-gene expression response summary and QC table",
    "expression_heatmap_pdf": "Annotated family expression heatmap PDF plot",
    "expression_heatmap_png": "Annotated family expression heatmap PNG plot",
    "wgd_handoff_manifest": "Standard-to-WGD handoff manifest for duplication and WGD event analysis",
    "kaks_failure_summary": "Ka/Ks calculator failure diagnostics grouped by collinearity source, calculator note, and CDS QC flags",
    "wgd_layers": "Ks-derived WGD layer assignments for standard-branch Ka/Ks pairs",
    "kaks_wgd_annotations": "WGD event labels and Ks positions used to annotate the standard-branch Ks distribution plot",
    "wgd_event_evidence": "Layer-level WGD event evidence table with configured event metadata",
    "ks_distribution_pdf": "Ks distribution PDF plot for WGD-layer interpretation",
    "ks_distribution_png": "Ks distribution PNG plot for WGD-layer interpretation",
    "mcscanx_duplicate_types": "Gene-level duplicate-type classification derived from MCScanX self intra-species pairs",
    "duplicate_type_kaks": "Ka/Ks table grouped by MCScanX self duplicate type",
    "duplicate_type_kaks_summary": "Duplicate-type Ka/Ks summary statistics",
    "duplicate_type_kaks_pdf": "Duplicate-type Ka/Ks PDF plot from MCScanX self classifications",
    "duplicate_type_kaks_png": "Duplicate-type Ka/Ks PNG plot from MCScanX self classifications",
    "plot_manifest": "Generated plot inventory",
    "software_versions": "Software and R package version table for methods reporting",
    "figure_interpretations": "Structured per-figure result interpretation notes",
    "figure_interpretations_md": "Markdown per-figure result interpretation notes",
    "final_report": "Final Markdown report with methods, software versions, QC, and per-figure result interpretation",
    "reference_mvp_package_audit_tsv": "Machine-readable Reference MVP package audit enforcing MCScanX self intra-species and JCVI inter-species boundaries",
    "reference_mvp_package_audit_md": "Markdown Reference MVP package audit summary for the modular result package",
    "figure_traceability_matrix": "Final report Figure Traceability Matrix linking every registered plot to close-reading, QC, software, and reproducibility evidence",
}
OPTIONAL_KEYS = {
    "promoters_bed",
    "promoters_fasta",
    "plantcare_submission_manifest",
    "plantcare_submission_status",
    "promoter_cis_elements",
    "promoter_cis_gene_matrix",
    "promoter_cis_gene_element_matrix",
    "promoter_cis_category_summary",
    "promoter_cis_element_annotations",
    "promoter_cis_pdf",
    "promoter_cis_png",
    "promoter1_pdf",
    "promoter1_png",
    "species_promoter2_pdf",
    "species_promoter2_png",
    "feature_summary",
    "feature_summary_pdf",
    "feature_summary_png",
    "circlize_link_density",
    "circlize_duplicate_type_tracks",
    "mcscanx_circlize_pdf",
    "mcscanx_circlize_png",
    "ppi_edges",
    "ppi_nodes",
    "ppi_hubs",
    "ppi_input_evidence",
    "ppi_network_qc",
    "ppi_node_annotation",
    "ppi_species_annotation",
    "ppi_overview_status",
    "ppi_ggnetview_status",
    "ppi_pdf",
    "ppi_png",
    "ppi_ggnetview_pdf",
    "ppi_ggnetview_png",
    "family_expression",
    "expression_sample_metadata",
    "expression_group_matrix",
    "expression_gene_summary",
    "expression_heatmap_pdf",
    "expression_heatmap_png",
    "wgd_layers",
    "kaks_failure_summary",
    "kaks_wgd_annotations",
    "wgd_event_evidence",
    "ks_distribution_pdf",
    "ks_distribution_png",
    "mcscanx_duplicate_types",
    "duplicate_type_kaks",
    "duplicate_type_kaks_summary",
    "duplicate_type_kaks_pdf",
    "duplicate_type_kaks_png",
    "figure_interpretations_md",
    "final_report",
    "reference_mvp_package_audit_tsv",
    "reference_mvp_package_audit_md",
    "figure_traceability_matrix",
}


def _traceability_anchor(final_report: str) -> str:
    return f"{final_report}#figure-traceability-matrix" if final_report else ""


def build_report_index(paths: dict[str, str]) -> list[dict[str, str]]:
    paths = dict(paths)
    for key in DESCRIPTIONS:
        paths.setdefault(key, "")
    paths["figure_traceability_matrix"] = paths.get("figure_traceability_matrix") or _traceability_anchor(paths.get("final_report", ""))
    return [
        {
            "key": key,
            "path": paths[key],
            "status": "available" if paths[key] else "missing",
            "description": DESCRIPTIONS[key],
        }
        for key in DESCRIPTIONS
    ]


def published_paths(
    published_outdir: str,
    family_expression_available: bool,
    promoter_available: bool = False,
    feature_summary_available: bool = False,
    promoter_cis_available: bool = False,
    mcscanx_circlize_available: bool = False,
    ppi_available: bool = False,
    wgd_available: bool = False,
) -> dict[str, str]:
    outdir = Path(published_outdir)
    return {
        "species_manifest": str(outdir / "tables/species_manifest.tsv"),
        "run_config_snapshot": str(outdir / "tables/run_config_snapshot.tsv"),
        "family_candidates": str(outdir / "tables/family_candidates.tsv"),
        "family_counts": str(outdir / "tables/family_counts.tsv"),
        "family_counts_pdf": str(outdir / "plots/family_counts.pdf"),
        "family_counts_png": str(outdir / "plots/family_counts.png"),
        "family_members_faa": str(outdir / "sequences/family_members.faa"),
        "gene_family_copy_number": str(outdir / "tables/gene_family_copy_number.tsv"),
        "gene_family_copy_number_summary": str(outdir / "tables/gene_family_copy_number_summary.tsv"),
        "gene_family_species_order": str(outdir / "tables/gene_family_species_order.tsv"),
        "gene_family_copy_number_expansion": str(outdir / "tables/gene_family_copy_number_expansion.tsv"),
        "gene_family_pangenome_summary": str(outdir / "tables/gene_family_pangenome_summary.tsv"),
        "gene_family_protein_properties": str(outdir / "tables/gene_family_protein_properties.tsv"),
        "gene_family_info_pdf": str(outdir / "plots/gene_family_info_summary.pdf"),
        "gene_family_info_png": str(outdir / "plots/gene_family_info_summary.png"),
        "alignment_manifest": str(outdir / "tables/alignment_manifest.tsv"),
        "alignment_file": str(outdir / "alignment/GDSL.mafft.aln.faa"),
        "phylogeny_manifest": str(outdir / "tables/phylogeny_manifest.tsv"),
        "phylogeny_tree": str(outdir / "phylogeny/GDSL.fasttree.treefile"),
        "motif_summary": str(outdir / "tables/motif_summary.tsv"),
        "gene_structure_summary": str(outdir / "tables/gene_structure_summary.tsv"),
        "tree_feature_matrix": str(outdir / "tables/tree_feature_matrix.tsv"),
        "tree_features_pdf": str(outdir / "plots/tree_features.pdf"),
        "tree_features_png": str(outdir / "plots/tree_features.png"),
        "chromosome_locations": str(outdir / "tables/chromosome_locations.tsv"),
        "promoters_bed": str(outdir / "tables/promoters.bed") if promoter_available else "",
        "promoters_fasta": str(outdir / "sequences/promoters.fa") if promoter_available else "",
        "plantcare_submission_manifest": str(outdir / "plantcare_submission/plantcare_submission_manifest.tsv") if promoter_available else "",
        "plantcare_submission_status": str(outdir / "plantcare_submission/plantcare_submission_status.tsv") if promoter_available else "",
        "promoter_cis_elements": str(outdir / "tables/promoter_cis_elements.tsv") if promoter_cis_available else "",
        "promoter_cis_gene_matrix": str(outdir / "tables/promoter_cis_gene_matrix.tsv") if promoter_cis_available else "",
        "promoter_cis_gene_element_matrix": str(outdir / "tables/promoter_cis_gene_element_matrix.tsv") if promoter_cis_available else "",
        "promoter_cis_category_summary": str(outdir / "tables/promoter_cis_category_summary.tsv") if promoter_cis_available else "",
        "promoter_cis_element_annotations": str(outdir / "tables/promoter_cis_element_annotations.tsv") if promoter_cis_available else "",
        "promoter_cis_pdf": str(outdir / "plots/promoter_cis_elements.pdf") if promoter_cis_available else "",
        "promoter_cis_png": str(outdir / "plots/promoter_cis_elements.png") if promoter_cis_available else "",
        "promoter1_pdf": str(outdir / "plots/promoter1.pdf") if promoter_cis_available else "",
        "promoter1_png": str(outdir / "plots/promoter1.png") if promoter_cis_available else "",
        "species_promoter2_pdf": str(outdir / "plots/species_promoter2.pdf") if promoter_cis_available else "",
        "species_promoter2_png": str(outdir / "plots/species_promoter2.png") if promoter_cis_available else "",
        "feature_summary": str(outdir / "tables/feature_summary.tsv") if feature_summary_available else "",
        "feature_summary_pdf": str(outdir / "plots/feature_summary.pdf") if feature_summary_available else "",
        "feature_summary_png": str(outdir / "plots/feature_summary.png") if feature_summary_available else "",
        "circlize_link_density": str(outdir / "tables/circlize_link_density.tsv") if mcscanx_circlize_available else "",
        "circlize_duplicate_type_tracks": str(outdir / "tables/circlize_duplicate_type_tracks.tsv") if mcscanx_circlize_available else "",
        "mcscanx_circlize_pdf": str(outdir / "plots/mcscanx_circlize.pdf") if mcscanx_circlize_available else "",
        "mcscanx_circlize_png": str(outdir / "plots/mcscanx_circlize.png") if mcscanx_circlize_available else "",
        "ppi_edges": str(outdir / "tables/ppi_edges.tsv") if ppi_available else "",
        "ppi_nodes": str(outdir / "tables/ppi_nodes.tsv") if ppi_available else "",
        "ppi_hubs": str(outdir / "tables/ppi_hubs.tsv") if ppi_available else "",
        "ppi_input_evidence": str(outdir / "tables/ppi_input_evidence.tsv") if ppi_available else "",
        "ppi_network_qc": str(outdir / "tables/ppi_network_qc.tsv") if ppi_available else "",
        "ppi_node_annotation": str(outdir / "tables/node_annotation.tsv") if ppi_available else "",
        "ppi_species_annotation": str(outdir / "tables/species_ppi_annotation.tsv") if ppi_available else "",
        "ppi_overview_status": str(outdir / "tables/ppi_overview_status.tsv") if ppi_available else "",
        "ppi_ggnetview_status": str(outdir / "tables/ppi_ggnetview_status.tsv") if ppi_available else "",
        "ppi_pdf": str(outdir / "plots/ppi.pdf") if ppi_available else "",
        "ppi_png": str(outdir / "plots/ppi.png") if ppi_available else "",
        "ppi_ggnetview_pdf": str(outdir / "plots/ppi_ggnetview.pdf") if ppi_available else "",
        "ppi_ggnetview_png": str(outdir / "plots/ppi_ggnetview.png") if ppi_available else "",
        "family_expression": str(outdir / "tables/family_expression.tsv") if family_expression_available else "",
        "expression_sample_metadata": str(outdir / "tables/expression_sample_metadata.tsv") if family_expression_available else "",
        "expression_group_matrix": str(outdir / "tables/expression_group_matrix.tsv") if family_expression_available else "",
        "expression_gene_summary": str(outdir / "tables/expression_gene_summary.tsv") if family_expression_available else "",
        "expression_heatmap_pdf": str(outdir / "plots/expression_heatmap.pdf") if family_expression_available else "",
        "expression_heatmap_png": str(outdir / "plots/expression_heatmap.png") if family_expression_available else "",
        "wgd_handoff_manifest": str(outdir / "tables/wgd_handoff_manifest.tsv"),
        "kaks_failure_summary": str(outdir / "kaks_inputs/kaks_failure_summary.tsv") if wgd_available else "",
        "wgd_layers": str(outdir / "tables/wgd_layers.tsv") if wgd_available else "",
        "kaks_wgd_annotations": str(outdir / "tables/kaks_wgd_annotations.tsv") if wgd_available else "",
        "wgd_event_evidence": str(outdir / "tables/wgd_event_evidence.tsv") if wgd_available else "",
        "ks_distribution_pdf": str(outdir / "plots/ks_distribution.pdf") if wgd_available else "",
        "ks_distribution_png": str(outdir / "plots/ks_distribution.png") if wgd_available else "",
        "mcscanx_duplicate_types": str(outdir / "tables/mcscanx_duplicate_types.tsv") if wgd_available else "",
        "duplicate_type_kaks": str(outdir / "tables/duplicate_type_kaks.tsv") if wgd_available else "",
        "duplicate_type_kaks_summary": str(outdir / "tables/duplicate_type_kaks_summary.tsv") if wgd_available else "",
        "duplicate_type_kaks_pdf": str(outdir / "plots/duplicate_type_kaks.pdf") if wgd_available else "",
        "duplicate_type_kaks_png": str(outdir / "plots/duplicate_type_kaks.png") if wgd_available else "",
        "plot_manifest": str(outdir / "report/plot_manifest.tsv"),
        "software_versions": str(outdir / "report/software_versions.tsv"),
        "figure_interpretations": str(outdir / "report/figure_interpretations.tsv"),
        "figure_interpretations_md": str(outdir / "report/figure_interpretations.md"),
        "final_report": str(outdir / "report/final_report.md"),
        "reference_mvp_package_audit_tsv": str(outdir / "report/reference_mvp_package_audit.tsv"),
        "reference_mvp_package_audit_md": str(outdir / "report/reference_mvp_package_audit.md"),
        "figure_traceability_matrix": _traceability_anchor(str(outdir / "report/final_report.md")),
    }


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def status_file_allows_available(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    unavailable_statuses = ("missing_input", "skipped_optional", "missing_dependency")
    return not any(status in text for status in unavailable_statuses)


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in DESCRIPTIONS:
        parser.add_argument(f"--{key.replace('_', '-')}", default="", required=key not in OPTIONAL_KEYS)
    parser.add_argument("--promoter-cis-status", default="")
    parser.add_argument("--expression-status", default="")
    parser.add_argument("--published-outdir", default=None)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paths = {key: getattr(args, key) for key in DESCRIPTIONS}
    paths["figure_traceability_matrix"] = paths["figure_traceability_matrix"] or _traceability_anchor(paths["final_report"])
    if args.published_outdir:
        published_outdir = Path(args.published_outdir)
        promoter_cis_status = Path(args.promoter_cis_status) if args.promoter_cis_status else published_outdir / "tables" / "promoter_cis_status.tsv"
        expression_status = Path(args.expression_status) if args.expression_status else published_outdir / "tables" / "expression_status.tsv"
        promoter_cis_available = bool(
            paths["promoter_cis_elements"] or paths["promoter_cis_category_summary"] or paths["promoter_cis_pdf"]
        ) and status_file_allows_available(promoter_cis_status)
        family_expression_available = bool(paths["family_expression"]) and status_file_allows_available(expression_status)
        paths = published_paths(
            args.published_outdir,
            family_expression_available=family_expression_available,
            promoter_available=bool(paths["promoters_bed"] or paths["promoters_fasta"]),
            promoter_cis_available=promoter_cis_available,
            feature_summary_available=bool(paths["feature_summary"] or paths["feature_summary_pdf"] or paths["feature_summary_png"]),
            mcscanx_circlize_available=bool(paths["mcscanx_circlize_pdf"] or paths["mcscanx_circlize_png"]),
            ppi_available=bool(paths["ppi_edges"] or paths["ppi_ggnetview_status"] or paths["ppi_ggnetview_pdf"]),
            wgd_available=bool(paths["wgd_layers"] or paths["wgd_event_evidence"] or paths["ks_distribution_pdf"]),
        )
    write_tsv(build_report_index(paths), args.out)


if __name__ == "__main__":
    main()
