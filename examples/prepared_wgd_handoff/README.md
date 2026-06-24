# Prepared WGD Handoff Example

This folder is a minimal copyable example for running the duplication and WGD event branch after family identification.

In a real run, `family_candidates.tsv` usually comes from:

```text
results/<run>/tables/family_candidates.tsv
```

The two prepared downstream tables are:

- `duplicate_types.tsv`: duplicate classifications from MCScanX, DupGen_finder, JCVI/SynMap-style preprocessing, or a curated genome-wide duplicate table.
- `kaks_pairs.tsv`: pair-level Ks values from KaKs_Calculator, PAML, or another Ka/Ks workflow.

Run the example through Nextflow:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  --config configs/example.config.yaml \
  --run_duplication_retention true \
  --duplicates examples/prepared_wgd_handoff/duplicate_types.tsv \
  --family_members examples/prepared_wgd_handoff/family_candidates.tsv \
  --kaks_pairs examples/prepared_wgd_handoff/kaks_pairs.tsv \
  --events_config configs/wgd_events.brassicaceae.yaml \
  --ks_bins 0.3,0.8,1.5 \
  --wgd_event_args "--event WGD_layer_1=alpha --event WGD_layer_2=beta --event WGD_layer_3=gamma --event WGD_layer_4=theta" \
  --outdir results/example_prepared_wgd
```

Expected outputs include:

```text
results/example_prepared_wgd/tables/wgd_layers.tsv
results/example_prepared_wgd/tables/wgd_event_evidence.tsv
results/example_prepared_wgd/tables/family_event_retention_summary.tsv
results/example_prepared_wgd/tables/retention_enrichment.tsv
results/example_prepared_wgd/report/final_report.md
```

The `wgd_event_evidence.tsv` table should contain alpha, beta, gamma, and theta event names when `configs/wgd_events.brassicaceae.yaml` and the command above are used.
