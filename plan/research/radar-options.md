# Radar options (UK) — P0 feature research

## TL;DR
**Prototype with RainViewer (zero backend, minutes to first frame). In parallel, spike a Met Office AWS-HDF5 → tile pipeline — that is the UK-native, license-clean, long-term radar.** DataHub Map Images is not radar. Breezy has no radar (we can leapfrog it).

## 1. Comparison

| Source | UK res / cadence | History + nowcast | Cost | License | Format | Verdict |
|---|---|---|---|---|---|---|
| **RainViewer Weather Maps API** | ~1 km composite (1200+ radars, 150+ countries; UK fed by Met Office network) / 10-min frames, past 2 h; marketing claims 5-min refresh, 2-min on paid app tiers | Past 2 h tiles; nowcast/forecast only inside RainViewer apps (30–120 min tiers) | Free, **no key** | Personal / educational / small-community only; attribution `weather data by RainViewer` + link; **commercial/high-volume = contact them, bespoke terms**; no SLA | `weather-maps.json` → `{host}/{path}/{size}/{z}/{x}/{y}/{color}/{options}.png` (z≤7, smooth/snow flags, custom color tables allowed) | ✅ **Prototype now** |
| **Met Office UK radar on AWS Open Data** | 1 km NIMROD-heritage UK composite rain-rate / **4 images/hr (15-min), ~20-min latency**, 2-yr rolling archive | Archive yes; nowcast no (we'd extrapolate or pair with model) | Free data (pay own AWS/compute) | **CC BY-SA** (British Crown copyright) — shippable with attribution | HDF5 composites — **we build the tile pipeline** | ✅ **Strategic bet — spike next** |
| Met Office DataHub Map Images | ~10 km global-model viz (precip *rate forecast*, not observed radar) | n/a | Free beta (1000/day) | DataHub T&Cs | PNG, preset UK/Europe regions | ❌ Not radar |
| EUMETSAT OPERA European composite | EU composite incl. UK / 15-min | Archive via EUMETSAT | Free w/ registration (EUMETSAT license) | EUMETSAT terms | Varies (need spike) | ➖ Fallback, not yet researched |
| Open-Meteo radar | Doesn't exist yet (open-meteo/open-meteo#1437) | — | — | — | — | ⏳ Watch; Breezy waits on it too |
| LibreWRX (self-hostable) | Depends on ingested feeds | Self-hosted stack | Self-host cost | FOSS (verify) | Self-hosted | ➖ What Breezy is studying; evaluate if AWS pipeline stalls |

## 2. What "good radar" needs (bar set by Windy / MyRadar / RainViewer app)
- Animated loop (past ~2 h) with play/pause + scrub, smooth frame interpolation.
- Smoothing toggle (RainViewer exposes `smooth` flag — keep it; users notice).
- Snow/rain distinction colors; custom color tables permitted by RainViewer.
- Coverage mask so no-data areas read as no-data, not clear-sky.
- Fast first frame: preload latest 2–3 frames, lazy-load the rest; cache tiles aggressively.
- Map base: MapLibre/Leaflet raster overlay; mobile GPU-friendly (z≤7 tiles are small).
- RainViewer app reference points: 100 m claimed display res, 2-h nowcast, minute-by-minute chart, rain-direction + totals (QPE) on paid tiers — good v2 checklist.

## 3. Recommended plan (updated 2026-10-09: personal Android, Met Office-direct, scrubbable timeline)
1. **Spike A — AWS HDF5 tiles**: download one 1 km UK composite, render PNG tiles, measure size + effort for a 15-min cron → tile endpoint. Verifies the past/now half of the timeline.
2. **Spike B — UKV 2 km precip as forecast half**: pull UK deterministic 2 km NetCDF from AWS, extract precipitation-rate steps, confirm timestep granularity, render in the same color ramp. Verifies the forecast half.
3. **Then — Android radar screen**: single timeline (see §5), MapLibre overlay, scrub + play. RainViewer demoted to fallback only (user wants Met Office-direct; also avoids commercial-terms issue entirely for personal use).
4. **Later**: NSWWS warnings overlay on radar (killer UK combo).

## 5. Timeline design: seamless past → now → forecast (all Met Office)
One frame array, one color ramp, per-frame kind flag:

- **Past + now (observed)**: AWS UK radar composite, 1 km, 15-min steps, ~20-min latency. Window −2 h → now ≈ 8 frames.
- **Forecast (model)**: UK deterministic 2 km precipitation-rate grids from AWS open data, +0 → +6 h. Rendered through the *same* rain-rate → color mapping so the nowcast boundary is invisible.
- **Player (manual scrub, no autoplay — decided 2026-10-09)**: drag scrub bar under the map; a "now" marker; crossfade across the obs/model boundary; per-frame badge (observed vs forecast) kept subtle — honesty without clutter.
- **Known mismatches to handle in code**: 1 km/15-min obs vs 2 km/coarser-step model → resample spatially, interpolate temporally between model steps; re-verify timestep granularity in Spike B.
- **Feeding the phone**: HDF5/NetCDF parsing on-device is heavy (native libs, multi-MB files, battery). For personal use, run a tiny home-side pipeline (dev PC / Pi / small VPS, 15-min cron: fetch → render tiles → serve). Phone fetches lightweight tiles + prefetches via WorkManager. Direct-S3-on-device stays a fallback, not the plan.

## 4. Open questions
- RainViewer commercial pricing/terms (contact sales when serious).
- OPERA as fallback — do only if AWS pipeline fails.
- Real-world UK coverage gaps (RainViewer coverage-mask endpoint answers this empirically).

## Sources
- https://www.rainviewer.com/api.html · https://www.rainviewer.com/api/weather-maps-api.html · examples: github.com/rainviewer/rainviewer-api-example · status: https://status.rainviewer.com
- https://registry.opendata.aws/met-office-uk-radar-observations
- https://catalogue.ceda.ac.uk/uuid/27dd6ffba67f667a18c62de5c3456350/ (NIMROD archive background)
- https://github.com/Jake-Pullen/met_office_radar_data (NIMROD .dat tooling, useful for spike)
