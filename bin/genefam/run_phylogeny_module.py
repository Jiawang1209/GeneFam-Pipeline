#!/usr/bin/env python3
"""Run 06_phylogeny: multiple sequence alignment and tree construction."""

from __future__ import annotations

import argparse
import csv
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bin.genefam.prepare_alignment_inputs import prepare_alignment_manifest
from bin.genefam.prepare_phylogeny_inputs import prepare_phylogeny_manifest


ALIGNMENT_FIELDS = ["family_name", "aligner", "sequence_count", "input_fasta", "raw_alignment", "trimmed_alignment"]
PHYLOGENY_FIELDS = ["family_name", "tree_builder", "alignment", "treefile", "support_file"]
COMMAND_FIELDS = ["step", "tool", "command", "stdout", "stderr", "status"]
TREE_SUBFAMILY_SCRIPT = REPO_ROOT / "scripts/plot_tree_subfamilies.R"
LABEL_MAP_FIELDS = ["original_id", "tree_label", "gene_id", "species_id"]
PLOT_CONFIG_FIELDS = ["parameter", "value"]


def load_project_config(path: Path | None) -> dict:
    if path is None:
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to read project.yaml")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Project config must be a mapping: {path}")
    return data


def config_path(value: str | Path | None, config_dir: Path) -> Path | None:
    if value is None or value == "":
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    return config_dir / path


def as_list(value: object, default: list[str] | None = None) -> list[str]:
    if value is None:
        return list(default or [])
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return shlex.split(value)
    raise ValueError(f"Expected list or string options, got {type(value).__name__}")


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def normalize_plot_config(config: object) -> dict[str, str]:
    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ValueError("phylogeny.subfamily.plot must be a mapping")
    normalized: dict[str, str] = {}
    for key, value in config.items():
        if value is None:
            continue
        normalized[str(key)] = str(value)
    return normalized


def write_plot_config(config: dict[str, str], path: Path) -> Path:
    rows = [{"parameter": key, "value": value} for key, value in sorted(config.items())]
    write_tsv(rows, path, PLOT_CONFIG_FIELDS)
    return path


def ensure_command(command: str) -> str:
    found = shutil.which(command)
    if found is None:
        raise RuntimeError(f"Required command not found: {command}")
    return found


def resolve_tree_executable(tree_builder: str) -> str:
    if tree_builder == "fasttree":
        for candidate in ("FastTree", "fasttree"):
            if shutil.which(candidate):
                return candidate
        raise RuntimeError("Required command not found: FastTree or fasttree")
    if tree_builder == "iqtree":
        for candidate in ("iqtree2", "iqtree"):
            if shutil.which(candidate):
                return candidate
        raise RuntimeError("Required command not found: iqtree2 or iqtree")
    raise ValueError("tree_builder must be fasttree or iqtree")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def split_member_id(identifier: str) -> tuple[str, str]:
    clean = identifier.split()[0]
    if "|" in clean:
        species_id, gene_id = clean.split("|", 1)
        return species_id, gene_id
    return "Unknown", clean


def default_sequence_map_path(input_fasta: Path) -> Path:
    return input_fasta.parents[1] / "tables/identify_sequence_map.tsv"


def load_sequence_map(input_fasta: Path) -> dict[str, dict[str, str]]:
    map_path = default_sequence_map_path(input_fasta)
    if not map_path.exists():
        return {}
    rows = read_tsv(map_path)
    return {row.get("fasta_id", ""): row for row in rows if row.get("fasta_id")}


def prepare_phylogeny_fasta(input_fasta: Path, output_fasta: Path, label_map: Path) -> Path:
    output_fasta.parent.mkdir(parents=True, exist_ok=True)
    label_map.parent.mkdir(parents=True, exist_ok=True)
    seen: dict[str, int] = {}
    rows: list[dict[str, str]] = []
    sequence_map = load_sequence_map(input_fasta)
    with input_fasta.open("r", encoding="utf-8") as source, output_fasta.open("w", encoding="utf-8") as fasta_out:
        for line in source:
            if line.startswith(">"):
                original_id = line[1:].strip().split()[0]
                mapped = sequence_map.get(original_id, {})
                if mapped:
                    species_id = mapped.get("species_id", "Unknown")
                    gene_id = mapped.get("gene_id", original_id)
                else:
                    species_id, gene_id = split_member_id(original_id)
                seen[gene_id] = seen.get(gene_id, 0) + 1
                tree_label = gene_id if seen[gene_id] == 1 else f"{gene_id}_dup{seen[gene_id]}"
                rows.append(
                    {
                        "original_id": original_id,
                        "tree_label": tree_label,
                        "gene_id": gene_id,
                        "species_id": species_id,
                    }
                )
                fasta_out.write(f">{tree_label}\n")
            else:
                fasta_out.write(line)
    write_tsv(rows, label_map, LABEL_MAP_FIELDS)
    return output_fasta


def run_mafft(input_fasta: Path, output_alignment: Path, options: list[str], log_dir: Path) -> dict[str, str]:
    ensure_command("mafft")
    output_alignment.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    command = ["mafft", *options, str(input_fasta)]
    stderr_path = log_dir / "mafft.stderr.log"
    with output_alignment.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {
        "step": "alignment",
        "tool": "mafft",
        "command": shell_join(command),
        "stdout": str(output_alignment),
        "stderr": str(stderr_path),
        "status": "completed",
    }


def run_muscle(input_fasta: Path, output_alignment: Path, options: list[str], log_dir: Path) -> dict[str, str]:
    ensure_command("muscle")
    output_alignment.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    if options:
        command = ["muscle", *[part.format(input=input_fasta, output=output_alignment) for part in options]]
    else:
        command = ["muscle", "-align", str(input_fasta), "-output", str(output_alignment)]
    stdout_path = log_dir / "muscle.stdout.log"
    stderr_path = log_dir / "muscle.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {
        "step": "alignment",
        "tool": "muscle",
        "command": shell_join(command),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "status": "completed",
    }


def run_fasttree(alignment: Path, treefile: Path, options: list[str], log_dir: Path) -> dict[str, str]:
    executable = resolve_tree_executable("fasttree")
    treefile.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    command = [executable, *options, "-out", str(treefile), str(alignment)]
    stderr_path = log_dir / "fasttree.stderr.log"
    stdout_path = log_dir / "fasttree.stdout.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {
        "step": "phylogeny",
        "tool": "fasttree",
        "command": shell_join(command),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "status": "completed",
    }


def run_iqtree(alignment: Path, treefile: Path, options: list[str], model: str, bootstrap: int, threads: str, log_dir: Path) -> dict[str, str]:
    executable = resolve_tree_executable("iqtree")
    treefile.parent.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    prefix = str(treefile).removesuffix(".treefile")
    command = [
        executable,
        "-s",
        str(alignment),
        "-m",
        model,
        "-bb",
        str(bootstrap),
        "-nt",
        str(threads),
        "-pre",
        prefix,
        *options,
    ]
    stdout_path = log_dir / "iqtree.stdout.log"
    stderr_path = log_dir / "iqtree.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    expected_tree = Path(f"{prefix}.treefile")
    if expected_tree != treefile and expected_tree.exists():
        shutil.copy2(expected_tree, treefile)
    return {
        "step": "phylogeny",
        "tool": "iqtree",
        "command": shell_join(command),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "status": "completed",
    }


def run_tree_subfamilies(
    treefile: Path,
    outdir: Path,
    family_name: str,
    r_bin: str,
    min_size: int,
    max_groups: int,
    label_map: Path,
    plot_config: Path,
    log_dir: Path,
) -> dict[str, str]:
    executable = ensure_command(r_bin)
    log_dir.mkdir(parents=True, exist_ok=True)
    if Path(executable).name == "R":
        command = [
            executable,
            "--vanilla",
            "--slave",
            "-f",
            str(TREE_SUBFAMILY_SCRIPT),
            "--args",
            str(treefile),
            str(outdir),
            family_name,
            str(min_size),
            str(max_groups),
            str(label_map),
            str(plot_config),
        ]
    else:
        command = [
            executable,
            str(TREE_SUBFAMILY_SCRIPT),
            str(treefile),
            str(outdir),
            family_name,
            str(min_size),
            str(max_groups),
            str(label_map),
            str(plot_config),
        ]
    stdout_path = log_dir / "tree_subfamily.stdout.log"
    stderr_path = log_dir / "tree_subfamily.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        subprocess.run(command, check=True, stdout=stdout, stderr=stderr, text=True)
    return {
        "step": "tree_subfamily",
        "tool": Path(executable).name,
        "command": shell_join(command),
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "status": "completed",
    }


def resolve_args(args: argparse.Namespace) -> dict:
    config = load_project_config(args.config)
    config_dir = args.config.parent if args.config else Path.cwd()
    project_config = config.get("project", {}) or {}
    phylogeny_config = config.get("phylogeny", {}) or {}
    genefamily_info_config = config.get("genefamily_info", {}) or {}
    subfamily_config = phylogeny_config.get("subfamily", {}) or {}
    project_outdir = config_path(project_config.get("outdir"), config_dir) or Path("results")
    family_name = args.family_name or phylogeny_config.get("family_name") or project_config.get("family_name") or "family"
    input_fasta = args.input_fasta or config_path(phylogeny_config.get("input_fasta"), config_dir) or project_outdir / "04_identification/fasta/identify.ID.fa"
    outdir = args.outdir or config_path(phylogeny_config.get("outdir"), config_dir) or project_outdir / "06_phylogeny"
    aligner = args.aligner or phylogeny_config.get("aligner", "mafft")
    tree_builder = args.tree_builder or phylogeny_config.get("tree_builder", "fasttree")
    if aligner not in {"mafft", "muscle"}:
        raise ValueError("aligner must be mafft or muscle")
    if tree_builder not in {"fasttree", "iqtree"}:
        raise ValueError("tree_builder must be fasttree or iqtree")
    default_tree_options = ["-lg"] if tree_builder == "fasttree" else ["-bnni", "-cmax", "15", "-redo"]
    configured_tree_options = (
        phylogeny_config.get(f"{tree_builder}_options")
        if phylogeny_config.get(f"{tree_builder}_options") is not None
        else phylogeny_config.get("tree_options")
    )
    return {
        "family_name": family_name,
        "input_fasta": input_fasta,
        "outdir": outdir,
        "aligner": aligner,
        "tree_builder": tree_builder,
        "aligner_options": as_list(args.aligner_options, None)
        if args.aligner_options is not None
        else as_list(phylogeny_config.get("aligner_options"), ["--auto"] if aligner == "mafft" else []),
        "tree_options": as_list(args.tree_options, None)
        if args.tree_options is not None
        else as_list(configured_tree_options, default_tree_options),
        "iqtree_model": args.iqtree_model or phylogeny_config.get("iqtree_model", "MFP"),
        "iqtree_bootstrap": args.iqtree_bootstrap
        if args.iqtree_bootstrap is not None
        else int(phylogeny_config.get("iqtree_bootstrap", 1000)),
        "threads": str(args.threads or phylogeny_config.get("threads", "AUTO")),
        "subfamily_enabled": bool(subfamily_config.get("enabled", True)),
        "subfamily_method": str(subfamily_config.get("method", "auto_topology")),
        "subfamily_min_size": int(subfamily_config.get("min_size", 2)),
        "subfamily_max_groups": int(subfamily_config.get("max_groups", 8)),
        "subfamily_r_bin": str(subfamily_config.get("r_bin") or genefamily_info_config.get("r_bin") or "/usr/local/bin/R"),
        "subfamily_plot_config": normalize_plot_config(subfamily_config.get("plot")),
    }


def run_module(**kwargs) -> Path:
    outdir: Path = kwargs["outdir"]
    tables_dir = outdir / "tables"
    alignment_dir = outdir / "alignment"
    phylogeny_dir = outdir / "phylogeny"
    logs_dir = outdir / "logs"
    inputs_dir = outdir / "inputs"
    input_fasta: Path = kwargs["input_fasta"]
    if not input_fasta.exists():
        raise ValueError(f"Input FASTA does not exist: {input_fasta}")
    phylogeny_input = inputs_dir / f"{kwargs['family_name']}.phylogeny_input.fa"
    label_map = tables_dir / "phylogeny_label_map.tsv"
    prepare_phylogeny_fasta(input_fasta, phylogeny_input, label_map)

    alignment_rows = prepare_alignment_manifest(kwargs["family_name"], phylogeny_input, alignment_dir, kwargs["aligner"])
    raw_alignment = Path(alignment_rows[0]["raw_alignment"])
    if kwargs["aligner"] == "mafft":
        alignment_command = run_mafft(phylogeny_input, raw_alignment, kwargs["aligner_options"], logs_dir)
    else:
        alignment_command = run_muscle(phylogeny_input, raw_alignment, kwargs["aligner_options"], logs_dir)
    alignment_rows[0]["trimmed_alignment"] = ""

    phylogeny_rows = prepare_phylogeny_manifest(alignment_rows, phylogeny_dir, kwargs["tree_builder"])
    alignment = Path(phylogeny_rows[0]["alignment"])
    treefile = Path(phylogeny_rows[0]["treefile"])
    if kwargs["tree_builder"] == "fasttree":
        tree_command = run_fasttree(alignment, treefile, kwargs["tree_options"], logs_dir)
    else:
        tree_command = run_iqtree(
            alignment,
            treefile,
            kwargs["tree_options"],
            kwargs["iqtree_model"],
            kwargs["iqtree_bootstrap"],
            kwargs["threads"],
            logs_dir,
        )
    command_rows = [alignment_command, tree_command]
    subfamily_command = None
    subfamily_assignments = outdir / "tables/tree_subfamily_assignments.tsv"
    subfamily_stats = outdir / "tables/tree_subfamily_stats.tsv"
    subfamily_plot_config = outdir / "tables/tree_subfamily_plot_config.tsv"
    subfamily_tree_plot = outdir / "plots/tree_subfamily.pdf"
    subfamily_stats_plot = outdir / "plots/tree_subfamily_species_stats.pdf"
    if kwargs["subfamily_enabled"]:
        if kwargs["subfamily_method"] != "auto_topology":
            raise ValueError("phylogeny.subfamily.method currently supports only auto_topology")
        write_plot_config(kwargs["subfamily_plot_config"], subfamily_plot_config)
        subfamily_command = run_tree_subfamilies(
            treefile,
            outdir,
            kwargs["family_name"],
            kwargs["subfamily_r_bin"],
            kwargs["subfamily_min_size"],
            kwargs["subfamily_max_groups"],
            label_map,
            subfamily_plot_config,
            logs_dir,
        )
        command_rows.append(subfamily_command)

    write_tsv(alignment_rows, tables_dir / "alignment_manifest.tsv", ALIGNMENT_FIELDS)
    write_tsv(phylogeny_rows, tables_dir / "phylogeny_manifest.tsv", PHYLOGENY_FIELDS)
    write_tsv(command_rows, tables_dir / "phylogeny_commands.tsv", COMMAND_FIELDS)
    report = [
        "# 06_phylogeny Summary",
        "",
        f"- Input FASTA: `{input_fasta}`",
        f"- Phylogeny FASTA: `{phylogeny_input}`",
        f"- Phylogeny label map: `{label_map}`",
        f"- Family: `{kwargs['family_name']}`",
        f"- Sequence count: {alignment_rows[0]['sequence_count']}",
        f"- Aligner: `{kwargs['aligner']}`",
        f"- Tree builder: `{kwargs['tree_builder']}`",
        f"- Alignment: `{raw_alignment}`",
        f"- Treefile: `{treefile}`",
        f"- Alignment command: `{alignment_command['command']}`",
        f"- Tree command: `{tree_command['command']}`",
    ]
    if kwargs["subfamily_enabled"]:
        report.extend(
            [
                f"- Subfamily method: `{kwargs['subfamily_method']}`",
                f"- Subfamily minimum size: {kwargs['subfamily_min_size']}",
                f"- Subfamily maximum groups: {kwargs['subfamily_max_groups']}",
                f"- Subfamily assignments: `{subfamily_assignments}`",
                f"- Subfamily statistics: `{subfamily_stats}`",
                f"- Subfamily plot config: `{subfamily_plot_config}`",
                f"- Subfamily tree plot: `{subfamily_tree_plot}`",
                f"- Subfamily species statistics plot: `{subfamily_stats_plot}`",
                f"- Subfamily command: `{subfamily_command['command'] if subfamily_command else ''}`",
            ]
        )
    else:
        report.append("- Subfamily classification: disabled")
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/phylogeny_summary.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=None, type=Path)
    parser.add_argument("--input-fasta", default=None, type=Path)
    parser.add_argument("--outdir", default=None, type=Path)
    parser.add_argument("--family-name", default=None)
    parser.add_argument("--aligner", choices=["mafft", "muscle"], default=None)
    parser.add_argument("--tree-builder", choices=["fasttree", "iqtree"], default=None)
    parser.add_argument("--aligner-options", default=None)
    parser.add_argument("--tree-options", default=None)
    parser.add_argument("--iqtree-model", default=None)
    parser.add_argument("--iqtree-bootstrap", default=None, type=int)
    parser.add_argument("--threads", default=None)
    args = parser.parse_args()
    try:
        outdir = run_module(**resolve_args(args))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"06_phylogeny completed at {outdir.resolve()}")


if __name__ == "__main__":
    main()
