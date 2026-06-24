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

Create or update the local environment from:

```bash
conda env create -f envs/GeneFamilyFlow.conda.yaml
conda activate GeneFamilyFlow
```

The environment file includes Python, R, workflow dependencies, and common bioinformatics tools used by the pipeline modules.
It also includes `openjdk` and `nextflow` so the local Conda route can run the workflow engine from the same `GeneFamilyFlow` environment.
On macOS arm64, `jcvi` and `kaks_calculator` are not available from the current Conda channels, so they are kept out of the local cross-platform environment file.

Update an existing environment with:

```bash
conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune
```

## Linux And Container Environment

Linux and Docker builds use the fuller environment file:

```bash
conda env create -f envs/GeneFamilyFlow.linux-64.conda.yaml
```

This file keeps platform-limited tools such as `jcvi` and `kaks_calculator` for containerized or Linux execution.

Generate a machine-specific bootstrap plan from the readiness TSV:

```bash
python bin/genefam/audit_readiness.py --conda-env GeneFamilyFlow --out results/readiness/command_readiness.tsv
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

Docker smoke verifier:

```bash
python bin/genefam/run_container_profile_smoke.py --profile docker \
  --conda-env GeneFamilyFlow \
  --outdir results/container_profile_smoke/docker
```

Apptainer execution:

```bash
nextflow run workflows/main.nf \
  -c workflows/nextflow.config \
  -profile apptainer \
  --config configs/example.config.yaml
```

Apptainer smoke verifier:

```bash
python bin/genefam/run_container_profile_smoke.py --profile apptainer \
  --conda-env GeneFamilyFlow \
  --outdir results/container_profile_smoke/apptainer
```

The container smoke verifier writes:

- `results/container_profile_smoke/docker/container_profile_smoke.tsv`
- `results/container_profile_smoke/docker/container_profile_smoke.md`
- `results/container_profile_smoke/apptainer/container_profile_smoke.tsv`
- `results/container_profile_smoke/apptainer/container_profile_smoke.md`

## Current Verification Boundary

The Python helpers and mock MVP can be tested without external tools. Full Nextflow and external-tool execution requires Nextflow plus the tools from `GeneFamilyFlow` to be installed or available through Docker/Apptainer.
