# WGD Event Evidence Model

GeneFam-Pipeline separates WGD evidence into three layers.

## Observed

Observed evidence comes from data products:

- syntenic duplicate gene pairs
- collinear blocks
- Ks values for duplicated pairs
- duplicate type labels such as WGD/segmental, tandem, proximal, dispersed, and singleton

These are computational outputs.

## Inferred

Anonymous WGD layers are inferred from Ks bins or Ks peaks:

```text
WGD_layer_1
WGD_layer_2
WGD_layer_3
```

These layers are allowed even without historical event names.

## Interpreted

Names such as `gamma`, `beta`, `alpha`, and `theta` are interpreted labels. They require a configuration or literature-backed event map.

The pipeline must not automatically rename a layer to one of these events unless the event metadata is supplied.

WGD event names must be unique within the event YAML. Duplicate names are rejected so one biological event label cannot silently overwrite another scope or expected age.

WGD event metadata requires name, scope, evidence, and expected_relative_age for every configured event.

Example:

```bash
python bin/genefam/classify_wgd_layers.py \
  --pairs duplicated_pairs_kaks.tsv \
  --bins 0.3,0.8,1.5 \
  --event WGD_layer_1=alpha \
  --event WGD_layer_2=beta \
  --event WGD_layer_3=gamma \
  --out wgd_layers.tsv

python bin/genefam/build_wgd_event_evidence.py \
  --classified-pairs wgd_layers.tsv \
  --events-config configs/wgd_events.brassicaceae.yaml \
  --out wgd_event_evidence.tsv
```

The event evidence table reports:

- `wgd_layer`
- `pair_count`
- `ks_min`
- `ks_median`
- `ks_max`
- `event_name`
- `interpretation_status`
- `evidence_source`
- `species_scope`
- `expected_relative_age`

This keeps the report honest: Ks and synteny support layers; literature/configuration supports event names.
