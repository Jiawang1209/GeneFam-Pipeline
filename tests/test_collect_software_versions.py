from bin.genefam.collect_software_versions import collect_versions


def test_collect_versions_records_detected_and_missing_tools():
    def fake_command_runner(command):
        joined = " ".join(command)
        if "nextflow" in joined:
            return 0, "nextflow version 26.04.4\n"
        return 127, ""

    def fake_r_package_runner(package):
        if package == "ggplot2":
            return "3.5.2"
        return None

    rows = collect_versions(
        command_runner=fake_command_runner,
        r_package_runner=fake_r_package_runner,
        tool_commands={"Nextflow": ["nextflow", "-version"], "MCScanX": ["MCScanX"]},
        r_packages=["ggplot2", "ggNetView"],
    )
    by_component = {row["component"]: row for row in rows}

    assert by_component["Nextflow"]["status"] == "detected"
    assert by_component["Nextflow"]["version"] == "nextflow version 26.04.4"
    assert by_component["MCScanX"]["status"] == "version_not_detected"
    assert by_component["ggplot2"]["version"] == "3.5.2"
    assert by_component["ggNetView"]["status"] == "version_not_detected"


def test_collect_versions_records_file_not_found_as_missing_tool():
    def missing_command_runner(command):
        raise FileNotFoundError(command[0])

    rows = collect_versions(
        command_runner=missing_command_runner,
        r_package_runner=lambda package: None,
        tool_commands={"IQ-TREE": ["iqtree2", "--version"]},
        r_packages=[],
    )

    assert rows == [
        {
            "component": "IQ-TREE",
            "kind": "command",
            "version": "version_not_detected",
            "status": "version_not_detected",
            "source": "iqtree2 --version",
        }
    ]
