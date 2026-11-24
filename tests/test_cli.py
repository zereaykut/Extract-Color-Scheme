"""Tests for the command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from extract_color_scheme.cli import main


@pytest.fixture()
def sample_image(tmp_path: Path) -> Path:
    data = np.zeros((10, 10, 3), dtype=np.uint8)
    data[:6, :, :] = [20, 40, 60]
    data[6:, :, :] = [200, 180, 160]
    path = tmp_path / "test.png"
    Image.fromarray(data, mode="RGB").save(path)
    return path


def test_cli_stdout_json(sample_image: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["-i", str(sample_image), "-c", "2", "-f", "json"])
    assert exit_code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["count"] == 2
    assert [c["hex"] for c in payload["colors"]] == ["#14283c", "#c8b4a0"]


def test_cli_write_output_infers_css_format(
    sample_image: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out_file = tmp_path / "nested" / "palette.css"
    exit_code = main(["-i", str(sample_image), "-c", "2", "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert content.startswith(":root {")
    assert "--color-1: #14283c;" in content

    captured = capsys.readouterr()
    assert "Saved 2 colors" in captured.out


def test_cli_missing_image_returns_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["-i", str(tmp_path / "missing.png")])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_cli_invalid_color_count_returns_error(
    sample_image: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = main(["-i", str(sample_image), "-c", "0"])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "n_colors must be at least 1" in captured.err
