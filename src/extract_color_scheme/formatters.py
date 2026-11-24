"""Output formatters for extracted color palettes."""

from __future__ import annotations

import json
from typing import Literal

from extract_color_scheme.extractor import ColorPalette

OutputFormat = Literal["json", "css", "hex", "table"]


def format_json(palette: ColorPalette) -> str:
    """Format a palette as pretty-printed JSON."""
    return json.dumps(palette.to_dict(), indent=2)


def format_css(palette: ColorPalette, *, prefix: str = "color") -> str:
    """Format a palette as CSS custom properties inside :root."""
    lines = [":root {"]
    for index, color in enumerate(palette.colors, start=1):
        lines.append(f"  --{prefix}-{index}: {color.hex}; /* {color.percentage:.2f}% */")
    lines.append("}")
    return "\n".join(lines)


def format_hex(palette: ColorPalette) -> str:
    """Format a palette as newline-separated hex codes."""
    return "\n".join(palette.hex_codes())


def format_table(palette: ColorPalette, *, colorize: bool = True) -> str:
    """Format a palette as a human-readable table with optional ANSI color swatches."""
    header = f"Palette for {palette.image_path} ({len(palette.colors)} colors):"
    rows = [header]
    for index, color in enumerate(palette.colors, start=1):
        r, g, b = color.rgb
        rgb_str = f"rgb({r:3d}, {g:3d}, {b:3d})"
        swatch = f"\033[48;2;{r};{g};{b}m    \033[0m " if colorize else ""
        rows.append(f"  {index:>2}. {swatch}{color.hex}  {rgb_str}  {color.percentage:6.2f}%")
    return "\n".join(rows)


def format_palette(
    palette: ColorPalette,
    fmt: OutputFormat,
    *,
    colorize: bool = True,
) -> str:
    """Render a ColorPalette using the requested output format."""
    if fmt == "json":
        return format_json(palette)
    if fmt == "css":
        return format_css(palette)
    if fmt == "hex":
        return format_hex(palette)
    if fmt == "table":
        return format_table(palette, colorize=colorize)
    raise ValueError(f"Unsupported output format: {fmt!r}")
