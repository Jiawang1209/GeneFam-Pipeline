#!/usr/bin/env python3
"""Normalize promoter cis-element annotations and build report-ready tables."""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


NORMALIZED_FIELDS = [
    "species_id",
    "gene_id",
    "element",
    "category",
    "position",
    "strand",
    "description",
]
GENE_CATEGORY_FIELDS = ["species_id", "gene_id", "category", "count"]
GENE_ELEMENT_FIELDS = ["species_id", "gene_id", "element", "category", "count", "positions"]
CATEGORY_SUMMARY_FIELDS = ["category", "element", "total_count", "gene_count", "species_count", "description"]
ELEMENT_ANNOTATION_FIELDS = [
    "element",
    "category",
    "gene_count",
    "species_count",
    "total_count",
    "position_min",
    "position_median",
    "position_max",
    "description",
]

ALIASES = {
    "species_id": ["species_id", "species", "species name", "organism"],
    "gene_id": ["gene_id", "gene id", "gene", "gene name", "sequence name", "seq id", "seq_id"],
    "element": ["element", "cis_element", "cis-element", "care", "cares", "motif", "site name", "name"],
    "category": ["category", "class", "type", "function category", "functional category"],
    "position": ["position", "site", "start", "location", "pos"],
    "strand": ["strand", "orientation"],
    "description": ["description", "function", "annotation", "site function"],
}

CATEGORY_RULES = [
    ("hormone_responsive", ["abscisic", "aba", "abre", "auxin", "gibberellin", "ga-", "meja", "salicylic", "tca-element"]),
    ("stress_responsive", ["stress", "drought", "low-temperature", "low temperature", "defense", "wound", "anaerobic", "ltr", "mbs", "tc-rich"]),
    ("light_responsive", ["light", "g-box", "box 4", "gt1-motif", "sp1", "ae-box", "i-box"]),
    ("growth_development", ["meristem", "endosperm", "circadian", "seed", "pollen", "zein", "cat-box"]),
    ("core_promoter", ["tata", "caat"]),
]


@dataclass(frozen=True)
class PromoterCisTables:
    normalized: list[dict[str, str]]
    gene_category_matrix: list[dict[str, str]]
    gene_element_matrix: list[dict[str, str]]
    category_summary: list[dict[str, str]]
    element_annotations: list[dict[str, str]]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _clean_header(header: str) -> str:
    return re.sub(r"\s+", " ", header.strip().lower().replace("_", " "))


def _alias_map(fieldnames: list[str]) -> dict[str, str]:
    cleaned = {_clean_header(field): field for field in fieldnames}
    mapping: dict[str, str] = {}
    for target, aliases in ALIASES.items():
        for alias in aliases:
            if alias in cleaned:
                mapping[target] = cleaned[alias]
                break
    return mapping


def _get(row: dict[str, str], mapping: dict[str, str], target: str) -> str:
    source = mapping.get(target)
    if not source:
        return ""
    return (row.get(source) or "").strip()


def infer_category(element: str, description: str) -> str:
    haystack = f"{element} {description}".lower()
    for category, terms in CATEGORY_RULES:
        if any(term in haystack for term in terms):
            return category
    return "other"


def _normalize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        return []
    mapping = _alias_map(list(rows[0].keys()))
    normalized: list[dict[str, str]] = []
    for row in rows:
        gene_id = _get(row, mapping, "gene_id")
        element = _get(row, mapping, "element")
        if not gene_id or not element:
            continue
        description = _get(row, mapping, "description")
        category = _get(row, mapping, "category") or infer_category(element, description)
        normalized.append(
            {
                "species_id": _get(row, mapping, "species_id"),
                "gene_id": gene_id,
                "element": element,
                "category": category,
                "position": _get(row, mapping, "position"),
                "strand": _get(row, mapping, "strand"),
                "description": description,
            }
        )
    return normalized


def _gene_category_matrix(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = Counter((row["species_id"], row["gene_id"], row["category"]) for row in rows)
    return [
        {"species_id": species_id, "gene_id": gene_id, "category": category, "count": str(count)}
        for (species_id, gene_id, category), count in sorted(counts.items())
    ]


def _gene_element_matrix(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["species_id"], row["gene_id"], row["element"], row["category"])].append(row)
    matrix: list[dict[str, str]] = []
    for (species_id, gene_id, element, category), group_rows in sorted(grouped.items()):
        positions = sorted({row["position"] for row in group_rows if row.get("position")}, key=lambda value: _position_sort_key(value))
        matrix.append(
            {
                "species_id": species_id,
                "gene_id": gene_id,
                "element": element,
                "category": category,
                "count": str(len(group_rows)),
                "positions": ",".join(positions),
            }
        )
    return matrix


def _position_sort_key(value: str) -> tuple[int, str]:
    parsed = _parse_position(value)
    if parsed is None:
        return (0, value)
    return (parsed, value)


def _parse_position(value: str) -> int | None:
    match = re.search(r"-?\d+", value or "")
    if not match:
        return None
    return int(match.group(0))


def _format_position(value: float | int) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def _category_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["category"], row["element"])].append(row)
    summary: list[dict[str, str]] = []
    for (category, element), group_rows in sorted(grouped.items()):
        descriptions = sorted({row["description"] for row in group_rows if row.get("description")})
        summary.append(
            {
                "category": category,
                "element": element,
                "total_count": str(len(group_rows)),
                "gene_count": str(len({row["gene_id"] for row in group_rows})),
                "species_count": str(len({row["species_id"] for row in group_rows if row.get("species_id")})),
                "description": "; ".join(descriptions[:3]),
            }
        )
    return summary


def _element_annotations(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["element"]].append(row)
    annotations: list[dict[str, str]] = []
    for element, group_rows in sorted(grouped.items()):
        categories = Counter(row["category"] for row in group_rows)
        category = sorted(categories.items(), key=lambda item: (-item[1], item[0]))[0][0]
        descriptions = sorted({row["description"] for row in group_rows if row.get("description")})
        positions = sorted(
            position
            for position in (_parse_position(row.get("position", "")) for row in group_rows)
            if position is not None
        )
        if positions:
            position_min = _format_position(min(positions))
            position_median = _format_position(statistics.median(positions))
            position_max = _format_position(max(positions))
        else:
            position_min = position_median = position_max = ""
        annotations.append(
            {
                "element": element,
                "category": category,
                "gene_count": str(len({row["gene_id"] for row in group_rows})),
                "species_count": str(len({row["species_id"] for row in group_rows if row.get("species_id")})),
                "total_count": str(len(group_rows)),
                "position_min": position_min,
                "position_median": position_median,
                "position_max": position_max,
                "description": "; ".join(descriptions[:3]),
            }
        )
    return annotations


def build_promoter_cis_tables(rows: list[dict[str, str]]) -> PromoterCisTables:
    normalized = _normalize_rows(rows)
    return PromoterCisTables(
        normalized=normalized,
        gene_category_matrix=_gene_category_matrix(normalized),
        gene_element_matrix=_gene_element_matrix(normalized),
        category_summary=_category_summary(normalized),
        element_annotations=_element_annotations(normalized),
    )


def _write_tsv(rows: list[dict[str, str]], fieldnames: list[str], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def write_tables(tables: PromoterCisTables, outdir: Path) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "promoter_cis_elements": outdir / "promoter_cis_elements.tsv",
        "promoter_cis_gene_matrix": outdir / "promoter_cis_gene_matrix.tsv",
        "promoter_cis_gene_element_matrix": outdir / "promoter_cis_gene_element_matrix.tsv",
        "promoter_cis_category_summary": outdir / "promoter_cis_category_summary.tsv",
        "promoter_cis_element_annotations": outdir / "promoter_cis_element_annotations.tsv",
    }
    _write_tsv(tables.normalized, NORMALIZED_FIELDS, outputs["promoter_cis_elements"])
    _write_tsv(tables.gene_category_matrix, GENE_CATEGORY_FIELDS, outputs["promoter_cis_gene_matrix"])
    _write_tsv(tables.gene_element_matrix, GENE_ELEMENT_FIELDS, outputs["promoter_cis_gene_element_matrix"])
    _write_tsv(tables.category_summary, CATEGORY_SUMMARY_FIELDS, outputs["promoter_cis_category_summary"])
    _write_tsv(tables.element_annotations, ELEMENT_ANNOTATION_FIELDS, outputs["promoter_cis_element_annotations"])
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cis-elements", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    args = parser.parse_args()
    tables = build_promoter_cis_tables(read_tsv(args.cis_elements))
    write_tables(tables, args.outdir)


if __name__ == "__main__":
    main()
