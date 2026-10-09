# Basemap + radar color scheme (2026-10-09)

## Basemap
- **Day: OpenFreeMap `positron`** (`tiles.openfreemap.org/styles/positron`) — quiet light-grey canvas, purpose-built as a background for overlaid data. Free public instance, no limits, no key, no registration. (RTR uses `liberty`; positron is quieter — better under radar. Same host, one-line swap.)
- **Night: custom darkened positron, hosted by us** — OpenFreeMap ships only light styles (liberty/bright/positron), but styles are plain JSON editable in Maputnik: fork positron, darken land/water/labels, host the JSON (tiles/fonts still OFM's). Wired to Breezy's location-based theme so the map follows the same sun logic as the rest of the app.
- **Fallback: CARTO `dark_matter`** — the classic dark radar canvas, free for non-commercial (5 M req/mo) but **requires an API key**, so it's plan B, not default.
- Radar sits above at adjustable opacity (RTR's `radarOpacity`); basemap labels dimmed so rain is the loudest thing on screen.

## Radar color ramp (shared obs + model — the seamless-timeline requirement)
One LUT in our tile pipeline, applied identically to AWS radar obs and UKV model precip, so the now→forecast boundary is invisible. Proposed default (tuned for dark basemap, sane on light):

| Rain rate (mm/h) | Color | Notes |
|---|---|---|
| < 0.1 | transparent | no-data ≠ dry handled by coverage mask |
| 0.1 – 0.5 | pale cyan `#A8E6F0`-ish | drizzle, barely-there |
| 0.5 – 1 | light blue | light rain |
| 1 – 2 | saturated blue | moderate |
| 2 – 4 | deep blue-violet | heavy |
| 4 – 8 | magenta-purple | very heavy |
| 8 – 16 | orange | intense / convective |
| 16+ | red-white core | extreme |

Principles: single-hue-progression (blue→purple→orange) reads as intensity without a legend; avoids red/green adjacency (most common colorblindness); snow/ice gets a separate pink/white treatment later (RainViewer-style `snow` flag equivalent).
Alternatives parked: (a) match Met Office app/website ramp for UK familiarity — compare against their legend in Spike A; (b) user-switchable schemes as a v2 setting (pipeline already owns the LUT, so this is cheap later).

## Open questions (for Spike A)
- Calibrate ramp stops against real AWS frames (what does 4 mm/h actually look like over the Pennines?).
- Confirm darkened-positron JSON renders cleanly in maplibre-compose.
- Snapshot PNG for the Breezy card uses the same LUT at card aspect ratio.
