"""Command-line interface for extract-color-scheme."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from PIL import UnidentifiedImageError

from extract_color_scheme import __version__
from extract_color_scheme.extractor import ColorSchemeExtractor, SortOrder
from extract_color_scheme.formatters import OutputFormat, format_palette


def _infer_format_from_path(output_path: Path) -> OutputFormat:
    suffix = output_path.suffix.lower()
    if suffix == ".css":
        return "css"
    if suffix in (".txt", ".hex"):
        return "hex"
    return "json"


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="extract-color-scheme",
        description="Extract dominant color palettes from an image using K-Means clustering.",
    )
    parser.add_argument(
        "-i",
        "--image",
        required=True,
        type=Path,
        help="Path to the input image file (.png, .jpg, .webp, etc.).",
    )
    parser.add_argument(
        "-c",
        "--colors",
        type=int,
        default=6,
        help="Number of dominant colors to extract (default: 6).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output file path. If omitted, prints the result to stdout.",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=("json", "css", "hex", "table"),
        default=None,
        help=(
            "Output format (default: inferred from -o extension or 'json' for files, "
            "'table' for stdout)."
        ),
    )
    parser.add_argument(
        "-s",
        "--sort",
        dest="sort_by",
        choices=("dominance", "luminance"),
        default="dominance",
        help="Sort order for extracted colors (default: dominance).",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=256,
        help="Maximum width/height in pixels before clustering (default: 256).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color swatches in table output.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI entry point and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    sort_by: SortOrder = args.sort_by

    try:
        extractor = ColorSchemeExtractor(
            n_colors=args.colors,
            max_image_size=args.max_size,
            sort_by=sort_by,
        )
        palette = extractor.extract(args.image)
    except (FileNotFoundError, ValueError, UnidentifiedImageError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_path: Path | None = args.output
    if args.output_format is not None:
        fmt: OutputFormat = args.output_format
    elif output_path is not None:
        fmt = _infer_format_from_path(output_path)
    else:
        fmt = "table"

    use_color = (not args.no_color) and (output_path is None) and sys.stdout.isatty()
    rendered = format_palette(palette, fmt, colorize=use_color)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Saved {len(palette.colors)} colors to {output_path}")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
