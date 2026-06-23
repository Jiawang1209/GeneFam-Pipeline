# Reference Plotting Reuse

The `Reference/` directory is part of the design source for GeneFam-Pipeline. It contains paper-derived scripts and outputs that can guide plotting modules.

## Reuse Policy

Use reference scripts as templates, not as mutable pipeline code.

Allowed:

- Inspect reference R/Python scripts before implementing related plots.
- Reuse chart types, biological grouping logic, color strategies, and output concepts.
- Port useful logic into parameterized scripts under `scripts/`.
- Mention the reference source in comments when a pipeline script is adapted from a specific example.

Not allowed unless explicitly requested:

- Editing files under `Reference/`.
- Calling reference scripts directly as pipeline modules.
- Copying absolute paths from reference scripts.
- Preserving one-off species assumptions without moving them into configuration.

## Current Useful References

- `Reference/Long_Weixiong_20240323_1_GDSL/R/5.GeneFamily_Info.R`: gene family summary and species-tree adjacent plots.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/6.tree.R`: phylogenetic tree annotation.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/8.collinearity_kaks.R`: Ka/Ks distribution plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/9.mcscanx_KaKs.R`: MCScanX duplicate type plus Ka/Ks plotting.
- `Reference/Long_Weixiong_20240323_1_GDSL/R/12.rnaseq.R`: RNA-seq expression heatmaps.
- `Reference/Large-Scale Plant Genomic Identification and Analysis Uncover ASMT:COMT Copy Number Variation Driving Melatonin Dosage Balance./source_code/`: large-scale copy-number, synteny, and expression figure scripts.

## Implementation Rule

Every reusable plot script should expose a stable command interface:

```text
/usr/local/bin/R --vanilla --slave -f scripts/<plot>.R --args <input.tsv> <outdir>
```

Each script should write deterministic output names into the requested output directory.
