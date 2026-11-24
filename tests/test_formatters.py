"""Tests for palette output formatters."""

from __future__ import annotations

import json
from pathlib import Path

from extract_color_scheme.extractor import ColorInfo, ColorPalette
from extract_color_scheme.formatters import (
    format_css,
    format_hex,
    format_json,
    format_palette,
    format_table,
)


def _sample_palette() -> ColorPalette:
    return ColorPalette(
        image_path=Path("samples/sample.png"),
        colors=(
            ColorInfo(hex="#112233", rgb=(17, 34, 51), percentage=65.5),
            ColorInfo(hex="#aabbcc", rgb=(170, 187, 204), percentage=34.5),
        ),
    )


def test_format_json() -> None:
    data = json.loads(format_json(_sample_palette()))
    assert data == {
        "image": "samples/sample.png",
        "count": 2,
        "colors": [
            {"hex": "#112233", "rgb": [17, 34, 51], "percentage": 65.5},
            {"hex": "#aabbcc", "rgb": [170, 187, 204], "percentage": 34.5},
        ],
    }


def test_format_css() -> None:
    css = format_css(_sample_palette())
    assert css == (
        ":root {\n  --color-1: #112233; /* 65.50% */\n  --color-2: #aabbcc; /* 34.50% */\n}"
    )


def test_format_hex() -> None:
    assert format_hex(_sample_palette()) == "#112233\n#aabbcc"


def test_format_table_without_ansi() -> None:
    table = format_table(_sample_palette(), colorize=False)
    assert "Palette for samples/sample.png (2 colors):" in table
    assert "#112233" in table
    assert "rgb( 17,  34,  51)" in table
    assert "\033[" not in table


def test_format_table_with_ansi() -> None:
    table = format_table(_sample_palette(), colorize=True)
    assert "\033[48;2;17;34;51m" in table


def test_format_palette_dispatch() -> None:
    palette = _sample_palette()
    assert format_palette(palette, "hex") == "#112233\n#aabbcc"
