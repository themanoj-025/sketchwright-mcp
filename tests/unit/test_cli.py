"""Unit tests for the Sketchwright command line interface and exit codes."""

from pathlib import Path

import pytest

from sketchwright.cli import main


def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "sketchwright 0.1.0" in captured.out


def test_cli_help_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "usage: sketchwright" in captured.out


def test_cli_capabilities_command(capsys: pytest.CaptureFixture[str]) -> None:
    main(["capabilities"])
    captured = capsys.readouterr()
    assert '"product": "Sketchwright"' in captured.out


def test_cli_validate_valid_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    valid_file = tmp_path / "valid.json"
    valid_file.write_text('{"schema_version": "1.0", "nodes": [{"id": "a"}]}', encoding="utf-8")
    main(["validate", str(valid_file)])
    captured = capsys.readouterr()
    assert "VALID" in captured.out


def test_cli_validate_invalid_file_exit_code_2(tmp_path: Path) -> None:
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text('{"nodes": [{"id": "a"}, {"id": "a"}]}', encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        main(["validate", str(invalid_file)])
    assert exc.value.code == 2


def test_cli_generate_file_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_file = tmp_path / "spec.json"
    input_file.write_text('{"nodes": [{"id": "n1", "label": "Test"}], "edges": []}', encoding="utf-8")
    out_file = tmp_path / "out.excalidraw"

    main(["generate", str(input_file), "-o", str(out_file)])
    assert out_file.is_file()
    captured = capsys.readouterr()
    assert "Generated diagram written to" in captured.out


def test_cli_layout_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_file = tmp_path / "layout_spec.json"
    input_file.write_text(
        '{"nodes": [{"id": "n1"}, {"id": "n2"}], "edges": [{"id": "e", "source": "n1", "target": "n2"}]}',
        encoding="utf-8",
    )

    main(["layout", str(input_file), "--direction", "TB", "--algorithm", "layered"])
    captured = capsys.readouterr()
    assert '"nodes":' in captured.out
    assert '"canvas":' in captured.out


def test_cli_generate_svg(tmp_path: Path) -> None:
    input_file = tmp_path / "spec_svg.json"
    input_file.write_text('{"nodes": [{"id": "n1"}]}', encoding="utf-8")
    out_svg = tmp_path / "out.svg"

    main(["generate", str(input_file), "-o", str(out_svg), "--format", "svg"])
    assert out_svg.is_file()
    assert "<svg" in out_svg.read_text(encoding="utf-8")


def test_cli_module_execution() -> None:
    import subprocess
    import sys

    res = subprocess.run([sys.executable, "-m", "sketchwright", "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "usage: sketchwright" in res.stdout
