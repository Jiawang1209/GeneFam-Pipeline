# Runtime Environment

GeneFam-Pipeline uses one shared runtime name:

```text
GeneFamilyFlow
```

R-language steps should use:

```text
/usr/local/bin/R
```

## Conda

Create the environment from:

```bash
conda env create -f envs/GeneFamilyFlow.conda.yaml
conda activate GeneFamilyFlow
```

The environment file includes Python, R, workflow dependencies, and common bioinformatics tools used by the pipeline modules.
It also includes `openjdk` and `nextflow` so the local Conda route can run the workflow engine from the same `GeneFamilyFlow` environment.

Update an existing environment with:

```bash
conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune
```

Generate a machine-specific bootstrap plan from the readiness TSV:

```bash
python bin/genefam/audit_readiness.py --out results/readiness/command_readiness.tsv
python bin/genefam/plan_runtime_bootstrap.py \
  --readiness results/readiness/command_readiness.tsv \
  --outdir results/readiness
```

This writes:

- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`

## Docker

Build the local image:

```bash
docker build -t genefam-pipeline:latest .
```

The Docker image creates the `GeneFamilyFlow` environment and links:

```text
/usr/local/bin/R -> /opt/conda/envs/GeneFamilyFlow/bin/R
```

This preserves the project-wide R binary contract inside the container.

## Nextflow Profiles

Local conda execution:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile local \
  --config configs/example.config.yaml
```

Docker execution:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile docker \
  --config configs/example.config.yaml
```

Apptainer execution:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile apptainer \
  --config configs/example.config.yaml
```

## Current Verification Boundary

The Python helpers and mock MVP can be tested without external tools. Full Nextflow and external-tool execution requires Nextflow plus the tools from `GeneFamilyFlow` to be installed or available through Docker/Apptainer.
