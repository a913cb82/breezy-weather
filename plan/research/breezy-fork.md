# Build on Breezy? — fork assessment (from source, 2026-10-09)

Reference clone: `/tmp/breezy` (depth-1, github.com/breezy-weather/breezy-weather).

## Verdict: yes, fork it — don't build from scratch
A from-scratch app rebuys theming, 16-day/hourly UI, charts, widgets, settings, i18n. Breezy gives all of that; our work shrinks to **(a) a Met Office source adapter** (documented path) + **(b) one radar card + detail screen** (new code, source-independent). Estimated shape: days, not months.

## Facts grounding this
- **License: LGPL-3.0** (`LICENSE`). Personal fork/modification is fine; keep notices intact. (Distribution would require source sharing — not our case.)
- **New source = copy-paste template**: `CONTRIBUTING.md` → copy `sources/pirateweather/`, implement JSON models (`@SerialName`, nullable fields) + service + converter. API keys via `breezy.<id>.key` in `local.properties` (never committed). Hourly forecast required only if we want it as a *main* source — DataHub spot/probabilistic qualifies.
- **New card = enum + holder**: `CardDisplay` enum (`CARD_NOWCAST`, `CARD_DAILY_FORECAST`, …) serialized as `&`-joined prefs; main screen renders `*ViewHolder`s (`PrecipitationNowcastViewHolder`…). Adding `CARD_RADAR` is structurally trivial.
- **No map SDK today**: `maps-utils` is just a namespace stub; no MapLibre/Mapbox/Google dependency. We add **MapLibre (BSD, keyless)** — consistent with the FOSS flavors (`src_freenet` / `src_nonfreenet` split exists; our code must live in the freenet-compatible side, i.e. no Google Maps).
- **Radar card does NOT need the source system**: like `CARD_CLOCK`, it can be source-independent — tiles come from our home pipeline keyed by lat/lon. No `SourceFeature` changes required.
- **Minimal-complexity card design** (fits Breezy's "blocks tap through to details"): card shows a **static latest-frame snapshot** (single PNG from our pipeline, cached) → tap opens a full radar detail screen with the scrubbable past→now→forecast timeline. Avoids embedding an interactive map in a scrolling list (lifecycle/perf pain).

## Work breakdown (personal fork)
1. Fork, build `freenet` flavor, sideload to Xiaomi. (One-time Gradle cost.)
2. `sources/metoffice/`: DataHub site-specific (+ blended for home) adapter; alerts via NSWWS if terms allow; else keep Open-Meteo as alerts secondary — the per-category secondary-source system already supports this mix.
3. Home tile pipeline (unchanged plan): AWS radar HDF5 + UKV precip → tiles/PNGs.
4. `CARD_RADAR` + snapshot card + radar detail screen (MapLibre + timeline player).
5. Keep fork rebased on upstream occasionally; don't aim for upstream merge (our Met Office-direct radar + private pipeline wouldn't meet their free-tier-for-all + radar-direction criteria anyway).

## Risks / gotchas
- Codebase onboarding: multi-module Gradle (app/data/domain/ui-weather-view/…), ViewHolder-based cards (not pure Compose) — read `MainAdapter` + one holder before coding.
- Map-in-app adds an NDK/binary dep (MapLibre) — fine for sideload, but first build will be slow.
- Upstream drift: rebase cost if we diverge far; keep our diff small and isolated (own package, own card).
