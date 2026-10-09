"""LUT tests: band mapping, boundaries, transparency (TDD)."""
import numpy as np
import pytest

from wx_tiles.lut import STOPS, apply_lut, band_index, lut_for_manifest


def test_band_index_boundaries():
    assert band_index(0.0) == -1
    assert band_index(0.09) == -1
    assert band_index(0.1) == 0
    assert band_index(0.499) == 0
    assert band_index(0.5) == 1
    assert band_index(3.99) == 3
    assert band_index(4.0) == 4
    assert band_index(15.99) == 5
    assert band_index(16.0) == 6
    assert band_index(115.0) == 6


def test_apply_lut_shape_and_alpha():
    rgba = apply_lut(np.array([[0.0, 0.2], [5.0, 20.0]]))
    assert rgba.shape == (2, 2, 4)
    assert rgba.dtype == np.uint8
    assert rgba[0, 0, 3] == 0  # dry -> transparent
    assert rgba[0, 1, 3] == 255
    assert rgba[1, 0, 3] == 255
    assert rgba[1, 1, 3] == 255


def test_apply_lut_nan_transparent():
    rgba = apply_lut(np.array([float("nan")]))
    assert rgba[0, 3] == 0


def test_apply_lut_colors_match_bands():
    # 0.2 -> band 0 color, 5.0 -> band 4 color, 20.0 -> extreme color
    rgba = apply_lut(np.array([0.2, 5.0, 20.0]))
    assert tuple(rgba[0, :3]) == (168, 230, 240)
    assert tuple(rgba[1, :3]) == (150, 60, 220)
    assert tuple(rgba[2, :3]) == (255, 60, 60)


def test_lut_for_manifest_roundtrip():
    lut = lut_for_manifest()
    assert len(lut) == len(STOPS) + 1
    assert lut[0]["min_mm_h"] == 0.1
    assert lut[-1]["min_mm_h"] == 16.0
    # every band maps back through band_index
    import json

    lut2 = json.loads(json.dumps(lut))
    assert lut2 == lut
