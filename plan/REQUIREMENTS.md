# Requirements (MVP — personal use, Xiaomi 15 Ultra)

## Scope: in
1. **Fork of Breezy Weather** (freenet flavor), sideloaded. All existing Breezy features keep working.
2. **Met Office source adapter** (`sources/metoffice/`): hourly + daily forecast for saved locations; home-site blended-probabilistic where quota allows, spot elsewhere. Stays inside free quotas (hourly polls, cache-first).
3. **Radar card**: new movable `CARD_RADAR` showing latest snapshot PNG; hidden gracefully when pipeline unreachable.
4. **Radar detail screen**: zoomable/scrollable MapLibre map (OFM positron day / darkened-positron night) + **manual scrub bar** over a unified timeline (Met Office-app parity: −6 h@15 m obs → +12 h@15 m / +54 h@60 m / +120 h@3 h model), one shared color ramp + **tap-for-value readout** (band mm/h via LUT inversion, frame time, obs/model badge).
5. **Tile pipeline** (home-side, 15-min cron): AWS radar HDF5 + UKV NetCDF → XYZ PNG tiles + snapshot + `manifest.json`.

## Scope: out (v2+)
Widgets changes, live wallpaper, upstream merge, user-switchable radar schemes, snow treatment, NSWWS overlay, multi-user/commercial use, inter-frame morphing (labeled interpolation), MOGREPS-UK ensembles (probabilistic rain chance), paid finer-than-open data (single-site radar, STEPS, commercial tiers).

## Acceptance criteria
- [ ] Fresh build installs alongside (or over) Breezy on the Xiaomi without key/Play dependencies.
- [ ] Met Office location shows hourly/daily data; 24 h of hourly polling stays under free quotas.
- [ ] Radar card renders a snapshot < 15 min old on Wi-Fi; tap opens the map.
- [ ] Scrubbing −6 h → +120 h (~110 variable-spaced frames) is smooth, boundary obs→model invisible, now-marker correct.
- [ ] Radar refreshes ≤15 min after new Met Office frames; map pans/zooms with overzoom past z7; no-data areas show as masked, not clear.
- [ ] Night use switches map + app to dark via location sun position.

## Resolved in Phase 0 spikes (see `research/spikes-phase0.md`)
- S3 layout known; radar 15-min cadence live, ~11-min latency; UKV 49 × 15-min steps to +12 h (no gap-filling needed).
- Shared LUT render-tested on both sources; NSWWS warnings free (20k/day).
