import subprocess
import sys
from pathlib import Path

from bin.genefam.build_run_plan import build_run_plan
from bin.genefam.validate_config import load_config


def test_build_run_plan_records_runtime_species_and_module_switches():
    config = {
        "project": {"name": "GDSL_demo", "outdir": "results/GDSL_demo"},
        "runtime": {"environment": "GeneFamilyFlow", "r_bin": "/usr/local/bin/R"},
        "run": {"species_group": "brassicaceae_core"},
        "species": {"include": ["Arabidopsis_thaliana"], "exclude": ["Camelina_sativa"]},
        "dev": {"mock_external_tools": True},
        "modules": {"identification": True, "phylogeny": False, "report": True},
    }

    rows = build_run_plan(config)

    assert rows == [
        {"section": "project", "key": "name", "value": "GDSL_demo"},
        {"section": "project", "key": "outdir", "value": "results/GDSL_demo"},
        {"section": "runtime", "key": "environment", "value": "GeneFamilyFlow"},
        {"section": "runtime", "key": "r_bin", "value": "/usr/local/bin/R"},
        {"section": "species", "key": "species_group", "value": "brassicaceae_core"},
        {"section": "species", "key": "include", "value": "Arabidopsis_thaliana"},
        {"section": "species", "key": "exclude", "value": "Camelina_sativa"},
        {"section": "dev", "key": "mock_external_tools", "value": "true"},
        {"section": "module", "key": "identification", "value": "enabled"},
        {"section": "module", "key": "phylogeny", "value": "disabled"},
        {"section": "module", "key": "report", "value": "enabled"},
    ]


def test_example_config_run_plan_includes_expected_disabled_wgd_modules():
    rows = build_run_plan(load_config(Path("configs/example.config.yaml")))
    by_key = {(row["section"], row["key"]): row["value"] for row in rows}

    assert by_key[("runtime", "environment")] == "GeneFamilyFlow"
    assert by_key[("runtime", "r_bin")] == "/usr/local/bin/R"
    assert by_key[("module", "identification")] == "enabled"
    assert by_key[("module", "duplication_retention")] == "disabled"
    assert by_key[("module", "kaks")] == "disabled"
    assert by_key[("module", "report")] == "enabled"


def test_build_run_plan_cli_writes_tsv(tmp_path):
    out_path = tmp_path / "run_plan.tsv"

    completed = subprocess.run(
        [
            sys.executable,
            "bin/genefam/build_run_plan.py",
            "--config",
            "configs/example.config.yaml",
            "--out",
            str(out_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    text = out_path.read_text(encoding="utf-8")
    assert text.startswith("section\tkey\tvalue\n")
    assert "runtime\tenvironment\tGeneFamilyFlow\n" in text
    assert "module\treport\tenabled\n" in text
