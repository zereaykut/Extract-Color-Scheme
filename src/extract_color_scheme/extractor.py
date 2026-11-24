"""Core K-Means color palette extraction logic."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

SortOrder = Literal["dominance", "luminance"]

_VALID_SORT_ORDERS: tuple[SortOrder, ...] = ("dominance", "luminance")


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert an (R, G, B) tuple in 0..255 to a lowercase hex color string."""
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


@dataclass(frozen=True, slots=True)
class ColorInfo:
    """Represents an extracted color and its share in the image."""

    hex: str
    rgb: tuple[int, int, int]
    percentage: float

    @property
    def luminance(self) -> float:
        """Perceptual relative luminance (ITU-R BT.709) in the 0..255 range."""
        r, g, b = self.rgb
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def to_dict(self) -> dict[str, Any]:
        """Serialize color information to a JSON-friendly dictionary."""
        return {
            "hex": self.hex,
            "rgb": list(self.rgb),
            "percentage": self.percentage,
        }


@dataclass(frozen=True, slots=True)
class ColorPalette:
    """Extracted color palette for a single source image."""

    image_path: Path
    colors: tuple[ColorInfo, ...]

    def hex_codes(self) -> list[str]:
        """Return ordered list of hex color codes."""
        return [color.hex for color in self.colors]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the palette to a JSON-friendly dictionary."""
        return {
            "image": str(self.image_path),
            "count": len(self.colors),
            "colors": [color.to_dict() for color in self.colors],
        }


class ColorSchemeExtractor:
    """Extract dominant colors from an image using K-Means clustering."""

    def __init__(
        self,
        n_colors: int = 6,
        *,
        max_image_size: int = 256,
        random_state: int = 42,
        sort_by: SortOrder = "dominance",
    ) -> None:
        if n_colors < 1:
            raise ValueError(f"n_colors must be at least 1, got {n_colors}")
        if max_image_size < 1:
            raise ValueError(f"max_image_size must be at least 1, got {max_image_size}")
        if sort_by not in _VALID_SORT_ORDERS:
            raise ValueError(f"sort_by must be one of {_VALID_SORT_ORDERS}, got {sort_by!r}")

        self.n_colors = n_colors
        self.max_image_size = max_image_size
        self.random_state = random_state
        self.sort_by = sort_by

    def load_pixels(self, image_path: str | Path) -> np.ndarray:
        """Load an image, resize for fast clustering, and return an (N, 3) uint8 RGB array."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        with Image.open(path) as img:
            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            )
            prepared = img.convert("RGBA" if has_alpha else "RGB")
            if max(prepared.size) > self.max_image_size:
                prepared.thumbnail(
                    (self.max_image_size, self.max_image_size),
                    Image.Resampling.LANCZOS,
                )
            pixels = np.asarray(prepared, dtype=np.uint8)

        if has_alpha:
            flat = pixels.reshape(-1, 4)
            opaque = flat[flat[:, 3] >= 128][:, :3]
            # Fall back to all RGB pixels if the image is fully transparent.
            return opaque if len(opaque) > 0 else flat[:, :3]

        return pixels.reshape(-1, 3)

    def extract(self, image_path: str | Path) -> ColorPalette:
        """Extract a sorted color palette from the given image path."""
        path = Path(image_path)
        pixels = self.load_pixels(path)
        total_pixels = len(pixels)

        unique_colors, unique_counts = np.unique(pixels, axis=0, return_counts=True)

        if len(unique_colors) <= self.n_colors:
            centers = unique_colors
            counts = unique_counts
        else:
            model = KMeans(
                n_clusters=self.n_colors,
                random_state=self.random_state,
                n_init="auto",
            )
            labels = model.fit_predict(pixels)
            centers = np.clip(np.rint(model.cluster_centers_), 0, 255).astype(np.uint8)
            counts = np.bincount(labels, minlength=self.n_colors)

        colors: list[ColorInfo] = []
        for center, count in zip(centers, counts, strict=True):
            if count == 0:
                continue
            rgb = (int(center[0]), int(center[1]), int(center[2]))
            percentage = round(float(count) / total_pixels * 100.0, 2)
            colors.append(
                ColorInfo(
                    hex=rgb_to_hex(rgb),
                    rgb=rgb,
                    percentage=percentage,
                )
            )

        if self.sort_by == "dominance":
            colors.sort(key=lambda c: (-c.percentage, c.luminance, c.hex))
        else:
            colors.sort(key=lambda c: (c.luminance, -c.percentage, c.hex))

        return ColorPalette(image_path=path, colors=tuple(colors))
