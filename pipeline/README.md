# wx-tiles — Met Office radar/model tile pipeline

Home-side cron job. Fetches free Met Office open data (no key), renders
WebMercator XYZ PNG tiles with one shared rain-rate LUT, emits `manifest.json`.

## Layout
- `src/wx_tiles/` — `lut.py` (shared color ramp), `s3.py` (unsigned HTTPS),
  `runs.py` (schedules + timeline), `grid.py` (parse + warp + render),
  `manifest.py`, `pipeline.py` (cycle runner)
- `tests/` — pytest, TDD. `WX_LIVE_S3=1` enables the one network test.

## Run
```
pip install -r requirements.txt
PYTHONPATH=src python -m wx_tiles.pipeline --out /srv/tiles --base-url https://tiles.example.com
```
Cron every 15 min. Output is content-addressed (`DONE` markers) so repeat
cycles only fetch + render new frames. Typical cycle: ~25 MB in, ~35 MB tiles.

## Deps
h5py, netCDF4, numpy, Pillow, pyproj (pytest for tests). No GDAL, no AWS account.
