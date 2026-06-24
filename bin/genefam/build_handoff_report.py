#!/usr/bin/env python3
"""Build a compact handoff report from release and runtime evidence."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _count(rows: list[dict[str, str]], key: str, value: str) -> int:
    return sum(1 for row in rows if row.get(key) == value)


def _release_summary(rows: list[dict[str, str]]) -> str:
    passed = _count(rows, "status", "passed")
    failed = _count(rows, "status", "failed")
    required_failed = sum(1 for row in rows if row.get("required") == "true" and row.get("status") == "failed")
    optional_failed = sum(1 for row in rows if row.get("required") == "false" and row.get("status") == "failed")
    return (
        f"passed={passed} failed={failed} required_failed={required_failed} "
        f"optional_failed={optional_failed} release_ready={str(required_failed == 0).lower()}"
    )


def _objective_summary(rows: list[dict[str, str]]) -> str:
    achieved = _count(rows, "status", "achieved")
    blocked = _count(rows, "status", "blocked")
    missing = _count(rows, "status", "missing")
    return f"achieved={achieved} blocked={blocked} missing={missing} complete={str(blocked == 0 and missing == 0).lower()}"


def _blocked_requirements(rows: list[dict[str, str]]) -> str:
    blocked = [
        row["requirement"]
        for row in rows
        if row.get("status") in {"blocked", "missing"} and row.get("requirement")
    ]
    return ", ".join(blocked) if blocked else "none"


def _missing_runtime(rows: list[dict[str, str]]) -> str:
    missing = [row["command"] for row in rows if row.get("status") == "missing"]
    return ", ".join(missing) if missing else "none"


def _available_runtime(rows: list[dict[str, str]]) -> str:
    available = [row["command"] for row in rows if row.get("status", "").startswith("available")]
    return ", ".join(available) if available else "none"


def _container_smoke(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "not_run"
    parts = [f"{row.get('profile', row.get('check', 'unknown'))}={row.get('status', 'unknown')}" for row in rows]
    return "; ".join(parts)


def build_handoff_sections(
    release_rows: list[dict[str, str]],
    objective_rows: list[dict[str, str]],
    readiness_rows: list[dict[str, str]],
    container_rows: list[dict[str, str]],
) -> dict[str, str]:
    return {
        "release": _release_summary(release_rows),
        "objective": _objective_summary(objective_rows),
        "blocked_requirements": _blocked_requirements(objective_rows),
        "available_runtime": _available_runtime(readiness_rows),
        "missing_runtime": _missing_runtime(readiness_rows),
        "container_smoke": _container_smoke(container_rows),
    }


def write_markdown(sections: dict[str, str], out_path: Path) -> None:
    lines = [
        "# GeneFam-Pipeline Handoff Report",
        "",
        "## Current Status",
        "",
        f"- Release checks: `{sections['release']}`",
        f"- Objective audit: `{sections['objective']}`",
        f"- Blocked requirements: `{sections['blocked_requirements']}`",
        f"- Available runtime commands: `{sections['available_runtime']}`",
        f"- Missing runtime commands: `{sections['missing_runtime']}`",
        f"- Container smoke: `{sections['container_smoke']}`",
        "",
        "## Key Evidence",
        "",
        "- `results/release_checks/release_checks.md`",
        "- `results/objective_audit/objective_audit.md`",
        "- `results/readiness/command_readiness.tsv`",
        "- `results/container_profile_smoke/docker/container_profile_smoke.md`",
        "- `results/container_profile_smoke/apptainer/container_profile_smoke.md`",
        "",
        "## Next Command",
        "",
        "```bash",
        "python bin/genefam/run_release_checks.py --outdir results/release_checks",
        "```",
        "",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_tsv(sections: dict[str, str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "summary"], delimiter="\t")
        writer.writeheader()
        writer.writerows({"section": key, "summary": value} for key, value in sections.items())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-checks", default=Path("results/release_checks/release_checks.tsv"), type=Path)
    parser.add_argument("--objective-audit", default=Path("results/objective_audit/objective_audit.tsv"), type=Path)
    parser.add_argument("--readiness", default=Path("results/readiness/command_readiness.tsv"), type=Path)
    parser.add_argument(
        "--container-smoke",
        action="append",
        default=[],
        type=Path,
        help="Container profile smoke TSV; may be provided multiple times",
    )
    parser.add_argument("--out", default=Path("results/handoff/handoff_report.md"), type=Path)
    parser.add_argument("--summary-tsv", default=Path("results/handoff/handoff_summary.tsv"), type=Path)
    args = parser.parse_args()

    container_rows: list[dict[str, str]] = []
    for path in args.container_smoke:
        container_rows.extend(read_tsv(path))

    sections = build_handoff_sections(
        release_rows=read_tsv(args.release_checks),
        objective_rows=read_tsv(args.objective_audit),
        readiness_rows=read_tsv(args.readiness),
        container_rows=container_rows,
    )
    write_markdown(sections, args.out)
    write_summary_tsv(sections, args.summary_tsv)


if __name__ == "__main__":
    main()
