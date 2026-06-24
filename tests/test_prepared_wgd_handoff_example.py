from pathlib import Path

from bin.genefam.classify_wgd_layers import classify_pairs
from bin.genefam.join_family_duplicates import join_family_duplicates
from bin.genefam.normalize_duplicate_types import normalize_duplicate_rows
from bin.genefam.run_nextflow_wgd_smoke import WGD_EVENT_ARGS


EXAMPLE_DIR = Path("examples/prepared_wgd_handoff")


def read_tsv(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def test_prepared_wgd_handoff_example_contains_copyable_inputs():
    assert (EXAMPLE_DIR / "README.md").exists()
    assert (EXAMPLE_DIR / "family_candidates.tsv").exists()
    assert (EXAMPLE_DIR / "duplicate_types.tsv").exists()
    assert (EXAMPLE_DIR / "kaks_pairs.tsv").exists()

    family_rows = read_tsv(EXAMPLE_DIR / "family_candidates.tsv")
    duplicate_rows = read_tsv(EXAMPLE_DIR / "duplicate_types.tsv")
    kaks_rows = read_tsv(EXAMPLE_DIR / "kaks_pairs.tsv")

    assert set(family_rows[0]) >= {"species_id", "gene_id"}
    assert set(duplicate_rows[0]) >= {"gene_id", "duplicate_type"}
    assert set(kaks_rows[0]) >= {"gene_a", "gene_b", "ks"}

    normalized = normalize_duplicate_rows(duplicate_rows)
    joined = join_family_duplicates(family_rows, normalized)
    classified = classify_pairs(
        kaks_rows,
        bins=[0.3, 0.8, 1.5],
        named_events={
            "WGD_layer_1": "alpha",
            "WGD_layer_2": "beta",
            "WGD_layer_3": "gamma",
            "WGD_layer_4": "theta",
        },
    )

    assert {row["duplicate_type"] for row in joined} == {"WGD/segmental"}
    assert {row["event_name"] for row in classified} == {"alpha", "beta", "gamma", "theta"}


def test_prepared_wgd_handoff_readme_documents_nextflow_command():
    text = (EXAMPLE_DIR / "README.md").read_text(encoding="utf-8")

    required_snippets = [
        "nextflow run workflows/main.nf",
        "--run_duplication_retention true",
        "--duplicates examples/prepared_wgd_handoff/duplicate_types.tsv",
        "--family_members examples/prepared_wgd_handoff/family_candidates.tsv",
        "--kaks_pairs examples/prepared_wgd_handoff/kaks_pairs.tsv",
        "--events_config configs/wgd_events.brassicaceae.yaml",
        WGD_EVENT_ARGS,
        "results/example_prepared_wgd",
        "wgd_event_evidence.tsv",
        "final_report.md",
    ]
    for snippet in required_snippets:
        assert snippet in text
