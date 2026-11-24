"""Tests for the core color extraction logic."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from extract_color_scheme.extractor import ColorSchemeExtractor, rgb_to_hex


def _save_image(path: Path, array: np.ndarray, mode: str = "RGB") -> Path:
    img = Image.fromarray(array, mode=mode)
    img.save(path)
    return path


def test_rgb_to_hex() -> None:
    assert rgb_to_hex((0, 0, 0)) == "#000000"
    assert rgb_to_hex((255, 255, 255)) == "#ffffff"
    assert rgb_to_hex((15, 160, 200)) == "#0fa0c8"


def test_extractor_validation() -> None:
    with pytest.raises(ValueError, match="n_colors"):
        ColorSchemeExtractor(n_colors=0)

    with pytest.raises(ValueError, match="max_image_size"):
        ColorSchemeExtractor(max_image_size=0)

    with pytest.raises(ValueError, match="sort_by"):
        ColorSchemeExtractor(sort_by="invalid")  # type: ignore[arg-type]


def test_missing_and_directory_paths(tmp_path: Path) -> None:
    extractor = ColorSchemeExtractor(n_colors=3)

    with pytest.raises(FileNotFoundError):
        extractor.extract(tmp_path / "does_not_exist.png")

    with pytest.raises(ValueError, match="not a file"):
        extractor.extract(tmp_path)


def test_extract_dominant_colors_sorted_by_dominance(tmp_path: Path) -> None:
    # 70% red, 20% green, 10% blue
    data = np.zeros((10, 10, 3), dtype=np.uint8)
    data[:7, :, :] = [255, 0, 0]
    data[7:9, :, :] = [0, 255, 0]
    data[9:, :, :] = [0, 0, 255]
    img_path = _save_image(tmp_path / "blocks.png", data)

    palette = ColorSchemeExtractor(n_colors=3, sort_by="dominance").extract(img_path)

    assert palette.hex_codes() == ["#ff0000", "#00ff00", "#0000ff"]
    assert [c.percentage for c in palette.colors] == [70.0, 20.0, 10.0]


def test_extract_sorted_by_luminance(tmp_path: Path) -> None:
    # Dark blue (low luminance), bright green (high luminance), pure white (highest)
    data = np.zeros((6, 6, 3), dtype=np.uint8)
    data[:2, :, :] = [255, 255, 255]
    data[2:4, :, :] = [0, 255, 0]
    data[4:, :, :] = [0, 0, 255]
    img_path = _save_image(tmp_path / "lum.png", data)

    palette = ColorSchemeExtractor(n_colors=3, sort_by="luminance").extract(img_path)

    assert palette.hex_codes() == ["#0000ff", "#00ff00", "#ffffff"]


def test_extract_ignores_transparent_pixels(tmp_path: Path) -> None:
    # 50% transparent black (should be ignored), 50% opaque orange
    data = np.zeros((10, 10, 4), dtype=np.uint8)
    data[:5, :, :] = [0, 0, 0, 0]
    data[5:, :, :] = [255, 128, 0, 255]
    img_path = _save_image(tmp_path / "alpha.png", data, mode="RGBA")

    palette = ColorSchemeExtractor(n_colors=4).extract(img_path)

    assert palette.hex_codes() == ["#ff8000"]
    assert palette.colors[0].percentage == 100.0


def test_extract_grayscale_image(tmp_path: Path) -> None:
    data = np.zeros((10, 10), dtype=np.uint8)
    data[:6, :] = 40
    data[6:, :] = 200
    img_path = _save_image(tmp_path / "gray.png", data, mode="L")

    palette = ColorSchemeExtractor(n_colors=2, sort_by="dominance").extract(img_path)

    assert palette.hex_codes() == ["#282828", "#c8c8c8"]
    assert [c.percentage for c in palette.colors] == [60.0, 40.0]


def test_extract_fewer_unique_colors_than_requested(tmp_path: Path) -> None:
    data = np.full((8, 8, 3), [12, 34, 56], dtype=np.uint8)
    img_path = _save_image(tmp_path / "solid.png", data)

    palette = ColorSchemeExtractor(n_colors=6).extract(img_path)

    assert len(palette.colors) == 1
    assert palette.colors[0].hex == "#0c2238"
    assert palette.colors[0].percentage == 100.0


@pytest.mark.parametrize("sample_name", ["sample.jpg", "sample.png"])
def test_extract_repo_samples(sample_name: str) -> None:
    sample_path = Path(__file__).resolve().parent.parent / "samples" / sample_name
    palette = ColorSchemeExtractor(n_colors=5).extract(sample_path)

    assert len(palette.colors) == 5
    assert all(c.hex.startswith("#") and len(c.hex) == 7 for c in palette.colors)
    assert pytest.approx(sum(c.percentage for c in palette.colors), abs=0.5) == 100.0
