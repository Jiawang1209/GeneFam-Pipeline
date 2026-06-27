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
python bin/genefam/audit_container_materials.py \
  --outdir results/container_materials
```

This writes:

- `results/readiness/runtime_bootstrap_plan.md`
- `results/readiness/runtime_bootstrap.sh`
- `results/container_materials/container_materials.tsv`
- `results/container_materials/container_materials.md`

The container-materials audit is static: it verifies that the Dockerfile, `Apptainer.def`, Linux Conda environment, and Nextflow container profiles agree on `GeneFamilyFlow`, `/usr/local/bin/R`, and the configured Docker/Apptainer image names before a runtime engine is available.

## Docker

Build the local image:

```bash
docker build -t genefam-pipeline:latest .
```

Build a local Apptainer image from the Docker image when Apptainer is available:

```bash
apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest
```

Or build the SIF through the checked-in Apptainer-native definition:

```bash
apptainer build --force genefam-pipeline_latest.sif Apptainer.def
```

`Apptainer.def` is Reference-safe: it copies only `bin`, `configs`, `envs`, `workflows`, `schemas`, and `tests/fixtures` into `/opt/GeneFam-Pipeline`, so local `Reference/` PDFs, paper data, and plotting templates are not pulled into the SIF build context.

The Docker image creates the `GeneFamilyFlow` environment and links:

```text
/usr/local/bin/R -> /opt/conda/envs/GeneFamilyFlow/bin/R
```

This preserves the project-wide R binary contract inside the container.

The image default command runs `bin/genefam/run_standard_smoke.py` for the standard branch smoke and writes:

```text
results/container_default_smoke
```

Run the same default smoke after building the image:

```bash
docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest
```

That gives the image a lightweight in-image workflow check without requiring Docker-in-Docker or Apptainer inside the container.

Container image names are parameterized in `workflows/nextflow.config`:

```text
params.container_image = "genefam-pipeline:latest"
params.apptainer_image = "genefam-pipeline_latest.sif"
```

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
  --config configs/example.config.yaml \
  --container_image genefam-pipeline:latest
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
  --config configs/example.config.yaml \
  --apptainer_image genefam-pipeline_latest.sif
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

After the container runtime gap is closed and the profile smokes pass, run:

```bash
scripts/run_local_acceptance.sh
```

This refreshes `results/delivery_bundle/delivery_bundle.md` and the paired handoff outputs from the final local evidence set.

## Current Verification Boundary

The Python helpers and mock MVP can be tested without external tools. Full Nextflow and external-tool execution requires Nextflow plus the tools from `GeneFamilyFlow` to be installed or available through Docker/Apptainer.
