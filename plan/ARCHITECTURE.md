# Architecture (draft)

## Data flow
```
Met Office AWS open data (S3)          DataHub API
  radar HDF5 (15-min)  UKV 2km NetCDF   spot/blended JSON
        \                  /                     |
         \                /                      |
      home tile pipeline (Python, 15-min cron)   | (direct from phone)
      renders with shared LUT                     |
        /                  \                     |
  XYZ PNG tiles +      manifest.json              |
  snapshot.png      (+ coverage mask)             |
        \                  /                     |
         v                v                       v
              Fork app (Breezy + CARD_RADAR + metoffice source)
              MapLibre (maplibre-compose) + OFM basemap
```

## Pipeline (home PC/Pi/VPS)
- Fetch latest radar composite + UKV precip steps; render XYZ PNGs z0–7 (SDK overzooms beyond).
- Emit `manifest.json`: `{ generated, now_index, lut: [{ max_mm_h, color }], frames: [{ t, kind: "obs"|"model", run, tiles: "<url>/{z}/{x}/{y}.png" }], snapshot: "<url>/snapshot.png", coverage: "<url>/mask/…" }`. The embedded LUT lets the app invert tile pixels into band readouts without a data API.
- Serve over HTTP (Tailscale/tunnel to phone); phone caches tiles + prefetches via WorkManager.

## App (fork, freenet flavor)
- `sources/metoffice/`: DataHub adapter (copy of pirateweather template); key in `local.properties`.
- `CARD_RADAR`: snapshot card (coils-style cached PNG) → detail screen; source-independent (lat/lon keyed).
- Detail screen: maplibre-compose map + windowed opacity frames + scrub bar + now-marker + obs/forecast badge + tap-for-band readout (LUT inversion → e.g. "2–4 mm/h", never fake exactness); day/night style switch from Breezy theme state. Ported RTR files keep MIT headers.
- Darkened-positron style JSON hosted alongside pipeline (or in-app asset).

## Operations (locked 2026-10-09)
- **Refresh**: pipeline cron every 15 min, idempotent (fetches trailing windows, skips existing). Radar frames appear ~5–11 min after validity (observed). Model frames refresh from the latest nowcast run (16 runs/day); hourly re-check is plenty.
- **Call budget**: AWS open data is quota-free (no key, ~3k small GETs/day from one pipeline — polite, not rate-limited). Phone→pipeline is our own server (unlimited). DataHub quotas (spot 360/d, blended 55/d, NSWWS 20k/d) bind only the forecast source, not radar.
- **Phone prefetch**: refresh on app open + WorkManager every ~30 min on Wi-Fi; tiles + manifest cached in Room/disk. No background cost worth optimizing for one user.
- **Map interaction**: full pan/zoom. Radar tiles rendered z0–7, SDK overzooms beyond (RTR precedent); vector basemap stays sharp underneath. Outside radar coverage → coverage-mask transparency (never fake clear-sky). Snapshot card uses fixed zoom on home location.
- **Time window** (Met Office-app parity, locked 2026-10-09): obs −6 h @15-min (24 frames, 1 km) → now → model +12 h @15-min (48 frames) → +54 h @60-min → +120 h @3-hourly (2 km throughout). ~110-frame scrub with variable spacing; slider ticks cluster at hours/days. No temporal interpolation — manual scrub lands on real frames only (interpolation was an animation problem; we have no animation).
- **Resolution over time**: 15-min steps for −6 h → +12 h; hourly +12→54 h; 3-hourly +54→120 h. Spatial steps once, 1 km → 2 km, at the now-boundary (shared LUT hides most of it). Run selection: newest *published* run covering each validity, finest step wins (nowcast 15-min → short hourly → medium 3-hourly). Runs publish 3–6 h late, so the far +12 h end is hourly until fresh nowcasts land — the variable-spacing scrub absorbs this by construction.
- **Frame loading**: ~110 RasterSources alive (RTR's keep-all pattern) is too heavy — detail screen instantiates a sliding window of layers around the scrub index (nearest ±3 full, rest on demand) with LRU tile cache. Snapshot card unaffected (single PNG).

## Key trade-offs (locked)
- Tiles rendered server-side (not on-device): battery + HDF5 libs.
- Static snapshot in card (not live mini-map): list perf.
- Manual scrub, no autoplay: simpler state, user preference.
