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
        "conda run -n GeneFamilyFlow iqtree2 --version",
        "conda run -n GeneFamilyFlow meme -version",
        "/usr/local/bin/R --version",
        "docker build -t genefam-pipeline:latest .",
        "python bin/genefam/run_release_checks.py --outdir results/release_checks",
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
            "The local environment includes Nextflow, OpenJDK, R packages, HMMER, DIAMOND, MAFFT, IQ-TREE, MEME, and related helpers available on the current platform.",
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
            "Apptainer users can build from the Docker image or use the `apptainer` profile in `workflows/nextflow.config`.",
            "",
            "## Verification",
            "",
            "```bash",
            "python bin/genefam/run_release_checks.py --outdir results/release_checks",
            "```",
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
