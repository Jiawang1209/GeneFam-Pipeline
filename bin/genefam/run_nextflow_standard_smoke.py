#!/usr/bin/env python3
"""Run or diagnose the Nextflow standard identification smoke path."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.run_nextflow_smoke import resolve_nextflow_binary
from bin.genefam.validate_config import load_config


FIELDNAMES = ["check", "status", "exit_code", "command", "note"]


def _resolve_optional_path(value: object) -> str:
    if value in {None, ""}:
        return ""
    path = Path(str(value))
    return str(path if path.is_absolute() else path.resolve())


def _bool_param(value: object) -> str:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return "true"
        if lowered in {"false", "0", "no", "off"}:
            return "false"
    return str(bool(value)).lower()


def load_standard_params(config_path: Path) -> dict[str, str]:
    config = load_config(config_path)
    project = config.get("project", {}) or {}
    gene_family = config.get("gene_family", {}) or {}
    identification = config.get("identification", {}) or {}
    dev = config.get("dev", {}) or {}
    plotting = config.get("plotting", {}) or {}
    modules = config.get("modules", {}) or {}
    promoter = config.get("promoter", {}) or {}
    ppi = config.get("ppi", {}) or {}
    expression = config.get("expression", {}) or {}
    return {
        "project_name": str(project.get("name", "GDSL_demo")),
        "gene_family": str(gene_family.get("name", "GDSL")),
        "use_hmmer": _bool_param(identification.get("use_hmmer", True)),
        "use_diamond": _bool_param(identification.get("use_diamond", True)),
        "final_rule": str(identification.get("final_rule", "intersection")),
        "mock_external_tools": _bool_param(dev.get("mock_external_tools", True)),
        "run_feature_summary": _bool_param(modules.get("feature_summary", False)),
        "run_mcscanx_circlize": _bool_param(modules.get("synteny", False)),
        "syntenic_pairs": _resolve_optional_path(plotting.get("syntenic_pairs")),
        "run_promoter": _bool_param(modules.get("promoter", False)),
        "run_promoter_cis": _bool_param(modules.get("promoter_cis", False)),
        "promoter_cis_elements": _resolve_optional_path(promoter.get("cis_elements")),
        "run_ppi": _bool_param(modules.get("ppi", False)),
        "ppi_edges": _resolve_optional_path(ppi.get("edges")),
        "ppi_nodes": _resolve_optional_path(ppi.get("nodes")),
        "expression_matrix": _resolve_optional_path(expression.get("matrix") if modules.get("expression") else None),
        "expression_metadata": _resolve_optional_path(expression.get("metadata") if modules.get("expression") else None),
        "gene_family_species_order": _resolve_optional_path(plotting.get("gene_family_species_order")),
    }


def expected_published_outputs(
    standard_outdir: Path,
    feature_summary: bool = False,
    mcscanx_circlize: bool = False,
    promoter: bool = False,
    promoter_cis: bool = False,
    ppi: bool = False,
    expression: bool = False,
) -> list[Path]:
    outputs = [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/run_config_snapshot.tsv",
        standard_outdir / "tables/family_candidates.tsv",
        standard_outdir / "tables/family_counts.tsv",
        standard_outdir / "tables/gene_family_copy_number.tsv",
        standard_outdir / "tables/gene_family_copy_number_summary.tsv",
        standard_outdir / "tables/gene_family_species_order.tsv",
        standard_outdir / "tables/gene_family_copy_number_expansion.tsv",
        standard_outdir / "tables/gene_family_pangenome_summary.tsv",
        standard_outdir / "tables/gene_family_protein_properties.tsv",
        standard_outdir / "tables/alignment_manifest.tsv",
        standard_outdir / "tables/phylogeny_manifest.tsv",
        standard_outdir / "alignment/GDSL.mafft.aln.faa",
        standard_outdir / "phylogeny/GDSL.fasttree.treefile",
        standard_outdir / "tables/motif_summary.tsv",
        standard_outdir / "tables/gene_structure_summary.tsv",
        standard_outdir / "tables/chromosome_locations.tsv",
        standard_outdir / "tables/wgd_handoff_manifest.tsv",
        standard_outdir / "sequences/family_members.faa",
        standard_outdir / "report/report_index.tsv",
        standard_outdir / "report/plot_manifest.tsv",
        standard_outdir / "report/final_report.md",
        standard_outdir / "plots/family_counts.pdf",
        standard_outdir / "plots/family_counts.png",
        standard_outdir / "plots/gene_family_info_summary.pdf",
        standard_outdir / "plots/gene_family_info_summary.png",
    ]
    if feature_summary:
        outputs.extend(
            [
                standard_outdir / "tables/feature_summary.tsv",
                standard_outdir / "plots/feature_summary.pdf",
                standard_outdir / "plots/feature_summary.png",
            ]
        )
    if mcscanx_circlize:
        outputs.extend(
            [
                standard_outdir / "tables/circlize_chromosomes.tsv",
                standard_outdir / "tables/circlize_links.tsv",
                standard_outdir / "tables/circlize_skipped_links.tsv",
                standard_outdir / "plots/mcscanx_circlize.pdf",
                standard_outdir / "plots/mcscanx_circlize.png",
            ]
        )
    if promoter:
        outputs.extend(
            [
                standard_outdir / "tables/promoters.bed",
                standard_outdir / "sequences/promoters.fa",
            ]
        )
    if promoter_cis:
        outputs.extend(
            [
                standard_outdir / "tables/promoter_cis_elements.tsv",
                standard_outdir / "tables/promoter_cis_gene_matrix.tsv",
                standard_outdir / "tables/promoter_cis_gene_element_matrix.tsv",
                standard_outdir / "tables/promoter_cis_category_summary.tsv",
                standard_outdir / "tables/promoter_cis_element_annotations.tsv",
                standard_outdir / "plots/promoter_cis_elements.pdf",
                standard_outdir / "plots/promoter_cis_elements.png",
            ]
        )
    if ppi:
        outputs.extend(
            [
                standard_outdir / "tables/ppi_edges.tsv",
                standard_outdir / "tables/ppi_nodes.tsv",
                standard_outdir / "tables/ppi_hubs.tsv",
                standard_outdir / "tables/ppi_input_evidence.tsv",
                standard_outdir / "tables/ppi_network_qc.tsv",
                standard_outdir / "tables/ppi_ggnetview_status.tsv",
                standard_outdir / "plots/ppi_ggnetview.pdf",
                standard_outdir / "plots/ppi_ggnetview.png",
            ]
        )
    if expression:
        outputs.extend(
            [
                standard_outdir / "tables/family_expression.tsv",
                standard_outdir / "tables/expression_sample_metadata.tsv",
                standard_outdir / "tables/expression_group_matrix.tsv",
                standard_outdir / "tables/expression_gene_summary.tsv",
                standard_outdir / "plots/expression_heatmap.pdf",
                standard_outdir / "plots/expression_heatmap.png",
            ]
        )
    return outputs


def expected_single_tool_outputs(standard_outdir: Path) -> list[Path]:
    return [
        standard_outdir / "tables/species_manifest.tsv",
        standard_outdir / "tables/family_candidates.tsv",
    ]


def build_nextflow_command(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: str,
    profile: str | None = None,
    use_hmmer: bool | str = True,
    use_diamond: bool | str = True,
    final_rule: str = "intersection",
    project_name: str | None = None,
    gene_family: str | None = None,
    mock_external_tools: bool | str = True,
    stop_after_family_candidates: bool | str = False,
    run_feature_summary: bool | str = False,
    run_mcscanx_circlize: bool | str = False,
    syntenic_pairs: str | None = None,
    run_promoter: bool | str = False,
    run_promoter_cis: bool | str = False,
    promoter_cis_elements: str | None = None,
    run_ppi: bool | str = False,
    ppi_edges: str | None = None,
    ppi_nodes: str | None = None,
    expression_matrix: str | None = None,
    expression_metadata: str | None = None,
    gene_family_species_order: str | None = None,
) -> list[str]:
    command = [
        nextflow_bin,
        "run",
        "workflows/main.nf",
        "-c",
        "workflows/nextflow.config",
    ]
    if profile:
        command.extend(["-profile", profile])
    if project_name:
        command.extend(["--project_name", project_name])
    if gene_family:
        command.extend(["--gene_family", gene_family])
    command.extend(
        [
            "--config",
            config,
            "--groups",
            groups,
            "--run_identification",
            "true",
            "--use_hmmer",
            _bool_param(use_hmmer),
            "--use_diamond",
            _bool_param(use_diamond),
            "--final_rule",
            final_rule,
            "--mock_external_tools",
            _bool_param(mock_external_tools),
            "--standard_stop_after_family_candidates",
            _bool_param(stop_after_family_candidates),
            "--run_feature_summary",
            _bool_param(run_feature_summary),
            "--run_mcscanx_circlize",
            _bool_param(run_mcscanx_circlize),
            "--run_promoter",
            _bool_param(run_promoter),
            "--run_promoter_cis",
            _bool_param(run_promoter_cis),
            "--run_ppi",
            _bool_param(run_ppi),
            "--mock_evidence_dir",
            mock_evidence_dir,
            "--outdir",
            outdir,
        ]
    )
    if syntenic_pairs:
        command.extend(["--syntenic_pairs", syntenic_pairs])
    if promoter_cis_elements:
        command.extend(["--promoter_cis_elements", promoter_cis_elements])
    if ppi_edges:
        command.extend(["--ppi_edges", ppi_edges])
    if ppi_nodes:
        command.extend(["--ppi_nodes", ppi_nodes])
    if expression_matrix:
        command.extend(["--expression_matrix", expression_matrix])
    if expression_metadata:
        command.extend(["--expression_metadata", expression_metadata])
    if gene_family_species_order:
        command.extend(["--gene_family_species_order", gene_family_species_order])
    return command


def _write_tsv(row: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, delimiter="\t")
        writer.writeheader()
        writer.writerow(row)


def _write_markdown(row: dict[str, str], out_path: Path) -> None:
    lines = [
        "# Nextflow Standard Branch Smoke",
        "",
        f"Status: {row['status']}",
        f"Exit code: {row['exit_code']}",
        "",
        "```bash",
        row["command"],
        "```",
        "",
        row["note"],
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run_nextflow_standard_smoke(
    nextflow_bin: str,
    config: str,
    groups: str,
    mock_evidence_dir: str,
    outdir: Path,
    conda_env: str | None = None,
    stop_after_family_candidates: bool | str = False,
    run_feature_summary: bool | str = False,
    run_mcscanx_circlize: bool | str = False,
    syntenic_pairs: str | None = None,
    run_promoter: bool | str = False,
    run_promoter_cis: bool | str = False,
    promoter_cis_elements: str | None = None,
    run_ppi: bool | str = False,
    ppi_edges: str | None = None,
    ppi_nodes: str | None = None,
    expression_matrix: str | None = None,
    expression_metadata: str | None = None,
) -> dict[str, str]:
    resolved_nextflow = resolve_nextflow_binary(nextflow_bin, conda_env=conda_env)
    standard_params = load_standard_params(Path(config))
    runtime_params = dict(standard_params)
    override_candidates = {
        "run_feature_summary": run_feature_summary,
        "run_mcscanx_circlize": run_mcscanx_circlize,
        "syntenic_pairs": syntenic_pairs,
        "run_promoter": run_promoter,
        "run_promoter_cis": run_promoter_cis,
        "promoter_cis_elements": promoter_cis_elements,
        "run_ppi": run_ppi,
        "ppi_edges": ppi_edges,
        "ppi_nodes": ppi_nodes,
        "expression_matrix": expression_matrix,
        "expression_metadata": expression_metadata,
    }
    for key, value in override_candidates.items():
        if isinstance(value, bool):
            if value:
                runtime_params[key] = _bool_param(value)
        elif value not in {None, ""}:
            runtime_params[key] = str(value)
    command_nextflow = resolved_nextflow or nextflow_bin
    profile = "activated" if conda_env and resolved_nextflow else None
    command = build_nextflow_command(
        nextflow_bin=command_nextflow,
        config=config,
        groups=groups,
        mock_evidence_dir=mock_evidence_dir,
        outdir=str(outdir / "standard"),
        profile=profile,
        stop_after_family_candidates=stop_after_family_candidates,
        **runtime_params,
    )
    if not resolved_nextflow:
        return {
            "check": "nextflow_standard_identification",
            "status": "missing_nextflow",
            "exit_code": "127",
            "command": " ".join(command),
            "note": "nextflow was not found on PATH or in the requested Conda environment; run the runtime bootstrap plan before this smoke can execute.",
        }
    env = os.environ.copy()
    if conda_env:
        env["PATH"] = f"{Path(resolved_nextflow).parent}:{env.get('PATH', '')}"
        env["CONDA_DEFAULT_ENV"] = conda_env
    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    standard_outdir = outdir / "standard"
    expected_outputs = (
        expected_single_tool_outputs(standard_outdir)
        if _bool_param(stop_after_family_candidates) == "true"
        else expected_published_outputs(
            standard_outdir,
            feature_summary=runtime_params["run_feature_summary"] == "true",
            mcscanx_circlize=runtime_params["run_mcscanx_circlize"] == "true",
            promoter=runtime_params["run_promoter"] == "true",
            promoter_cis=runtime_params["run_promoter_cis"] == "true",
            ppi=runtime_params["run_ppi"] == "true",
            expression=bool(runtime_params["expression_matrix"]),
        )
    )
    missing_outputs = [path for path in expected_outputs if not path.exists()]
    passed = completed.returncode == 0 and not missing_outputs
    if completed.returncode == 0 and missing_outputs:
        output = "\n".join(
            [
                output,
                "Missing published outputs:",
                *[str(path) for path in missing_outputs],
            ]
        )
    return {
        "check": "nextflow_standard_identification",
        "status": "passed" if passed else "failed",
        "exit_code": str(completed.returncode),
        "command": " ".join(command),
        "note": " | ".join(line.strip() for line in output.splitlines() if line.strip())[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nextflow-bin", default="nextflow")
    parser.add_argument("--conda-env", default=None)
    parser.add_argument("--config", default="configs/example.config.yaml")
    parser.add_argument("--groups", default="configs/species_groups.yaml")
    parser.add_argument("--mock-evidence-dir", default="tests/fixtures/mock_evidence")
    parser.add_argument("--outdir", default=Path("results/nextflow_standard_smoke"), type=Path)
    parser.add_argument("--run-feature-summary", action="store_true")
    parser.add_argument("--run-mcscanx-circlize", action="store_true")
    parser.add_argument("--syntenic-pairs", default=None)
    parser.add_argument("--run-promoter", action="store_true")
    parser.add_argument("--run-promoter-cis", action="store_true")
    parser.add_argument("--promoter-cis-elements", default=None)
    parser.add_argument("--run-ppi", action="store_true")
    parser.add_argument("--ppi-edges", default=None)
    parser.add_argument("--ppi-nodes", default=None)
    parser.add_argument("--expression-matrix", default=None)
    parser.add_argument("--expression-metadata", default=None)
    args = parser.parse_args()
    row = run_nextflow_standard_smoke(
        args.nextflow_bin,
        args.config,
        args.groups,
        args.mock_evidence_dir,
        args.outdir,
        conda_env=args.conda_env,
        run_feature_summary=args.run_feature_summary,
        run_mcscanx_circlize=args.run_mcscanx_circlize,
        syntenic_pairs=args.syntenic_pairs,
        run_promoter=args.run_promoter,
        run_promoter_cis=args.run_promoter_cis,
        promoter_cis_elements=args.promoter_cis_elements,
        run_ppi=args.run_ppi,
        ppi_edges=args.ppi_edges,
        ppi_nodes=args.ppi_nodes,
        expression_matrix=args.expression_matrix,
        expression_metadata=args.expression_metadata,
    )
    _write_tsv(row, args.outdir / "nextflow_standard_smoke.tsv")
    _write_markdown(row, args.outdir / "nextflow_standard_smoke.md")
    sys.exit(0 if row["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
