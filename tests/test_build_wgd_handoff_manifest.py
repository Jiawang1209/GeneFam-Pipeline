import subprocess
import sys

from bin.genefam.build_wgd_handoff_manifest import build_handoff_manifest, read_tsv


def test_build_handoff_manifest_marks_family_candidates_available_and_prepared_inputs_pending():
    rows = build_handoff_manifest(
        family_candidates="results/run/tables/family_candidates.tsv",
        duplicates="",
        kaks_pairs="",
        events_config="configs/wgd_events.brassicaceae.yaml",
        ks_bins="0.3,0.8,1.5",
        wgd_event_args="--event WGD_layer_1=alpha --event WGD_layer_2=beta",
    )

    by_item = {row["item"]: row for row in rows}
    assert by_item["family_members"] == {
        "item": "family_members",
        "path": "results/run/tables/family_candidates.tsv",
        "status": "available",
        "required_for": "duplication_retention",
        "description": "Family candidate table produced by the standard identification branch",
    }
    assert by_item["duplicate_types"]["status"] == "pending_user_preparation"
    assert by_item["duplicate_types"]["description"] == "Prepared MCScanX or duplicate-classification table"
    assert by_item["kaks_pairs"]["status"] == "pending_user_preparation"
    assert by_item["events_config"]["status"] == "configured"
    assert by_item["ks_bins"]["path"] == "0.3,0.8,1.5"
    assert by_item["wgd_event_args"]["path"] == "--event WGD_layer_1=alpha --event WGD_layer_2=beta"


def test_build_handoff_manifest_cli_writes_tsv(tmp_path):
    out = tmp_path / "wgd_handoff_manifest.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_wgd_handoff_manifest.py",
            "--family-candidates",
            "results/run/tables/family_candidates.tsv",
            "--events-config",
            "configs/wgd_events.brassicaceae.yaml",
            "--ks-bins",
            "0.3,0.8,1.5",
            "--wgd-event-args",
            "--event WGD_layer_1=alpha --event WGD_layer_2=beta",
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    rows = read_tsv(out)
    assert rows[0]["item"] == "family_members"
    assert rows[1]["item"] == "duplicate_types"
    assert rows[1]["status"] == "pending_user_preparation"
