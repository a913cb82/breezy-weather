"""Grid parsing (ODIM HDF5 radar, UKV NetCDF) + WebMercator XYZ tile render."""
import io
import math

import numpy as np
from PIL import Image

from wx_tiles.lut import apply_lut

TILE = 256
R = 6378137.0
WORLD = 2 * math.pi * R


def render_snapshot(data: np.ndarray, src_proj: str, src_extent,
                    lonlat_bbox, width: int = 768) -> bytes:
    """Fixed-view PNG (card snapshot): lonlat_bbox=(lon0,lat0,lon1,lat1)."""
    import pyproj
    lon0, lat0, lon1, lat1 = lonlat_bbox
    aspect = (lat1 - lat0) / max(lon1 - lon0, 1e-9)
    height = max(1, int(width * aspect * 1.4))  # lat degrees are taller on screen
    inv = pyproj.Transformer.from_crs("EPSG:4326", src_proj, always_xy=True)
    sxmin, symin, sxmax, symax = src_extent
    h, w = data.shape
    GX = np.linspace(lon0, lon1, width)
    GY = np.linspace(lat1, lat0, height)
    GXG, GYG = np.meshgrid(GX, GY)
    SX, SY = inv.transform(GXG.ravel(), GYG.ravel())
    SX = np.array(SX).reshape(height, width)
    SY = np.array(SY).reshape(height, width)
    px = ((SX - sxmin) / (sxmax - sxmin) * (w - 1)).round().astype(int)
    py = ((symax - SY) / (symax - symin) * (h - 1)).round().astype(int)
    ok = (px >= 0) & (px < w) & (py >= 0) & (py < h)
    vals = np.full((height, width), np.nan)
    vals[ok] = data[py[ok], px[ok]]
    buf = io.BytesIO()
    Image.fromarray(_default_colorize(vals)).save(buf, format="PNG")
    return buf.getvalue()


def mask_colorize(values_mm_h: np.ndarray) -> np.ndarray:
    """Black where the radar has no coverage, transparent elsewhere."""
    out = np.zeros(values_mm_h.shape + (4,), dtype=np.uint8)
    nocov = ~np.isfinite(values_mm_h)
    out[nocov] = (0, 0, 0, 255)
    return out


def tile_bounds_3857(z: int, x: int, y: int):
    n = 2 ** z
    size = WORLD / n
    xmin = -WORLD / 2 + x * size
    xmax = xmin + size
    ymax = WORLD / 2 - y * size
    ymin = ymax - size
    return xmin, ymin, xmax, ymax


def _corners_to_extent(transformer, lon_lat_corners):
    xs, ys = transformer.transform(
        [c[0] for c in lon_lat_corners], [c[1] for c in lon_lat_corners])
    return min(xs), min(ys), max(xs), max(ys)


def _s(v) -> str:
    return v.decode() if isinstance(v, (bytes, bytearray)) else str(v)


def parse_radar(blob: bytes) -> dict:
    import h5py
    with h5py.File(io.BytesIO(blob), "r") as f:
        raw = np.asarray(f["dataset1/data1/data"][:], dtype="float32")
        try:
            w = f["dataset1/where"].attrs
        except KeyError:
            w = f["where"].attrs
        what = f["dataset1/data1/what"].attrs
        projdef = _s(w["projdef"])
        corners = [(float(w["UL_lon"]), float(w["UL_lat"])),
                   (float(w["UR_lon"]), float(w["UR_lat"])),
                   (float(w["LL_lon"]), float(w["LL_lat"])),
                   (float(w["LR_lon"]), float(w["LR_lat"]))]
        try:
            gain, offset = float(what["gain"]), float(what["offset"])
        except KeyError:
            gain, offset = 1.0, 0.0
    data = raw * gain + offset
    data[raw == -1.0] = np.nan  # nodata -> transparent
    import pyproj
    fwd = pyproj.Transformer.from_crs("EPSG:4326", projdef, always_xy=True)
    extent = _corners_to_extent(fwd, corners)
    return {"data": data, "proj": projdef, "extent": extent}


def parse_ukv(blob: bytes) -> dict:
    import netCDF4
    with netCDF4.Dataset("in-mem", memory=blob) as d:
        var = d["lwe_precipitation_rate"]
        data = np.asarray(var[:], dtype="float32") * 3600000.0  # m/s -> mm/h
        xc = np.asarray(d["projection_x_coordinate"][:], dtype="float64")
        yc = np.asarray(d["projection_y_coordinate"][:], dtype="float64")
        dx = float(xc[1] - xc[0]) if len(xc) > 1 else 2000.0
        dy = float(yc[1] - yc[0]) if len(yc) > 1 else 2000.0
        mapping = None
        for v in d.variables.values():
            if getattr(v, "grid_mapping_name", "") == "lambert_azimuthal_equal_area":
                mapping = v
                break
        proj = ("+proj=laea +lat_0=%s +lon_0=%s +x_0=0 +y_0=0 +ellps=WGS84 +units=m"
                % (mapping.getncattr("latitude_of_projection_origin"),
                   mapping.getncattr("longitude_of_projection_origin")))
        extent = (float(xc.min() - dx / 2), float(yc.min() - dy / 2),
                  float(xc.max() + dx / 2), float(yc.max() + dy / 2))
    data[~np.isfinite(data)] = np.nan
    return {"data": data, "proj": proj, "extent": extent, "units_mm_h": True}


def _tiles_for_extent(extent_3857, z):
    xmin, ymin, xmax, ymax = extent_3857
    n = 2 ** z
    size = WORLD / n
    x0 = max(0, int(math.floor((xmin + WORLD / 2) / size)))
    x1 = min(n - 1, int(math.floor((xmax + WORLD / 2) / size)))
    y0 = max(0, int(math.floor((WORLD / 2 - ymax) / size)))
    y1 = min(n - 1, int(math.floor((WORLD / 2 - ymin) / size)))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            yield x, y


def _default_colorize(values_mm_h: np.ndarray) -> np.ndarray:
    return apply_lut(np.where(np.isnan(values_mm_h), -1.0, values_mm_h))


def render_tiles(data: np.ndarray, src_proj: str, src_extent, zmin: int, zmax: int,
                 tile_size: int = TILE, sink=None, colorize=None) -> list:
    """Nearest-neighbor warp to XYZ PNGs. Returns [(z,x,y)] rendered; dry tiles skipped."""
    colorize = colorize or _default_colorize
    import pyproj
    h, w = data.shape
    sxmin, symin, sxmax, symax = src_extent
    inv = pyproj.Transformer.from_crs("EPSG:3857", src_proj, always_xy=True)
    rendered = []
    for z in range(zmin, zmax + 1):
        # project source extent into webmercator once per zoom (approx via corners+edges)
        fwd = pyproj.Transformer.from_crs(src_proj, "EPSG:3857", always_xy=True)
        ex = np.linspace(sxmin, sxmax, 33)
        ey = np.linspace(symin, symax, 33)
        edge = [(float(x), symin) for x in ex] + [(float(x), symax) for x in ex] + \
               [(sxmin, float(y)) for y in ey] + [(sxmax, float(y)) for y in ey]
        mx, my = fwd.transform([p[0] for p in edge], [p[1] for p in edge])
        ext3857 = (min(mx), min(my), max(mx), max(my))
        for x, y in _tiles_for_extent(ext3857, z):
            xmin, ymin, xmax, ymax = tile_bounds_3857(z, x, y)
            gx = np.linspace(xmin, xmax, tile_size)
            gy = np.linspace(ymax, ymin, tile_size)  # top row first
            GX, GY = np.meshgrid(gx, gy)
            SX, SY = inv.transform(GX.ravel(), GY.ravel())
            SX = np.array(SX).reshape(tile_size, tile_size)
            SY = np.array(SY).reshape(tile_size, tile_size)
            with np.errstate(invalid="ignore"):
                px = ((SX - sxmin) / (sxmax - sxmin) * (w - 1)).round().astype(int)
                py = ((symax - SY) / (symax - symin) * (h - 1)).round().astype(int)
            ok = (px >= 0) & (px < w) & (py >= 0) & (py < h)
            vals = np.full((tile_size, tile_size), np.nan)
            vals[ok] = data[py[ok], px[ok]]
            rgba = colorize(vals)
            if rgba[:, :, 3].max() == 0:
                continue
            buf = io.BytesIO()
            Image.fromarray(rgba).save(buf, format="PNG")
            if sink is not None:
                sink((z, x, y), buf.getvalue())
            rendered.append((z, x, y))
    return rendered
