# Duplication Retention Design

This module adds an evolution-aware layer to the gene family pipeline.

## What Can Be Automated

The pipeline can automatically compute or infer:

- duplicate type classification: singleton, dispersed, proximal, tandem, WGD/segmental
- syntenic duplicated gene pairs
- Ka, Ks, and Ka/Ks values when CDS files are available
- anonymous WGD layers from configured Ks bins or detected Ks peaks
- gene family enrichment against whole-genome duplicate type backgrounds

## What Requires Evidence-Backed Annotation

Historical event names such as gamma, beta, alpha, and theta are not raw outputs of MCScanX or Ka/Ks tools. They are literature-backed interpretations of WGD/WGT layers.

The pipeline must not label a layer as gamma, beta, alpha, or theta unless one of these is provided:

- a known event map
- a species-specific literature configuration
- a validated block-to-event table

Without this evidence, reports should use neutral labels:

```text
WGD_layer_1
WGD_layer_2
WGD_layer_3
```

## Outputs

Planned outputs:

```text
tables/duplicate_gene_classification.tsv
tables/wgd_layers.tsv
tables/wgd_event_evidence.tsv
tables/retention_enrichment.tsv
plots/ks_density.pdf
plots/duplication_type_barplot.pdf
```

## Interpretation Rule

The report should separate observation from interpretation:

- Observation: this family is enriched for WGD/segmental duplicates.
- Inference: this family has multiple Ks-supported WGD layers.
- Named interpretation: this layer is alpha or theta only when configured evidence supports it.

See `docs/wgd_event_evidence.md` for the concrete event evidence table contract.

## Retention Enrichment

`bin/genefam/retention_enrichment.py` compares the duplicate type distribution of family members against a whole-genome duplicate classification background.

Inputs:

- family duplicate table with `duplicate_type`
- background duplicate table with `duplicate_type`

Output:

```text
tables/retention_enrichment.tsv
```

Columns:

- `duplicate_type`
- `family_count`
- `family_total`
- `background_count`
- `background_total`
- `fold_enrichment`
- `p_value`
