"""Extract dominant color palettes from images using K-Means clustering."""

from extract_color_scheme.extractor import (
    ColorInfo,
    ColorPalette,
    ColorSchemeExtractor,
    SortOrder,
    rgb_to_hex,
)
from extract_color_scheme.formatters import (
    OutputFormat,
    format_css,
    format_hex,
    format_json,
    format_palette,
    format_table,
)

__version__ = "0.2.0"

__all__ = [
    "ColorInfo",
    "ColorPalette",
    "ColorSchemeExtractor",
    "OutputFormat",
    "SortOrder",
    "__version__",
    "format_css",
    "format_hex",
    "format_json",
    "format_palette",
    "format_table",
    "rgb_to_hex",
]
