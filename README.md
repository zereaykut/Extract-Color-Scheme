# Extract Color Scheme

A fast, lightweight CLI tool and Python library for extracting dominant color palettes from images (`.png`, `.jpg`, `.webp`, etc.) using K-Means clustering.

## Features

- **K-Means Color Extraction**: Identifies the dominant colors in an image along with each color's share (`percentage`), `RGB` tuple, and `HEX` code.
- **Smart Image Handling**: Supports RGB, RGBA (transparent pixels are ignored), grayscale, and palette-based images, with configurable downsampling (`--max-size`) for fast processing.
- **Multiple Output Formats**: Export palettes as `json`, `css` custom properties, plain `hex` lists, or a formatted terminal `table` with 24-bit color swatches.
- **Flexible Sorting**: Sort extracted colors by `dominance` (pixel share) or perceptual `luminance` (ITU-R BT.709).
- **Modern Python Tooling**: Packaged with `pyproject.toml`, managed with [`uv`](https://docs.astral.sh/uv/), linted with `ruff`, and tested with `pytest`.

## Project Structure

```text
Extract-Color-Scheme/
├── samples/
│   ├── sample.jpg
│   └── sample.png
├── src/
│   └── extract_color_scheme/
│       ├── __init__.py
│       ├── cli.py
│       ├── extractor.py
│       └── formatters.py
├── tests/
│   ├── test_cli.py
│   ├── test_extractor.py
│   └── test_formatters.py
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager

## Installation

Clone the repository and sync dependencies with `uv`:

```bash
git clone https://github.com/zereaykut/Extract-Color-Scheme.git
cd Extract-Color-Scheme
uv sync
```

## Usage

Run the CLI directly through `uv`:

```bash
# Print a 6-color palette table in the terminal (using the bundled sample)
uv run extract-color-scheme -i samples/sample.jpg -c 6

# Export palette as JSON
uv run extract-color-scheme -i samples/sample.jpg -c 6 -o palette.json

# Export palette as CSS custom properties (format inferred from .css extension)
uv run extract-color-scheme -i samples/sample.png -c 5 -o palette.css

# Sort by perceptual luminance and print plain hex codes
uv run extract-color-scheme -i samples/sample.jpg -c 6 -s luminance -f hex
```

### CLI Options

| Flag | Long Flag | Description | Default |
| --- | --- | --- | --- |
| `-i` | `--image` | Path to the input image file (required) | — |
| `-c` | `--colors` | Number of dominant colors to extract | `6` |
| `-o` | `--output` | Output file path (prints to stdout if omitted) | `None` |
| `-f` | `--format` | Output format: `json`, `css`, `hex`, `table` | `table` (stdout) / inferred from `-o` |
| `-s` | `--sort` | Sort order: `dominance` or `luminance` | `dominance` |
| — | `--max-size` | Max width/height in pixels before clustering | `256` |
| — | `--no-color` | Disable ANSI color swatches in table output | `False` |
| `-v` | `--version` | Show program version and exit | — |

### Example Output

Running `uv run extract-color-scheme -i samples/sample.jpg -c 6 -f json` outputs:

```json
{
  "image": "samples/sample.jpg",
  "count": 6,
  "colors": [
    {
      "hex": "#1d0c14",
      "rgb": [29, 12, 20],
      "percentage": 55.93
    },
    {
      "hex": "#2c1820",
      "rgb": [44, 24, 32],
      "percentage": 19.87
    },
    {
      "hex": "#452a2a",
      "rgb": [69, 42, 42],
      "percentage": 10.35
    },
    {
      "hex": "#421319",
      "rgb": [66, 19, 25],
      "percentage": 6.72
    },
    {
      "hex": "#6d3b2b",
      "rgb": [109, 59, 43],
      "percentage": 5.78
    },
    {
      "hex": "#c5626c",
      "rgb": [197, 98, 108],
      "percentage": 1.34
    }
  ]
}
```

### Python API

You can also use `ColorSchemeExtractor` directly in Python:

```python
from extract_color_scheme import ColorSchemeExtractor, format_css

extractor = ColorSchemeExtractor(n_colors=5, sort_by="dominance")
palette = extractor.extract("samples/sample.png")

print(palette.hex_codes())
print(format_css(palette))
```

## Development

Run tests and linter checks via `uv`:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
