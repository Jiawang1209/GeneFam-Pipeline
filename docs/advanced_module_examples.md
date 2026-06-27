# Advanced Module Examples

`configs/advanced_modules.example.yaml` shows the minimal config changes needed to enable the advanced analysis surface:

- Ka/Ks selection pressure
- chromosome locations
- expression integration
- synteny
- promoter cis-element visualization
- MCScanX circlize visualization
- PPI visualization with ggNetView
- duplication-retention analysis
- named WGD event interpretation
- phylogeny and motif modules

Validate the example:

```bash
python bin/genefam/validate_config.py configs/advanced_modules.example.yaml
```

Generate an audit-friendly run plan:

```bash
python bin/genefam/build_run_plan.py \
  --config configs/advanced_modules.example.yaml \
  --out results/GDSL_advanced_example/tables/run_plan.tsv
```

Before running the full workflow, check local command availability:

```bash
python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv
```

The advanced example expects:

- `input.required.cds: true` for Ka/Ks.
- `input.required.gff3: true` for chromosome location.
- `input.required.genome: true` when promoter extraction or promoter cis-element analysis is enabled.
- `expression.matrix` for expression integration.
- `plotting.syntenic_pairs` for MCScanX + `circlize` visualization in the standard report branch.
- `promoter.cis_elements` for PlantCARE-style promoter cis-element plots.
- `ppi.edges` and optional `ppi.nodes` for ggNetView PPI plots.
- `modules.synteny: true` and `modules.kaks: true` before `modules.duplication_retention: true`.
- `wgd_events.named_event_annotation: true` with `wgd_events.event_map` for gamma/beta/alpha/theta labels.

The file uses placeholder data paths such as `data/species_bank`, `data/reference/GDSL_reference.pep.fa`, `data/expression/family_expression.tsv`, `data/mcscanx/syntenic_pairs.tsv`, `data/promoter/plantcare_cis_elements.tsv`, and `data/ppi/ppi_edges.tsv`. Replace these with project-specific files before real execution.
