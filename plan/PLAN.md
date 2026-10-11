# Weather App — Plan

> Status: `active` — full build-out to shippable radar underway (2026-10-11). Research in `research/`, scope in `REQUIREMENTS.md`, design in `ARCHITECTURE.md`, decisions in `DECISIONS.md`.

## Vision
A Breezy Weather fork with UK-first Met Office data and a **best-in-class scrubbable weather radar** as the headline feature. Personal use, single Android device (Xiaomi 15 Ultra), inside Met Office free quotas.

## Non-negotiables
1. **Radar is P0** — smooth, manually scrubbable past→now→forecast, fast to first frame.
2. UK accuracy first (Met Office), sensible fallback elsewhere.
3. Breezy-native UI/UX — calm, Material 3 Expressive, no dashboard clutter.
4. Minimal complexity — fork, port, and reuse before inventing.

## Research tracks
| Track | File | Status |
|---|---|---|
| Breezy Weather UI/UX | `research/breezy-weather.md` | ✅ done |
| Met Office data APIs (+ personal free-quota check) | `research/metoffice-data.md` | ✅ done |
| Radar options → Met Office-direct timeline | `research/radar-options.md` | ✅ done |
| Fork assessment (from Breezy source) | `research/breezy-fork.md` | ✅ done |
| Radar code reuse (RoadTripRadar / Overmorrow) | `research/radar-reuse.md` | ✅ done |
| Basemap + radar color scheme | `research/basemap-and-colors.md` | ✅ done |

## Phases
| Phase | Work | Exit criteria |
|---|---|---|
| 0. Spikes | A: one AWS radar HDF5 → tiles (bucket layout, sizes, LUT calibration). B: UKV NetCDF precip steps (timestep granularity) | ✅ done 2026-10-09 — see `research/spikes-phase0.md` + `evidence/` |
| 1. Fork + toolchain | Fork Breezy, build freenet flavor, sideload to Xiaomi — ✅ build half done 2026-10-11 via personal CI (`personal-build.yml`, green run 38131819530, APK verified `org.breezyweather.debug` sdk37); device install/launch pending (needs adb + phone) | App runs on device |
| 2. Pipeline | 15-min cron → tiles + snapshot + manifest.json — ✅ code done, pytest 19/19, offline render verified (`origin/phase/2-pipeline`, 4 commits). Deploy gaps (2026-10-11): no cron unit, no tile hosting, no retention pruning, run probing fragile. FIXED 2026-10-11 (949d5e828, TDD now 22 tests): 404/DNS skips frame with warn, DONE frames kept in manifest, empty-obs → now_index -1. Live-validated: 97 frames (24 obs + 73 model), obs 10 min old, manifest + 768px snapshot + 14k tiles verified. Contract: manifest LUT is `[{min_mm_h,color}]`. ⚠️ merge deletes `personal-build.yml` — restore on merge — ✅ LIVE 2026-10-11: 15-min auto-deploy → Pages serves fresh manifest/snapshot/tiles, phone-ready. Remaining: run-probe hardening only | Live cycle + hosted manifest |
| 3. Met Office source | `sources/metoffice/` adapter, quota-safe polling — mapped 2026-10-11: template = `brightsky/` (`HttpSource`+`WeatherSource`), register in `SourceManager` national list, key via `breezy.metoffice.key`→`BuildConfig`; stub + nonfreenet impl exist — ✅ code done 2026-10-11 (merged): freenet port of DataHub impl, standalone class (stub's NonFreeNetSource is filtered from freenet), CI compile green. Runtime needs DataHub key — NOT yet available | Forecast renders for saved locations |
| 4. Radar UI | `CARD_RADAR` snapshot card + detail map + scrub bar, day/night styles — ✅ card half done 2026-10-11 (merged): enum + ViewType.RADAR + holder (OkHttp snapshot, freshness, UK-gated, graceful offline), manifest data layer, no new deps, CI green. TODO: maplibre dep + detail map + scrub + tap + LUT inversion readout | Acceptance criteria in REQUIREMENTS.md pass |
| 5. Polish | Prefetch, offline cache, ramp tune vs Met Office legend | Feels native; snapshot fresh |

Phases 0–2 code done; build-out order: finish Phase 1 device check → deploy Phase 2 live (cron + hosting + robustness) → write Phase 3 → Phase 4 → Phase 5.
