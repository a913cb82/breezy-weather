"""Shared rain-rate -> color lookup table (single LUT for obs + model)."""
import numpy as np

# (lower bound mm/h, RGB). <0.1 is transparent (dry / no-data handled by alpha).
STOPS = [0.1, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
COLORS = [
    (168, 230, 240),  # drizzle
    (120, 200, 250),  # light rain
    (60, 140, 250),  # moderate
    (60, 60, 220),  # heavy
    (150, 60, 220),  # very heavy
    (220, 60, 200),  # intense
    (250, 140, 40),  # convective
]
EXTREME_COLOR = (255, 60, 60)  # >= 16 mm/h


def band_index(value_mm_h: float) -> int:
    """0-based band for a rain rate, or -1 when below the first stop."""
    for i in range(len(STOPS) - 1, -1, -1):
        if value_mm_h >= STOPS[i]:
            return i
    return -1


def apply_lut(values_mm_h: np.ndarray) -> np.ndarray:
    """Map rain rates to RGBA. Values <0.1 (or NaN) become transparent."""
    values = np.asarray(values_mm_h, dtype=float)
    out = np.zeros(values.shape + (4,), dtype=np.uint8)
    valid = (values >= STOPS[0]) & np.isfinite(values)
    for i, color in enumerate(COLORS):
        hi = STOPS[i + 1] if i + 1 < len(STOPS) else 16.0
        sel = valid & (values >= STOPS[i]) & (values < hi)
        out[sel, :3] = color
        out[sel, 3] = 255
    sel = valid & (values >= 16.0)
    out[sel, :3] = EXTREME_COLOR
    out[sel, 3] = 255
    return out


def lut_for_manifest() -> list:
    """JSON-serializable LUT so the app can invert tile pixels into bands."""
    return [{"min_mm_h": lo, "color": list(c)} for lo, c in zip(STOPS, COLORS)] + [
        {"min_mm_h": 16.0, "color": list(EXTREME_COLOR)}
    ]
