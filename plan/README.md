# START HERE (agent handoff)

This fork adds a Met Office-direct weather radar to Breezy Weather (personal use, one Android phone). You are on branch `phase/2-pipeline` unless noted otherwise.

## Where we are (2026-10-11)
- ✅ Phase 0 (spikes): `plan/research/spikes-phase0.md` + `plan/research/evidence/` — live S3 probes, renders.
- ✅ Phase 2 (pipeline) code: on `origin/phase/2-pipeline` (4 commits, 19 pytest), offline end-to-end verified. Deploy gaps tracked in `plan/PLAN.md` (cron, hosting, retention, 404/crash robustness). ⚠️ merging it deletes `.github/workflows/personal-build.yml` — restore on merge.
- ✅ Phase 1 build half: green CI via `.github/workflows/personal-build.yml` (free public-repo runners, APK artifact verified). Device install/launch pending (needs adb + phone).
- 🗺️ Phase 3/4 integration mapped (brightsky template, `SourceManager`, `CardDisplay`/`MainAdapter`, no map SDK yet). Kotlin unwritten; all Kotlin verified via CI — this PC can't dex (3.7 GB RAM).
- Mission: full build-out to shippable radar, tracked in `plan/PLAN.md` + `REQUIREMENTS.md` checkboxes + `DECISIONS.md` (append-only).

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
1. Device: adb bridge + install + launch check (Phase 1 exit; needs phone plugged in + `usbipd`).
2. Pipeline live: one full live cycle to a scratch dir (wall-time < 15 min), then cron + tile hosting + retention + robustness fixes (Phase 2 deploy gaps in `plan/PLAN.md`).
3. Kotlin via CI: Phase 3 adapter → Phase 4 `CARD_RADAR`, each step green in `personal-build` before merging.
4. Tick `plan/REQUIREMENTS.md` checkboxes as acceptance criteria pass; append to `plan/DECISIONS.md`, never rewrite.
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
