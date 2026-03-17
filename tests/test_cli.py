import json
import subprocess


def test_cli_help():
    result = subprocess.run(["b2mml", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_convert(tmp_path):
    input_file = "tests/data/sample_ampla.xml"
    output_file = tmp_path / "out.xml"

    result = subprocess.run(
        ["b2mml", "convert", input_file, str(output_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_file.exists()
    assert "<ShowEquipmentInformation" in output_file.read_text()


def test_cli_json(tmp_path):
    input_file = "tests/data/sample_ampla.xml"
    output_file = tmp_path / "out.json"

    result = subprocess.run(
        ["b2mml", "json", input_file, str(output_file)], capture_output=True, text=True
    )

    assert result.returncode == 0
    assert output_file.exists()

    data = json.loads(output_file.read_text())
    assert "equipment" in data
    assert "classes" in data


def test_cli_json_stdout():
    input_file = "tests/data/sample_ampla.xml"

    result = subprocess.run(
        ["b2mml", "json", input_file], capture_output=True, text=True
    )

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "equipment" in data
