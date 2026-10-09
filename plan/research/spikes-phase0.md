# Phase 0 spikes — results (2026-10-09, all resolved)

Probed live with curl + Python (venv `/tmp/wx`: h5py, netCDF4, numpy, Pillow, pyproj). Evidence renders in `evidence/`.

## A. Buckets (no key, no signup, eu-west-2)
- Radar: `s3://met-office-radar-obs-data/` (+ SNS `met-office-radar-obs-data-object_created`)
- Model: `s3://met-office-atmospheric-model-data/` (+ SNS `…-atmospheric-model-data-object_created`)
- Unsigned HTTPS listing works (`?list-type=2&prefix=…`), so the pipeline needs only curl/Python — no AWS account.

## B. Radar layout + format
- Path: `radar/YYYY/MM/DD/YYYYMMDDHHMM_ODIM_ng_radar_rainrate_composite_1km_UK.h5` (predictable — pipeline computes today's paths directly).
- Cadence live-verified: 72 files on 2026-10-09, 00:00→17:45, every 15 min. Latest file at 17:56 UTC was 17:45 → **~11 min latency** (better than the 20-min doc claim).
- Size 0.5–1.5 MB/file (varies with weather). 8-frame window ≈ 4–12 MB per cycle.
- Parses with h5py: standard ODIM, `dataset1/data1/data` float32 2175×1725, 1 km transverse-mercator (UK grid), gain 1.0 / offset 0, `quantity=RATE` (mm/h), nodata −1, undetect 0. 17 radars in today's composite.
- Coverage: lat 43.7–62.9, lon −18–+16 (UK + Ireland + N France — generous frame).

## C. UKV precip steps (forecast half)
- Path: `uk-deterministic-2km/<RUN>/…`, RUN = `YYYYMMDDTHHMMZ` (e.g. `20261009T1400Z`).
- File: `<validity>-<lead>-<param>.nc`, e.g. `20261009T1745Z-PT0003H45M-precipitation_rate.nc`. (Gotcha: validity stamp contains a `T` — `20261009T1745Z`, not `202610091745Z`.)
- Nowcast run T1400Z holds **49 × 15-min `precipitation_rate` steps, +0 h → +12 h**. No temporal gap-filling needed for our +6 h window — better than hoped.
- Each file: single var `lwe_precipitation_rate`, 970×1042, Lambert azimuthal equal area, m/s (×3.6e6 → mm/h), **~0.6 MB**. 24 files (+0–6 h) ≈ 15 MB per cycle.
- Run duration attr `PT12H`, grid `uk_extended` v1.7.0. Doc warns of a Jan-2026 format change (superblock v2, status flags, more steps) — pin parser versions, re-check after any parse failure.

## D. Shared-LUT render test
Same blue→purple→orange ramp applied to both: percentile distributions match closely (radar p50 0 / p99 3.07 / p99.9 9.06; UKV p50 0 / p99 3.74 / p99.9 9.70 mm/h). Renders look like believable UK weather in both (`evidence/spike-*.png`). Seamless-timeline premise holds. (First attempt rendered all-orange — my band-mapping bug, not data; fixed version confirmed.)

## E. NSWWS warnings (bonus)
**Free**: 20,000 req/day, burst 200/s (`datahub.metoffice.gov.uk/pricing/warnings`). No quota worry; v2 overlay is unblocked data-wise.

## F. Full-timeline verification (2026-10-09 ~18:06 UTC)
Checked live for the exact Met Office-app timeline:

| Segment | Source | Result |
|---|---|---|
| −6 h → now @15-min | radar/2026/10/09 (73 files, last 18:00) | ✅ 24+ trailing frames present |
| +0 → +12 h @15-min | nowcast T1400Z (49 steps, validities → 10-10T02:00) | ✅ present, with nuance below |
| +12 → +54 h @60-min | short T1200Z (spot-checked +12/+30/+54 h validities, HTTP 206) | ✅ |
| +57 → +120 h @3-hourly | medium T0300Z (spot-checked +57/+120 h, HTTP 206) | ✅ |
| Lead filename format | zero-padded 4-digit hours (`PT0012H00M`, `PT0120H00M`) | ✅ confirmed by existence probes |

**Nuance — run publish lag**: at 18:06 UTC no run newer than T1400Z is published (T15–T18 absent; matches the 3–6 h latency). So the far end of the +12 h window (02:00–06:00) has no 15-min steps *yet* — the per-validity best-run fallback serves those hours from the short run at hourly steps until a newer nowcast publishes. The variable-spacing scrub design already absorbs this: the timeline shows actual available steps, and resolution quietly improves as fresh runs land. Pipeline rule: newest run covering each validity, finest step wins.

## Consequences for the plan
- Pipeline fetch per 15-min cycle: ~8 radar files + ~24 UKV precip files ≈ 20–27 MB. Trivial for home broadband; phone only ever sees rendered tiles.
- Both grids need reprojection to WebMercator XYZ (tmerc + LAEA → EPSG:3857). Phase 2 needs rasterio/GDAL or pyproj+Pillow warp — standard work, no research risk left.
- Manifest schema in ARCHITECTURE.md stands as-is.
