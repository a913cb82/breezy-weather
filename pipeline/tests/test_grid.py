"""Grid warp + tile render tests (TDD)."""
import numpy as np
import pytest

from wx_tiles.grid import (
    parse_radar,
    parse_ukv,
    render_tiles,
    tile_bounds_3857,
)


def test_tile_bounds_3857():
    # z0 single tile spans the world
    xmin, ymin, xmax, ymax = tile_bounds_3857(0, 0, 0)
    assert xmin == pytest.approx(-20037508.34, abs=1)
    assert xmax == pytest.approx(20037508.34, abs=1)
    # z1 tiles quarter it
    a = tile_bounds_3857(1, 0, 0)
    b = tile_bounds_3857(1, 1, 1)
    assert a[2] == pytest.approx(0.0, abs=1)  # xmax of NW tile
    assert b[0] == pytest.approx(0.0, abs=1)  # xmin of SE tile


def test_render_tiles_identity():
    # 2x2-degree block at equator in EPSG:3857, TL pixel wet, rest dry
    data = np.zeros((4, 4))
    data[0, 0] = 5.0
    out = {}
    tiles = render_tiles(data, "EPSG:3857", (-111319.5, -111319.5, 111319.5, 111319.5),
                         zmin=5, zmax=5, tile_size=64, sink=out.__setitem__)
    assert len(tiles) >= 1
    # wet pixel lands opaque in its tile
    opaque = [k for k, png in out.items()]
    assert opaque
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(out[opaque[0]]))
    assert img.size == (64, 64)
    assert np.array(img)[:, :, 3].max() == 255


def test_render_tiles_all_dry_skipped():
    out = {}
    tiles = render_tiles(np.zeros((4, 4)), "EPSG:3857",
                         (-111319.5, -111319.5, 111319.5, 111319.5),
                         zmin=5, zmax=5, tile_size=64, sink=out.__setitem__)
    assert tiles == [] and out == {}


def test_parse_radar_fixture():
    pytest.importorskip("h5py")
    import os
    path = os.environ.get("WX_RADAR_FIXTURE", "/tmp/radar.h5")
    if not os.path.exists(path):
        pytest.skip("no radar fixture")
    with open(path, "rb") as f:
        g = parse_radar(f.read())
    import numpy as np
    assert g["data"].shape == (2175, 1725)
    assert np.nanmin(g["data"]) >= -1.0  # nodata stored as NaN
    assert "tmerc" in g["proj"]


def test_parse_ukv_fixture():
    pytest.importorskip("netCDF4")
    import os
    path = os.environ.get("WX_UKV_FIXTURE", "/tmp/precip.nc")
    if not os.path.exists(path):
        pytest.skip("no ukv fixture")
    with open(path, "rb") as f:
        g = parse_ukv(f.read())
    assert g["data"].shape == (970, 1042)
    assert "units_mm_h" in g and g["units_mm_h"] is True
