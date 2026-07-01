#!/usr/bin/env python3
"""Run 12_full_bioinformatics_report: assemble a complete bioinformatics Markdown report."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


VERSION_FIELDS = ["software", "version", "status", "command"]
FIGURE_FIELDS = ["module", "figure", "path", "interpretation"]
MODULE_STATUS_FIELDS = ["module", "status", "note"]
BUILD_STATUS_FIELDS = ["status", "module_count", "figure_count", "note"]


MODULES = [
    ("01_preprocess", "Data preprocessing"),
    ("02_hmm", "HMM candidate screening"),
    ("03_blastp", "Seed/reference BLASTP screening"),
    ("04_identification", "Candidate integration and domain confirmation"),
    ("05_genefamily_info", "Gene family information and protein properties"),
    ("06_phylogeny", "Alignment, phylogeny, and subfamily classification"),
    ("07_domain_motif_genestructure", "Domain, motif, and gene structure visualization"),
    ("08_jcvi", "Inter-species JCVI collinearity"),
    ("09_mcscanx", "Intra-species MCScanX duplication and circlize"),
    ("10_promoter", "Promoter extraction and cis-element integration"),
    ("11_ppi", "AraNet-supported PPI and ggNetView visualization"),
]


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


def write_tsv(rows: list[dict[str, str]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def detect_version(software: str, command: list[str]) -> dict[str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {"software": software, "version": "not_detected", "status": "missing", "command": " ".join(command)}
    output = (completed.stdout or completed.stderr or "").strip().splitlines()
    version = output[0][:200] if output else "not_detected"
    return {"software": software, "version": version, "status": "detected" if completed.returncode == 0 else "not_detected", "command": " ".join(command)}


def software_versions(r_bin: str) -> list[dict[str, str]]:
    rows = [
        detect_version("python", ["python", "--version"]),
        detect_version("R", [r_bin, "--version"]),
        detect_version("JCVI", ["python", "-c", "import jcvi; print(getattr(jcvi, '__version__', 'version_not_detected'))"]),
        detect_version("MCScanX", ["MCScanX", "--help"]),
        detect_version("diamond", ["diamond", "--version"]),
        detect_version("blastp", ["blastp", "-version"]),
        detect_version("seqkit", ["seqkit", "version"]),
    ]
    ggnetview = subprocess.run([r_bin, "--vanilla", "--slave", "-e", 'cat(as.character(utils::packageVersion("ggNetView")))'], check=False, capture_output=True, text=True)
    rows.append(
        {
            "software": "ggNetView",
            "version": ggnetview.stdout.strip() if ggnetview.returncode == 0 else "not_detected",
            "status": "detected" if ggnetview.returncode == 0 else "missing",
            "command": f'{r_bin} --vanilla --slave -e packageVersion("ggNetView")',
        }
    )
    return rows


def first_status_from_tsv(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "available", "No status table found; module output directory exists"
    rows = read_tsv(path)
    if not rows:
        return "unknown", f"Empty status table: {path.name}"
    row = rows[0]
    return row.get("status", row.get("check", "available")), row.get("note", "")


def collect_module_status(results: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    preferred_status = {
        "08_jcvi": "logs/jcvi_run_status.tsv",
        "09_mcscanx": "logs/mcscanx_execution_status.tsv",
        "10_promoter": "logs/promoter_cis_status.tsv",
        "11_ppi": "logs/ppi_status.tsv",
    }
    for module, label in MODULES:
        module_dir = results / module
        if not module_dir.exists():
            rows.append({"module": module, "status": "missing", "note": f"{label} output directory not found"})
            continue
        status_rel = preferred_status.get(module)
        status, note = first_status_from_tsv(module_dir / status_rel) if status_rel else ("available", f"{label} outputs are present")
        rows.append({"module": module, "status": status, "note": note})
    return rows


def figure_interpretation(module: str, figure: Path) -> str:
    name = figure.name
    if module == "05_genefamily_info":
        return "This figure summarizes family member counts or protein physicochemical properties across species, supporting cross-species comparison of copy number and protein feature distributions."
    if module == "06_phylogeny":
        return "This phylogenetic figure groups candidate proteins by tree topology and helps interpret subfamily structure and species-specific membership patterns."
    if module == "07_domain_motif_genestructure":
        return "This composite figure aligns tree order with conserved domains, MEME motifs, and exon/UTR/CDS structures, allowing structural conservation and divergence to be read gene by gene."
    if module == "08_jcvi":
        return "This JCVI figure summarizes inter-species collinearity or Ka/Ks evidence and should be interpreted as conserved syntenic context among selected species."
    if module == "09_mcscanx":
        return "This MCScanX/circlize figure shows intra-species chromosomal distribution, local density, duplicate type tracks, and tandem or WGD links for family members."
    if module == "10_promoter":
        return "This promoter figure summarizes cis-element counts by species and functional class, highlighting hormone, stress, light, or development-related regulatory signals."
    if module == "11_ppi":
        return "This ggNetView PPI figure shows AraNet-supported interaction structure for family-associated nodes; sparse networks indicate limited retained reference-supported edges under current evidence settings."
    return f"This figure belongs to {module} and should be interpreted together with that module's summary report."


def collect_figures(results: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for module, _label in MODULES:
        plot_dir = results / module / "plots"
        if not plot_dir.exists():
            continue
        for figure in sorted(plot_dir.glob("*")):
            if figure.suffix.lower() not in {".pdf", ".png"}:
                continue
            rows.append({"module": module, "figure": figure.name, "path": str(figure), "interpretation": figure_interpretation(module, figure)})
    return rows


def collect_module_summaries(results: Path) -> list[tuple[str, str]]:
    summaries: list[tuple[str, str]] = []
    for module, label in MODULES:
        report_dir = results / module / "report"
        if not report_dir.exists():
            continue
        texts = []
        for report in sorted(report_dir.glob("*.md")):
            text = report.read_text(encoding="utf-8")
            if len(text) > 2600:
                cut_at = text.rfind("\n", 0, 2600)
                if cut_at < 1200:
                    cut_at = 2600
                text = text[:cut_at].rstrip() + "\n\n[Module summary truncated in the final report; see the module report for full command details.]"
            texts.append(text)
        if texts:
            summaries.append((f"{module}: {label}", "\n\n".join(texts)))
    return summaries


def write_report(project_name: str, outdir: Path, versions: list[dict[str, str]], statuses: list[dict[str, str]], figures: list[dict[str, str]], summaries: list[tuple[str, str]]) -> None:
    lines = [
        f"# {project_name} Gene Family Bioinformatics Report",
        "",
        "## Methods",
        "",
        "This report summarizes a multi-species gene family workflow covering preprocessing, HMM candidate screening, BLASTP/reference evidence, final identification, gene family information, phylogeny, domain/motif/gene-structure visualization, JCVI collinearity, MCScanX self duplication, promoter analysis, and AraNet-supported PPI analysis.",
        "",
        "### Software Versions",
        "",
        "| Software | Status | Version | Command |",
        "|---|---|---|---|",
    ]
    for row in versions:
        lines.append(f"| {row['software']} | {row['status']} | {row['version']} | `{row['command']}` |")
    lines.extend(["", "## Results", ""])
    for title, summary in summaries:
        lines.extend([f"### {title}", "", summary.strip(), ""])
    lines.extend(["### Module Status Overview", "", "| Module | Status | Note |", "|---|---|---|"])
    for row in statuses:
        lines.append(f"| {row['module']} | {row['status']} | {row['note']} |")
    lines.extend(["", "## Figure-by-Figure Interpretation", ""])
    if figures:
        for row in figures:
            lines.extend([f"### {row['module']} / {row['figure']}", "", f"Path: `{row['path']}`", "", row["interpretation"], ""])
    else:
        lines.append("No figure files were detected in module plot directories.")
    lines.extend(
        [
            "## QC Warnings",
            "",
            "- Modules marked `missing_input`, `planned`, or `ready_not_executed` require the corresponding optional inputs or explicit execution flags before being interpreted as final biological evidence.",
            "- Sparse PPI or missing cis-element plots should be interpreted as current evidence limitations, not as absence of biological regulation or interaction.",
            "",
            "## Reproducibility Commands",
            "",
            "```bash",
            "conda run -n GeneFamilyFlow python bin/genefam/run_jcvi_module.py --config projects/Whirly_2026/project.yaml",
            "conda run -n GeneFamilyFlow python bin/genefam/run_mcscanx_module.py --config projects/Whirly_2026/project.yaml",
            "conda run -n GeneFamilyFlow python bin/genefam/run_promoter_module.py --config projects/Whirly_2026/project.yaml",
            "conda run -n GeneFamilyFlow python bin/genefam/run_ppi_module.py --config projects/Whirly_2026/project.yaml",
            "conda run -n GeneFamilyFlow python bin/genefam/run_full_bioinformatics_report.py --config projects/Whirly_2026/project.yaml",
            "```",
            "",
        ]
    )
    (outdir / "report").mkdir(parents=True, exist_ok=True)
    (outdir / "report/full_bioinformatics_report.md").write_text("\n".join(lines), encoding="utf-8")


def run_full_report(config_path_value: Path | None = None, outdir_override: Path | None = None) -> Path:
    config = load_project_config(config_path_value)
    config_dir = config_path_value.parent if config_path_value else Path.cwd()
    project_name = config.get("project", {}).get("name", "GeneFam_Project")
    results = config_path(config.get("project", {}).get("outdir", "results"), config_dir) or Path("results")
    outdir = outdir_override or (results / "12_full_bioinformatics_report")
    for subdir in ["tables", "report", "logs"]:
        (outdir / subdir).mkdir(parents=True, exist_ok=True)
    r_bin = str(config.get("report", {}).get("r_bin", config.get("ppi", {}).get("r_bin", "/usr/local/bin/R")))
    versions = software_versions(r_bin)
    statuses = collect_module_status(results)
    figures = collect_figures(results)
    summaries = collect_module_summaries(results)
    write_tsv(versions, outdir / "tables/software_versions.tsv", VERSION_FIELDS)
    write_tsv(statuses, outdir / "tables/module_status_overview.tsv", MODULE_STATUS_FIELDS)
    write_tsv(figures, outdir / "tables/figure_interpretation_index.tsv", FIGURE_FIELDS)
    write_tsv([{"status": "available", "module_count": str(len(statuses)), "figure_count": str(len(figures)), "note": "Full bioinformatics report generated"}], outdir / "logs/report_build_status.tsv", BUILD_STATUS_FIELDS)
    write_report(str(project_name), outdir, versions, statuses, figures, summaries)
    return outdir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()
    run_full_report(config_path_value=args.config, outdir_override=args.outdir)


if __name__ == "__main__":
    main()
