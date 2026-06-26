#!/usr/bin/env python3
"""Build structured figure-reading notes for completion reports."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = [
    "figure_key",
    "title",
    "input_data",
    "what_figure_shows",
    "key_observations",
    "biological_interpretation",
    "qc_warnings",
    "qc_tables",
    "method_and_software",
    "reproducibility",
    "result_reading_status",
    "output_path",
]


TEMPLATES = {
    "family": (
        "Family copy number and member count overview",
        "Family member count table",
        "Per-species gene family member counts and copy-number differences.",
        "Inspect the highest and lowest member counts and whether related species share similar copy-number patterns.",
        "Species with larger counts may indicate lineage-specific expansion or contraction relative to the sampled set.",
    ),
    "mcscanx": (
        "MCScanX syntenic relationship overview",
        "MCScanX syntenic pair table and chromosome coordinates",
        "syntenic block links among family members and their chromosome positions.",
        "Inspect dense link clusters, skipped links, and chromosome-specific concentration of duplicated genes.",
        "Conserved syntenic block structure supports segmental/WGD-derived relationships when paired with Ks evidence.",
    ),
    "kaks": (
        "Ka/Ks and Ks distribution overview",
        "Normalized Ka/Ks pair table",
        "Ks distribution, Ka/Ks ratios, and WGD layer support for duplicated gene pairs.",
        "Inspect Ks peaks, ratios above or below 1, and whether configured WGD layers are well separated.",
        "Ks-supported layers provide observational evidence; gamma/beta/alpha/theta labels remain configured interpretations.",
    ),
    "ks_distribution": (
        "Ks distribution and named WGD-layer support",
        "Normalized Ka/Ks pair table with configured WGD-layer intervals",
        "Genome-duplication pair Ks values, Ka/Ks ratios, and configured event windows used to support named WGD layers.",
        "Inspect the number of duplicated pairs inside each Ks interval, whether peaks are separated, and whether low-count layers should be treated cautiously.",
        "Ks-supported layers provide observational evidence; gamma/beta/alpha/theta labels are historical interpretations that must be reconciled with synteny and phylogeny.",
    ),
    "duplicate_type_kaks": (
        "Duplicate-type grouped Ka/Ks selection overview",
        "Duplicate classification table joined to normalized Ka/Ks pair metrics",
        "Ka/Ks and Ks distributions grouped by WGD, tandem, proximal, transposed, or dispersed duplicate classes.",
        "Inspect whether WGD-derived pairs differ from local duplicate classes in Ks age, Ka/Ks ratio, and pair count support.",
        "Duplicate-type contrasts help separate WGD retention from local duplication dynamics and highlight classes with possible relaxed or purifying selection.",
    ),
    "pangenome_kaks": (
        "Pangenome-class grouped Ka/Ks selection overview",
        "Pangenome class table joined to normalized Ka/Ks pair metrics",
        "Ka/Ks and Ks distributions grouped by core, soft-core, dispensable, and private gene-pair classes.",
        "Inspect whether broadly retained classes have lower Ka/Ks values than dispensable/private classes and whether each class has enough pairs.",
        "Pangenome-class contrasts connect retention breadth with selection pressure and can flag dosage-sensitive conserved genes versus lineage-variable candidates.",
    ),
    "expression": (
        "Expression heatmap",
        "Family expression matrix and sample metadata",
        "Expression variation among family members across tissues, treatments, or time points.",
        "Inspect co-expression clusters, treatment-specific responses, and low-expression genes.",
        "Clustered expression patterns can suggest functional divergence or conserved regulatory responses.",
    ),
    "promoter": (
        "Promoter cis-element summary",
        "Promoter BED/FASTA and cis-element annotation table",
        "Promoter lengths and cis-element category abundance across genes or species.",
        "Inspect enriched stress, hormone, light, and development-related element classes.",
        "Cis-element differences suggest candidate regulatory divergence that should be validated experimentally.",
    ),
    "ppi": (
        "PPI network generated with ggNetView",
        "PPI edge table and node annotation table",
        "Protein interaction network structure, node groups, and edge weights.",
        "Inspect hub genes, dense modules, isolated nodes, and whether hubs overlap key family members.",
        "Hub genes may represent candidate regulatory or functional interaction centers.",
    ),
    "pangenome": (
        "Gene family pangenome and copy-number balance",
        "Gene family copy-number, expansion, and pangenome presence summary tables",
        "Presence/absence breadth, copy-number dosage, expansion status, and protein-property distributions for the selected family.",
        "Inspect whether the family is core, soft-core, dispensable, or absent across selected species and whether high-copy species dominate dosage variation.",
        "Core families suggest broad conservation, while dispensable or lineage-expanded patterns can indicate ecological specialization, dosage tuning, or lineage-specific retention.",
    ),
    "feature": (
        "Feature summary overview",
        "Domain, motif, gene-structure, synteny, and promoter summary tables",
        "Aggregated feature counts and distributions for large gene families.",
        "Inspect outlier genes, dominant feature categories, and modules with missing evidence.",
        "Feature summaries help prioritize interpretable subsets when full per-gene figures are too dense.",
    ),
    "tree": (
        "Tree, motif, gene-structure, and domain composite",
        "Phylogenetic tree, motif summary, gene-structure table, and domain hit table",
        "Tree-ordered family members with aligned feature tracks for gene structure, domain evidence, and motif catalog statistics.",
        "Inspect whether clades share exon/CDS patterns, domain coverage, and motif catalog support.",
        "Conserved feature tracks within clades support structural conservation; divergent tracks can indicate subfunctionalization candidates.",
    ),
}


QC_TABLES = {
    "family": "tables/gene_family_copy_number.tsv; tables/gene_family_copy_number_summary.tsv; tables/gene_family_copy_number_expansion.tsv; tables/gene_family_protein_properties.tsv",
    "mcscanx": "tables/circlize_link_density.tsv; tables/circlize_duplicate_type_tracks.tsv; tables/circlize_skipped_links.tsv; tables/mcscanx_summary.tsv",
    "kaks": "tables/kaks_wgd_annotations.tsv; WGD Event Evidence table; tables/pangenome_kaks_summary.tsv; tables/duplicate_type_kaks_summary.tsv",
    "ks_distribution": "tables/kaks_wgd_annotations.tsv; WGD Event Evidence table; tables/kaks_pairs.tsv; tables/family_wgd_event_membership.tsv",
    "duplicate_type_kaks": "tables/duplicate_type_kaks.tsv; tables/duplicate_type_kaks_summary.tsv; tables/duplicate_type_kaks_skipped.tsv; tables/normalized_duplicate_types.tsv",
    "pangenome_kaks": "tables/pangenome_kaks.tsv; tables/pangenome_kaks_summary.tsv; tables/pangenome_kaks_skipped.tsv; tables/gene_family_pangenome_summary.tsv",
    "expression": "tables/expression_sample_metadata.tsv; tables/expression_group_matrix.tsv; tables/expression_gene_summary.tsv",
    "promoter": "tables/promoter_cis_category_summary.tsv; tables/promoter_cis_element_annotations.tsv; tables/promoter_cis_gene_element_matrix.tsv",
    "ppi": "tables/ppi_input_evidence.tsv; tables/ppi_network_qc.tsv; tables/ppi_hubs.tsv; tables/ppi_ggnetview_status.tsv",
    "pangenome": "tables/gene_family_copy_number.tsv; tables/gene_family_pangenome_summary.tsv; tables/gene_family_copy_number_expansion.tsv; tables/gene_family_protein_properties.tsv; tables/pangenome_kaks_summary.tsv",
    "feature": "tables/feature_summary.tsv; tables/domain_summary.tsv; tables/motif_summary.tsv; tables/gene_structure_summary.tsv",
    "tree": "tables/tree_feature_matrix.tsv; tables/domain_summary.tsv; tables/motif_summary.tsv; tables/gene_structure_summary.tsv",
}


METHOD_AND_SOFTWARE = {
    "family": "build_gene_family_info.py; plot_gene_family_info.R; /usr/local/bin/R; GeneFamilyFlow",
    "mcscanx": "MCScanX; build_circlize_inputs.py; plot_mcscanx_circlize.R; circlize; /usr/local/bin/R; GeneFamilyFlow",
    "kaks": "KaKs_Calculator/PAML-compatible Ka/Ks table; classify_wgd_layers.py; build_kaks_plot_annotations.py; plot_kaks.R; plot_pangenome_kaks.R; /usr/local/bin/R; GeneFamilyFlow",
    "ks_distribution": "KaKs_Calculator/PAML-compatible Ka/Ks table; classify_wgd_layers.py; build_kaks_plot_annotations.py; plot_kaks.R; /usr/local/bin/R; GeneFamilyFlow",
    "duplicate_type_kaks": "MCScanX duplicate classes; build_duplicate_type_kaks.py; plot_duplicate_type_kaks.R; /usr/local/bin/R; GeneFamilyFlow",
    "pangenome_kaks": "Gene-family pangenome classes; build_pangenome_kaks.py; plot_pangenome_kaks.R; /usr/local/bin/R; GeneFamilyFlow",
    "expression": "build_expression_summary.py; plot_expression_heatmap.R; pheatmap/ComplexHeatmap-compatible R output; /usr/local/bin/R; GeneFamilyFlow",
    "promoter": "extract_promoters.py; build_promoter_cis_elements.py; plot_promoter_cis_elements.R; /usr/local/bin/R; GeneFamilyFlow",
    "ppi": "build_ppi_tables.py; plot_ppi_ggnetview.R; ggNetView; /usr/local/bin/R; GeneFamilyFlow",
    "pangenome": "build_gene_family_info.py; build_pangenome_kaks_summary.py; plot_gene_family_info.R; plot_pangenome_kaks.R; /usr/local/bin/R; GeneFamilyFlow",
    "feature": "summarize_feature_tables.py; plot_feature_summary.R; /usr/local/bin/R; GeneFamilyFlow",
    "tree": "FastTree/IQ-TREE-compatible Newick input; build_tree_feature_matrix.py; plot_tree_features.R; /usr/local/bin/R; GeneFamilyFlow",
}


REPRODUCIBILITY = {
    "family": "python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke",
    "mcscanx": "python bin/genefam/run_mcscanx_circlize_smoke.py --r-bin /usr/local/bin/R --outdir results/mcscanx_circlize_smoke",
    "kaks": "python bin/genefam/run_kaks_wgd_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/kaks_wgd_plot_smoke",
    "ks_distribution": "python bin/genefam/run_kaks_wgd_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/kaks_wgd_plot_smoke",
    "duplicate_type_kaks": "python bin/genefam/run_duplicate_type_kaks_smoke.py --r-bin /usr/local/bin/R --outdir results/duplicate_type_kaks_smoke",
    "pangenome_kaks": "python bin/genefam/run_pangenome_kaks_smoke.py --r-bin /usr/local/bin/R --outdir results/pangenome_kaks_smoke",
    "expression": "python bin/genefam/run_expression_heatmap_smoke.py --expression tests/fixtures/expression/family_expression.tsv --metadata tests/fixtures/expression/sample_metadata.tsv --r-bin /usr/local/bin/R --outdir results/expression_heatmap_smoke",
    "promoter": "python bin/genefam/run_promoter_cis_smoke.py --r-bin /usr/local/bin/R --outdir results/promoter_cis_smoke",
    "ppi": "python bin/genefam/run_ppi_ggnetview_plot_smoke.py --r-bin /usr/local/bin/R --outdir results/ppi_ggnetview_plot_smoke",
    "pangenome": "python bin/genefam/run_gene_family_info_smoke.py --r-bin /usr/local/bin/R --outdir results/gene_family_info_smoke",
    "feature": "python bin/genefam/run_feature_summary_smoke.py --r-bin /usr/local/bin/R --outdir results/feature_summary_smoke",
    "tree": "python bin/genefam/run_tree_feature_smoke.py --r-bin /usr/local/bin/R --outdir results/tree_feature_smoke",
}


READING_STATUS = {
    "family": "template-guided close reading; validate copy-number calls, selected species, and family-member evidence before manuscript use",
    "mcscanx": "template-guided close reading; validate skipped links, chromosome coordinates, and MCScanX block evidence before manuscript use",
    "kaks": "template-guided close reading; validate Ks peak separation, pair counts, and configured WGD event metadata before naming gamma/beta/alpha/theta layers",
    "ks_distribution": "figure-specific close reading; validate Ks bin boundaries, event labels, pair counts, and synteny/phylogeny support before naming gamma/beta/alpha/theta layers",
    "duplicate_type_kaks": "figure-specific close reading; validate duplicate class assignments, skipped pairs, and per-class sample sizes before interpreting selection differences",
    "pangenome_kaks": "figure-specific close reading; validate pangenome class thresholds, skipped pairs, and class sample sizes before interpreting retention breadth",
    "expression": "template-guided close reading; validate sample metadata, normalization, and replicate structure before biological conclusions",
    "promoter": "template-guided close reading; validate promoter extraction window, motif source, and category mapping before regulatory conclusions",
    "ppi": "template-guided close reading; validate interaction evidence, hub ranking, and ggNetView status before network interpretation",
    "pangenome": "template-guided close reading; validate core/soft-core/dispensable thresholds, copy-number tables, and pangenome sampling before manuscript use",
    "feature": "template-guided close reading; validate source feature tables and large-family aggregation before prioritizing candidate genes",
    "tree": "template-guided close reading; validate tree topology, feature-table completeness, and motif/domain source evidence before clade interpretation",
}


def _template_key(plot_key: str, path: str) -> str:
    value = f"{plot_key} {path}".lower()
    for key in ["duplicate_type_kaks", "pangenome_kaks", "ks_distribution"]:
        if key in value:
            return key
    for key in ["mcscanx", "kaks", "expression", "promoter", "ppi", "pangenome", "tree", "feature", "family"]:
        if key in value or (key == "kaks" and "ks_" in value):
            return key
    return "feature"


def _qc_warning(path: str) -> str:
    if "smoke" in path or "fixtures" in path or "demo" in path:
        return "This figure is generated from smoke/demo data; do not treat it as a biological conclusion."
    return "Review input completeness, skipped rows, and module QC tables before biological interpretation."


def build_figure_interpretations(plots: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for plot in plots:
        key = plot.get("plot_key") or plot.get("key") or Path(plot.get("path", "")).stem
        path = plot.get("path", "")
        template_key = _template_key(key, path)
        template = TEMPLATES[template_key]
        rows.append(
            {
                "figure_key": key,
                "title": template[0],
                "input_data": template[1],
                "what_figure_shows": template[2],
                "key_observations": template[3],
                "biological_interpretation": template[4],
                "qc_warnings": _qc_warning(path),
                "qc_tables": QC_TABLES[template_key],
                "method_and_software": METHOD_AND_SOFTWARE[template_key],
                "reproducibility": REPRODUCIBILITY[template_key],
                "result_reading_status": READING_STATUS[template_key],
                "output_path": path,
            }
        )
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(rows: list[dict[str, str]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], out_path: Path) -> None:
    lines = ["# Figure Result Interpretations", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row['figure_key']}: {row['title']}",
                "",
                f"- Input data: {row['input_data']}",
                f"- What the figure shows: {row['what_figure_shows']}",
                f"- Key observations: {row['key_observations']}",
                f"- Biological interpretation: {row['biological_interpretation']}",
                f"- QC warnings / limitations: {row['qc_warnings']}",
                f"- QC tables: {row['qc_tables']}",
                f"- Method/software: {row['method_and_software']}",
                f"- Reproducibility: {row['reproducibility']}",
                f"- Result reading status: {row['result_reading_status']}",
                f"- Output path: `{row['output_path']}`",
                "",
            ]
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot-manifest", required=True, type=Path)
    parser.add_argument("--out-tsv", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    rows = build_figure_interpretations(read_tsv(args.plot_manifest))
    write_tsv(rows, args.out_tsv)
    write_markdown(rows, args.out_md)


if __name__ == "__main__":
    main()
