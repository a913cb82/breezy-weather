# Radar reuse: RoadTripRadar + Overmorrow (from source, 2026-10-09)

Clones: `/tmp/rtr` (digiexchris/RoadTripRadar, MIT), `/tmp/over` (bmaroti9/Overmorrow, GPL-3.0).

## Verdict
- **RoadTripRadar = code donor.** Native Kotlin + Compose, MIT (compatible with our LGPL fork; keep its copyright notices). Its radar stack ports almost 1:1.
- **Overmorrow = UX reference only.** Flutter/Dart — nothing portable to Breezy, but it validates our card→detail shape (`RadarSmall` preview + full `radar_page`) and frame-timer UX.

## Take from RoadTripRadar (concrete files)
| File | What it gives us |
|---|---|
| `gradle/libs.versions.toml` → `org.maplibre.compose:maplibre-compose:0.12.1` (+ `material3`) | **Compose-native maps** — no AndroidView interop in Breezy cards/screens |
| `data/RainViewer.kt` (22 lines) | Tile-URL-template pattern: `…/{path}/512/{z}/{x}/{y}/2/1_1.png`, `MAX_ZOOM=7` with SDK overzoom. Our pipeline serves the same XYZ shape → same pattern, our host/paths |
| `ui/MapLayers.kt` → `WeatherRadarLayers` | **Frame animation by opacity**: one RasterSource+RasterLayer per frame, active frame gets `radarOpacity`, rest `0f`. Proven in production; fits our obs+model frame list directly |
| `model/Models.kt` + `CustomThemeHelpers.kt` | Keyless **OpenFreeMap** basemap (`tiles.openfreemap.org/styles/liberty`) — FOSS-flavor-safe, no API key |
| `ui/WeatherTimeline.kt` (143 lines) | Tick-strip timeline component — restyle to M3/Breezy and **make it scrubbable** (theirs reads display-only) |

Animation driver: ViewModel-owned `currentFrameIndex` playhead consumed by both map layers and timeline (also reused for their car surface — we only need phone).

## Take from Overmorrow (ideas, not code)
- `RadarSmall` (embedded live mini-preview) vs our static-PNG snapshot: theirs proves live-in-card works, but static PNG stays the minimal-complexity choice — revisit only if the snapshot feels dead.
- 1 s frame-advance timer with optional haptics; ~12-frame lists from `decode_RV.dart` (67-line frame-URL builder — the same "fetch manifest → frame paths" shape our pipeline manifest will use).

## What stays custom (Met Office-direct core)
1. **Frame manifest**: our pipeline's JSON (obs frames −2 h + UKV model frames +6 h, per-frame kind flag) replaces the RainViewer manifest fetch.
2. **Timeline player**: manual scrub bar (+ now-marker + obs/forecast badge, no autoplay) — new, Breezy-M3-styled.
3. **Breezy-native integration**: `CARD_RADAR` holder + detail screen using Breezy `ThemeManager` colors; day/night basemap style switch wired to Breezy's location-based theme; snapshot PNG sized to Breezy card metrics.
4. Perf check: RTR keeps all frame sources alive (~12). Ours is ~20 (8 obs + 12 model) — start with their pattern, fall back to single-source URL-swap + neighbor precache if memory/bitmaps complain on the Xiaomi.

## License notes
- RTR MIT → fine inside LGPL-3.0 fork; retain `Copyright (c) digiexchris` headers on ported files.
- Overmorrow GPL-3.0 → also compatible, but we port no code, only ideas.
