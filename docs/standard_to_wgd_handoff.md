# Standard To WGD Handoff

This guide connects the standard identification branch to the duplication and WGD event branch. Use it when a gene family has been identified and you want gamma, beta, alpha, theta, or other named-event retention evidence from prepared MCScanX and Ka/Ks tables.

## Step 1: Run Family Identification

Run the standard branch on the selected species bank:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_identification true \
  --final_rule intersection \
  --outdir results/<run>
```

The handoff file for the next branch is:

```text
results/<run>/tables/family_candidates.tsv
```

It contains the family member gene IDs used by chromosome mapping, expression subsetting, and duplication-retention analysis.

## Step 2: Prepare Duplication Inputs

The WGD branch expects prepared intermediate tables. These can come from MCScanX, JCVI/SynMap-style preprocessing, KaKs_Calculator, or curated tables as long as they are normalized to the contracts below.

Duplicate type table:

```text
gene_id
duplicate_type
```

Accepted `duplicate_type` values are normalized by `bin/genefam/normalize_duplicate_types.py` into:

```text
WGD/segmental
tandem
proximal
dispersed
singleton
```

Ka/Ks pair table:

```text
gene_a
gene_b
ks
```

The `ks` values define anonymous WGD layers first. Named events such as gamma, beta, alpha, and theta are then assigned through `--wgd_event_args` and `configs/wgd_events.brassicaceae.yaml`.

## Step 3: Run The WGD Branch

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --duplicates path/to/duplicate_types.tsv \
  --family_members results/<run>/tables/family_candidates.tsv \
  --kaks_pairs path/to/kaks_pairs.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta" \
  --outdir results/<run>_wgd
```

The key outputs are:

```text
results/<run>_wgd/tables/wgd_layers.tsv
results/<run>_wgd/tables/wgd_event_evidence.tsv
results/<run>_wgd/tables/family_wgd_event_membership.tsv
results/<run>_wgd/tables/family_event_retention_summary.tsv
results/<run>_wgd/tables/retention_enrichment.tsv
results/<run>_wgd/report/final_report.md
```

`wgd_event_evidence.tsv` is the layer-level evidence table for gamma, beta, alpha, theta, or any other configured event names. `family_event_retention_summary.tsv` reports how many family members are retained in each named event. `retention_enrichment.tsv` compares duplicate-type retention in the family against the background duplicate table.

## Smoke Test

Use the Nextflow WGD smoke to verify the branch without external MCScanX or Ka/Ks tools:

```bash
python bin/genefam/run_nextflow_wgd_smoke.py --conda-env GeneFamilyFlow --outdir results/nextflow_wgd_smoke
```

The smoke writes:

```text
results/nextflow_wgd_smoke/wgd/tables/wgd_event_evidence.tsv
results/nextflow_wgd_smoke/wgd/report/final_report.md
```

It validates that the Nextflow branch emits configured gamma, beta, alpha, and theta evidence and publishes a report.
