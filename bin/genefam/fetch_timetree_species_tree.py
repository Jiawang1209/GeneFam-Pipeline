#!/usr/bin/env python3
"""Optional TimeTree browser automation for species-list Newick export."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


STATUS_FIELDS = ["source", "status", "species_count", "tree", "note"]
VALIDATION_FIELDS = ["latin_name", "newick_label", "status"]


def read_species(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_status(path: Path, *, status: str, species_count: int, tree: Path | None, note: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATUS_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerow(
            {
                "source": "timetree",
                "status": status,
                "species_count": str(species_count),
                "tree": str(tree.resolve()) if tree and tree.exists() else "",
                "note": note,
            }
        )


def newick_label(latin_name: str) -> str:
    return latin_name.replace(" ", "_")


def validate_downloaded_tree(species: list[str], tree: Path, validation: Path) -> tuple[str, str]:
    tree_text = tree.read_text(encoding="utf-8") if tree.exists() else ""
    rows: list[dict[str, str]] = []
    missing: list[str] = []
    for latin_name in species:
        label = newick_label(latin_name)
        found = latin_name in tree_text or label in tree_text
        rows.append({"latin_name": latin_name, "newick_label": label, "status": "found" if found else "missing"})
        if not found:
            missing.append(latin_name)

    validation.parent.mkdir(parents=True, exist_ok=True)
    with validation.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=VALIDATION_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    if missing:
        return (
            "available_with_missing_taxa",
            f"Downloaded Newick tree is missing {len(missing)} of {len(species)} submitted species: {', '.join(missing)}",
        )
    return "available", "Downloaded Newick species tree from TimeTree with all submitted species represented."


def run_timetree_upload(species_list: Path, out_tree: Path, status: Path, *, timeout_ms: int, headless: bool) -> int:
    species = read_species(species_list)
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError:
        write_status(
            status,
            status="pending_manual_upload",
            species_count=len(species),
            tree=None,
            note="Playwright is not installed; upload timetree_species_input.txt to https://timetree.org/ manually and export Newick.",
        )
        return 0

    download_dir = out_tree.parent
    download_dir.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=headless)
            page = browser.new_page(accept_downloads=True)
            page.goto("https://timetree.org/", wait_until="domcontentloaded", timeout=timeout_ms)
            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(str(species_list))
            page.get_by_text("Upload", exact=True).click(timeout=timeout_ms)
            page.wait_for_load_state("networkidle", timeout=timeout_ms)
            try:
                with page.expect_download(timeout=timeout_ms) as download_info:
                    page.get_by_text("Newick", exact=False).click(timeout=timeout_ms)
                download = download_info.value
                download.save_as(str(out_tree))
            except PlaywrightTimeoutError:
                browser.close()
                write_status(
                    status,
                    status="pending_manual_export",
                    species_count=len(species),
                    tree=None,
                    note="TimeTree upload opened, but Newick export was not detected automatically. Export Newick manually from the TimeTree page.",
                )
                return 0
            browser.close()
    except Exception as exc:  # pragma: no cover - depends on external website state
        write_status(
            status,
            status="pending_manual_upload",
            species_count=len(species),
            tree=None,
            note=f"TimeTree automation failed without blocking 01_preprocess: {exc}",
        )
        return 0

    validation = out_tree.parent / "timetree_species_validation.tsv"
    status_value, note = validate_downloaded_tree(species, out_tree, validation)
    write_status(
        status,
        status=status_value,
        species_count=len(species),
        tree=out_tree,
        note=note,
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species-list", required=True, type=Path)
    parser.add_argument("--out-tree", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--timeout-ms", default=180000, type=int)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    raise SystemExit(
        run_timetree_upload(
            args.species_list,
            args.out_tree,
            args.status,
            timeout_ms=args.timeout_ms,
            headless=args.headless,
        )
    )


if __name__ == "__main__":
    main()
