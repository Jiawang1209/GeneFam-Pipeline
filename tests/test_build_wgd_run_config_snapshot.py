import subprocess
import sys

from bin.genefam.build_wgd_run_config_snapshot import build_snapshot, parse_event_args


def test_parse_event_args_accepts_space_and_equals_forms():
    assert parse_event_args("--event WGD_layer_1=alpha --event=WGD_layer_2=beta") == {
        "WGD_layer_1": "alpha",
        "WGD_layer_2": "beta",
    }


def test_build_snapshot_records_wgd_inputs_bins_and_event_mapping():
    rows = build_snapshot(
        events_config="configs/wgd_events.brassicaceae.yaml",
        ks_bins="0.3,0.8,1.5",
        event_args="--event WGD_layer_1=alpha --event WGD_layer_2=beta",
        duplicates="duplicates.tsv",
        family_members="family_candidates.tsv",
        kaks_pairs="kaks_pairs.tsv",
    )

    by_key = {row["key"]: row["value"] for row in rows}
    assert by_key["events_config"] == "configs/wgd_events.brassicaceae.yaml"
    assert by_key["ks_bins"] == "0.3,0.8,1.5"
    assert by_key["duplicates"] == "duplicates.tsv"
    assert by_key["family_members"] == "family_candidates.tsv"
    assert by_key["kaks_pairs"] == "kaks_pairs.tsv"
    assert by_key["event.WGD_layer_1"] == "alpha"
    assert by_key["event.WGD_layer_2"] == "beta"


def test_build_wgd_run_config_snapshot_cli_writes_key_value_tsv(tmp_path):
    out = tmp_path / "wgd_run_config_snapshot.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_wgd_run_config_snapshot.py",
            "--events-config",
            "configs/wgd_events.brassicaceae.yaml",
            "--ks-bins",
            "0.3,0.8,1.5",
            "--event-args",
            "--event WGD_layer_1=alpha --event WGD_layer_2=beta",
            "--duplicates",
            "duplicates.tsv",
            "--family-members",
            "family_candidates.tsv",
            "--kaks-pairs",
            "kaks_pairs.tsv",
            "--out",
            str(out),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("key\tvalue\n")
    assert "event.WGD_layer_1\talpha\n" in text
    assert "event.WGD_layer_2\tbeta\n" in text
