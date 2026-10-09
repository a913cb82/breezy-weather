# START HERE (agent handoff)

This fork adds a Met Office-direct weather radar to Breezy Weather (personal use, one Android phone). You are on branch `phase/2-pipeline` unless noted otherwise.

## Where we are (2026-10-09)
- ✅ Phase 0 (spikes): `plan/research/spikes-phase0.md` + `plan/research/evidence/` — live S3 probes, renders.
- ✅ Phase 2 (pipeline): `pipeline/` implemented TDD (19 pytest), offline end-to-end verified. **NOT yet pushed** (PC was offline) — push first when network returns.
- ⏳ Phase 1 (fork build): must happen on the build PC — `./gradlew assembleFreenetDebug` (`plan/BUILD.md`). Never attempted here (no JDK/SDK on this PC by choice).
- ⏳ Phase 3 (Met Office source), Phase 4 (radar UI): Kotlin, unwritten. Writable here but **not compilable here** — flag everything for build-PC verification.

## Branch map
- `main` = upstream + `plan/` docs only (pushed to `a913cb82/breezy-weather`).
- `phase/2-pipeline` = main + `pipeline/` + plan updates (2 commits ahead of main, unpushed at handoff).
- Upstream: `upstream/main` (breezy-weather). Sync with fetch + merge, never rebase our work away.

## Read in this order
1. `plan/PLAN.md` — phases + exit criteria (source of truth for status).
2. `plan/REQUIREMENTS.md` — MVP scope + acceptance checkboxes.
3. `plan/ARCHITECTURE.md` — data flow, `manifest.json` contract, locked trade-offs.
4. `plan/DECISIONS.md` — append-only log (newest last). **Append, don't rewrite.**
5. `plan/research/` — background; `spikes-phase0.md` is the most load-bearing.

## Next steps (in order)
1. Push `phase/2-pipeline` (and confirm `main` is in sync with GitHub).
2. Build PC: validate freenet APK (Phase 1 exit criteria in `plan/BUILD.md`).
3. Connected PC: one full live pipeline cycle (`pipeline/README.md`), check wall-time < 15 min.
4. Write the Kotlin (Phase 3 source adapter → Phase 4 `CARD_RADAR`); compile + test on build PC.
5. Keep `plan/` (here) and `weather/*.md` (dev PC mirror) in sync — they drifted once already; `diff -q` before every commit.

## Constraints of a no-SDK PC (and how to recreate this one's setup)
- No JDK/Android SDK, no big downloads (bandwidth-limited, intermittently offline).
- TDD per project rules: tests first (`pipeline/tests/`), run with `PYTHONPATH=pipeline/src python -m pytest pipeline/tests/`.
- Recreate the Python env anywhere (small downloads only):
  `python3 -m venv /tmp/wx && /tmp/wx/bin/pip install -r pipeline/requirements.txt`
- Re-fetch the exact test fixtures (or set `WX_RADAR_FIXTURE` / `WX_UKV_FIXTURE` to any same-format files):
  `curl -o /tmp/radar.h5 https://met-office-radar-obs-data.s3.eu-west-2.amazonaws.com/radar/2026/10/09/202610091745_ODIM_ng_radar_rainrate_composite_1km_UK.h5`
  `curl -o /tmp/precip.nc https://met-office-atmospheric-model-data.s3.eu-west-2.amazonaws.com/uk-deterministic-2km/20261009T1400Z/20261009T1745Z-PT0003H45M-precipitation_rate.nc`
- Reference clones used during research (only re-clone if you must re-check something; findings are in `plan/research/`):
  `github.com/breezy-weather/breezy-weather`, `github.com/digiexchris/RoadTripRadar`, `github.com/bmaroti9/Overmorrow`
