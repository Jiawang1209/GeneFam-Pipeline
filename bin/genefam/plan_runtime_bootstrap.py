#!/usr/bin/env python3
"""Generate an actionable runtime bootstrap plan from a readiness TSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_readiness_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {
                "command": row.get("command", ""),
                "status": row.get("status", ""),
                "path": row.get("path", ""),
            }
            for row in csv.DictReader(handle, delimiter="\t")
        ]


def _missing_commands(rows: list[dict[str, str]]) -> list[str]:
    return [row["command"] for row in rows if row["status"] == "missing"]


def build_bootstrap_plan(rows: list[dict[str, str]]) -> dict[str, str]:
    missing = _missing_commands(rows)
    missing_text = ", ".join(missing) if missing else "none"
    shell_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune",
        "conda run -n GeneFamilyFlow python bin/genefam/validate_config.py configs/example.config.yaml",
        "conda run -n GeneFamilyFlow nextflow -version",
        "conda run -n GeneFamilyFlow hmmsearch -h >/dev/null",
        "conda run -n GeneFamilyFlow diamond version",
        "conda run -n GeneFamilyFlow mafft --version >/dev/null",
        "conda run -n GeneFamilyFlow FastTree -expert >/dev/null",
        "conda run -n GeneFamilyFlow iqtree2 --version || conda run -n GeneFamilyFlow iqtree --version",
        "conda run -n GeneFamilyFlow meme -version",
        "/usr/local/bin/R --version",
        "docker build -t genefam-pipeline:latest .",
        'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest',
        "apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest",
        "apptainer build --force genefam-pipeline_latest.sif Apptainer.def",
        "python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker",
        "python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer",
        "python bin/genefam/run_release_checks.py --outdir results/release_checks",
        "bash scripts/run_local_acceptance.sh",
    ]
    markdown = "\n".join(
        [
            "# Runtime Bootstrap Plan",
            "",
            f"Missing commands: {missing_text}",
            "",
            "## Primary Path",
            "",
            "Refresh the shared local `GeneFamilyFlow` Conda environment from `envs/GeneFamilyFlow.conda.yaml`.",
            "The local environment includes Nextflow, OpenJDK, R packages, HMMER, DIAMOND, MAFFT, FastTree, IQ-TREE, MEME, and related helpers available on the current platform.",
            "IQ-TREE verification accepts either `iqtree2` or the `iqtree` alias used by some Conda builds.",
            "",
            "```bash",
            "conda env update -n GeneFamilyFlow -f envs/GeneFamilyFlow.conda.yaml --prune",
            "```",
            "",
            "R steps continue to use `/usr/local/bin/R`; inside Docker this path is linked to the `GeneFamilyFlow` R binary.",
            "",
            "## Container Path",
            "",
            "Linux and Docker builds use `envs/GeneFamilyFlow.linux-64.conda.yaml` so platform-limited tools such as `jcvi` and `kaks_calculator` stay available in the container route.",
            "",
            "Build the reproducible Docker image after the Conda environment file changes:",
            "",
            "```bash",
            "docker build -t genefam-pipeline:latest .",
            "```",
            "",
            "Run the Docker image default standard smoke. It writes `results/container_default_smoke` through the mounted results directory:",
            "",
            "```bash",
            'docker run --rm -v "$PWD/results:/opt/GeneFam-Pipeline/results" genefam-pipeline:latest',
            "```",
            "",
            "Build the local Apptainer SIF from that Docker image when Apptainer is available:",
            "",
            "```bash",
            "apptainer build --force genefam-pipeline_latest.sif docker-daemon://genefam-pipeline:latest",
            "```",
            "",
            "Build the same SIF through the Reference-safe Apptainer-native definition when Docker daemon access is unavailable or not preferred:",
            "",
            "```bash",
            "apptainer build --force genefam-pipeline_latest.sif Apptainer.def",
            "```",
            "",
            "The Nextflow profiles use `params.container_image` and `params.apptainer_image`; defaults are `genefam-pipeline:latest` and `genefam-pipeline_latest.sif`.",
            "",
            "## Verification",
            "",
            "Verify each container profile directly before rerunning the full release gate:",
            "",
            "```bash",
            "python bin/genefam/run_container_profile_smoke.py --profile docker --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/docker",
            "python bin/genefam/run_container_profile_smoke.py --profile apptainer --conda-env GeneFamilyFlow --outdir results/container_profile_smoke/apptainer",
            "```",
            "",
            "```bash",
            "python bin/genefam/run_release_checks.py --outdir results/release_checks",
            "```",
            "",
            "After the runtime gap is closed, rerun the local acceptance wrapper so the handoff report and delivery bundle are refreshed from the same evidence set:",
            "",
            "```bash",
            "bash scripts/run_local_acceptance.sh",
            "```",
            "",
            "Open `results/delivery_bundle/delivery_bundle.md` as the final user-facing index after that pass.",
            "",
        ]
    )
    return {"markdown": markdown, "shell": "\n".join(shell_lines) + "\n"}


def write_bootstrap_outputs(plan: dict[str, str], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "runtime_bootstrap_plan.md").write_text(plan["markdown"], encoding="utf-8")
    shell_path = outdir / "runtime_bootstrap.sh"
    shell_path.write_text(plan["shell"], encoding="utf-8")
    shell_path.chmod(0o755)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readiness", required=True, type=Path)
    parser.add_argument("--outdir", default=Path("results/readiness"), type=Path)
    args = parser.parse_args()
    rows = read_readiness_tsv(args.readiness)
    write_bootstrap_outputs(build_bootstrap_plan(rows), args.outdir)


if __name__ == "__main__":
    main()
