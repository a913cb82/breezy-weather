# Weather App — Plan

> Status: `planned` — research in `research/`, scope in `REQUIREMENTS.md`, design in `ARCHITECTURE.md`, decisions in `DECISIONS.md`.

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
| 1. Fork + toolchain | Fork Breezy, build freenet flavor, sideload to Xiaomi | App runs on device |
| 2. Pipeline | 15-min cron → tiles + snapshot + manifest.json | 🔄 in progress (here: no SDK needed, pytest-verified) |
| 3. Met Office source | `sources/metoffice/` adapter, quota-safe polling | Forecast renders for saved locations |
| 4. Radar UI | `CARD_RADAR` snapshot card + detail map + scrub bar, day/night styles | Acceptance criteria in REQUIREMENTS.md pass |
| 5. Polish | Prefetch, offline cache, ramp tune vs Met Office legend | Feels native; snapshot fresh |

Phase 0 is done and the data side is fully proven. Start with Phase 1 (fork + toolchain).
