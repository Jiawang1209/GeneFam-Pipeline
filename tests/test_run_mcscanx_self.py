import os
from pathlib import Path

from bin.genefam.run_mcscanx_self import read_tsv, run_mcscanx_self


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def make_executable(path: Path, text: str = "#!/usr/bin/env bash\nexit 0\n") -> Path:
    write(path, text)
    path.chmod(0o755)
    return path


def test_run_mcscanx_self_marks_ready_without_executing_when_tools_exist(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    make_executable(bin_dir / "diamond")
    make_executable(bin_dir / "MCScanX")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    prepared = tmp_path / "mcscanx_self_circos"
    write(prepared / "commands/mcscanx_self_commands.sh", "#!/usr/bin/env bash\ndiamond blastp --help >/dev/null\ntouch executed.marker\n")

    status_path = run_mcscanx_self(prepared_dir=prepared, execute=False)

    rows = read_tsv(status_path)
    assert rows == [
        {
            "status": "ready_not_executed",
            "execute": "false",
            "missing_tools": "",
            "command": "commands/mcscanx_self_commands.sh",
            "exit_code": "",
            "note": "MCScanX dependencies are available; set mcscanx_execute_self=true to execute self BLAST and MCScanX",
        }
    ]
    assert not (prepared / "executed.marker").exists()


def test_run_mcscanx_self_executes_command_script_when_requested(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    make_executable(bin_dir / "diamond", "#!/usr/bin/env bash\nexit 0\n")
    make_executable(bin_dir / "MCScanX")
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")

    prepared = tmp_path / "mcscanx_self_circos"
    write(prepared / "commands/mcscanx_self_commands.sh", "#!/usr/bin/env bash\necho running\nmkdir -p mcscanx_run\ntouch mcscanx_run/A.collinearity\n")

    status_path = run_mcscanx_self(prepared_dir=prepared, execute=True)

    rows = read_tsv(status_path)
    assert rows[0]["status"] == "executed"
    assert rows[0]["execute"] == "true"
    assert rows[0]["exit_code"] == "0"
    assert rows[0]["note"] == "MCScanX self command script executed successfully"
    assert (prepared / "mcscanx_run/A.collinearity").exists()
    assert "running" in (prepared / "mcscanx_execution.log").read_text(encoding="utf-8")


def test_run_mcscanx_self_detects_ncbi_blast_dependencies_from_command_script(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"
    make_executable(bin_dir / "MCScanX")
    monkeypatch.setenv("PATH", str(bin_dir))

    prepared = tmp_path / "mcscanx_self_circos"
    write(prepared / "commands/mcscanx_self_commands.sh", "#!/usr/bin/env bash\nmakeblastdb -h\nblastp -h\n")

    status_path = run_mcscanx_self(prepared_dir=prepared, execute=False)

    rows = read_tsv(status_path)
    assert rows[0]["status"] == "missing_dependency"
    assert rows[0]["missing_tools"] == "makeblastdb,blastp"
