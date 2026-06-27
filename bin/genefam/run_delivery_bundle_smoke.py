#!/usr/bin/env python3
"""Smoke-test delivery bundle and global figure gallery generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_delivery_bundle import run_delivery_bundle


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_smoke(outdir: Path) -> dict[str, Path]:
    inputs = outdir / "inputs"
    release = inputs / "release_checks.tsv"
    objective = inputs / "objective_audit.tsv"
    readiness = inputs / "command_readiness.tsv"
    quickstart = inputs / "quickstart_summary.tsv"
    bundle = outdir / "delivery_bundle"

    write_text(
        release,
        "\n".join(
            [
                "check\trequired\tstatus\texit_code\tcommand\tnote",
                "quickstart handoff\ttrue\tpassed\t0\tquickstart\tstandard and WGD",
                "publication report audit\ttrue\tpassed\t0\tpublication\tstandard figures",
                "standard report index audit\ttrue\tpassed\t0\tstandard index\tstandard report index",
                "WGD publication report audit\ttrue\tpassed\t0\twgd publication\tWGD figures",
                "WGD report index audit\ttrue\tpassed\t0\twgd index\tWGD report index",
                "Docker profile smoke\tfalse\tfailed\t1\tdocker\tmissing runtime",
                "Apptainer profile smoke\tfalse\tfailed\t1\tapptainer\tmissing runtime",
            ]
        )
        + "\n",
    )
    write_text(
        objective,
        "\n".join(
            [
                "requirement\tstatus\tevidence\tnote",
                "final reports\tachieved\tstandard and WGD reports\tok",
                "Docker/Apptainer reproducibility\tblocked\treadiness\tmissing container runtimes",
            ]
        )
        + "\n",
    )
    write_text(
        readiness,
        "\n".join(
            [
                "command\tstatus\tpath",
                "nextflow\tavailable_in_conda\tGeneFamilyFlow:/bin/nextflow",
                "/usr/local/bin/R\tavailable\t/usr/local/bin/R",
                "docker\tmissing\t",
                "apptainer\tmissing\t",
            ]
        )
        + "\n",
    )
    write_text(
        quickstart,
        "\n".join(
            [
                "step\tstatus\tpath\tnote",
                "standard_branch_smoke\tpassed\tresults/quickstart/standard_smoke/report/final_report.md\tstandard",
                "prepared_wgd_handoff\tpassed\tresults/quickstart/example_prepared_wgd/report/final_report.md\twgd",
            ]
        )
        + "\n",
    )

    outputs = run_delivery_bundle(
        release_checks=release,
        objective_audit=objective,
        readiness=readiness,
        quickstart=quickstart,
        outdir=bundle,
    )
    gallery = outputs["figure_gallery"]
    manifest = outputs["delivery_manifest"]
    summary = outdir / "delivery_bundle_smoke.md"
    gallery_text = gallery.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")

    required_fragments = [
        "standard\ttree_features\tresults/nextflow_standard_feature_smoke/standard/plots/tree_features.pdf",
        "standard\tppi_ggnetview\tresults/nextflow_standard_feature_smoke/standard/plots/ppi_ggnetview.pdf",
        "wgd\tks_distribution\tresults/nextflow_wgd_smoke/wgd/plots/ks_distribution.pdf",
        "wgd\tduplicate_type_kaks\tresults/nextflow_wgd_smoke/wgd/plots/duplicate_type_kaks.pdf",
        "results/nextflow_standard_feature_smoke/standard/report/software_versions.tsv",
        "results/nextflow_wgd_smoke/wgd/report/software_versions.tsv",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in gallery_text]
    if "status\tfigure_gallery\tavailable" not in manifest_text:
        missing.append("delivery manifest figure_gallery row")
    status = "passed" if not missing else "failed"

    lines = [
        "# Delivery Bundle Figure Gallery Smoke",
        "",
        f"Status: {status}",
        f"Delivery bundle: {outputs['delivery_bundle']}",
        f"Delivery manifest: {manifest}",
        f"Figure gallery TSV: {gallery}",
        f"Figure gallery Markdown: {outputs['figure_gallery_md']}",
        "",
        "Checked entries: tree_features, ppi_ggnetview, ks_distribution, duplicate_type_kaks, and software version links.",
    ]
    if missing:
        lines.extend(["", "Missing:"] + [f"- {item}" for item in missing])
    write_text(summary, "\n".join(lines) + "\n")
    if missing:
        raise SystemExit(1)
    return {**outputs, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default=Path("results/delivery_bundle_smoke"), type=Path)
    args = parser.parse_args()
    outputs = run_smoke(args.outdir)
    print("output\tpath")
    for key, path in sorted(outputs.items()):
        print(f"{key}\t{path}")


if __name__ == "__main__":
    main()
