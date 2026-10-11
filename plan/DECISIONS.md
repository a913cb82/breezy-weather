# Decisions

Append-only log. Newest at bottom.

| Date | Decision | Rationale | Status |
|---|---|---|---|
| 2026-10-09 | Radar is P0 feature; prototype it first | User priority; highest technical risk | accepted |
| 2026-10-09 | Track research in `research/*.md` | Keep sources + verdicts reviewable | accepted |
| 2026-10-09 | Radar: prototype RainViewer, spike Met Office AWS-HDF5 pipeline | Zero-backend first frame vs license-clean UK-native long term | superseded (Met Office-direct accepted; RainViewer fallback only) |
| 2026-10-09 | Forecast: prototype Open-Meteo + DataHub blended free tier side-by-side | Compare UK accuracy before committing to paid DataHub | proposed |
| 2026-10-09 | Personal Android (Xiaomi 15 Ultra), stay in Met Office free quota | Single user fits: worst case ~144/360 spot calls/day, 24/55 blended/day | accepted |
| 2026-10-09 | Radar Met Office-direct: AWS 1 km obs (past/now) + UKV 2 km precip (forecast), one scrubbable timeline | Seamless past→now→forecast, all Met Office, license-clean | accepted |
| 2026-10-09 | Stack: Kotlin + Compose + M3 Expressive, MapLibre, home-side tile pipeline, sideload | Mirrors Breezy; avoids HDF5-on-device; no Play Store needed | superseded |
| 2026-10-09 | Fork Breezy (LGPL-3.0): add metoffice source + source-independent CARD_RADAR (static snapshot → detail timeline) | Verified in source: template source path, enum cards, no map SDK; MapLibre fits freenet flavor | accepted |
| 2026-10-09 | Radar stack: maplibre-compose + OpenFreeMap basemap + RTR opacity-frame pattern, MIT-ported; Overmorrow UX ref only | RTR native Kotlin/MIT ports 1:1; Overmorrow is Flutter (ideas only) | accepted |
| 2026-10-09 | Radar timeline is manual scrub bar under map; no autoplay/animation | User preference: direct time control beats passive playback | accepted |
| 2026-10-09 | Basemap: OFM positron (day) + self-hosted darkened positron (night); radar: shared blue→purple→orange LUT | Keyless, FOSS-safe; one ramp for obs+model keeps timeline seamless | accepted |
| 2026-10-09 | Plan structure: REQUIREMENTS + ARCHITECTURE + phased plan; Phase 0 spikes first | Research done; spikes answer bucket/UKV unknowns before building | accepted |
| 2026-10-09 | Phase 0 done: buckets/paths known, radar 15-min/~11-min latency, UKV 49×15-min steps, LUT render-tested, NSWWS free | Live-probed S3 + rendered both sources; no gap-filling needed; ~25 MB/cycle pipeline fetch | accepted |
| 2026-10-09 | Radar ops: 15-min pipeline cron, quota-free AWS fetch, 32-frame −2 h/+6 h window, z0–7 tiles + overzoom, uniform 15-min steps in-window | All numbers from Phase 0 evidence; +6 h is UX choice, +12 h available free | superseded |
| 2026-10-09 | Timeline matches Met Office app: −6 h@15 m obs, +12 h@15 m / +54 h@60 m / +120 h@3 h model; windowed layer loading | Parity with reference app; ~110 frames forces sliding-window layers, not keep-all; no interpolation (manual scrub) | accepted |
| 2026-10-09 | Free-data ceiling confirmed: 1 km/15-min radar + 2 km UKV is the max open data; tap-for-value in MVP, morphing/ensembles/paid data to v2 | Searched finer options — all commercial; software-side precision (mm/h readout) needs no new data | accepted |
| 2026-10-09 | Builds happen on separate PC (this one is bandwidth-limited); plan + BUILD.md published to fork | No JDK/SDK downloads here; fork carries plan/ subtree + build instructions | accepted |
| 2026-10-09 | Pipeline implemented TDD (19 pytest) on branch phase/2-pipeline; offline end-to-end render verified | No-SDK work done here; probe-storm + timeouts hardened for flaky links; push when network returns | accepted |
| 2026-10-11 | Manifest LUT contract = [{min_mm_h,color}] (code wins over ARCH max_mm_h); app band lookup = highest stop whose color matches | Inversion needs lower bounds; one-line doc fix, no pipeline change | accepted |
| 2026-10-11 | Full build-out mission: finish P1 device → deploy P2 live (cron+hosting+robustness) → write P3 adapter → P4 CARD_RADAR UI → P5 polish; plan/*.md are the tracker; merge of phase/2-pipeline must restore personal-build.yml | Integration points mapped (brightsky template, SourceManager, CardDisplay/MainAdapter, no map SDK yet); Kotlin verified via CI, this PC can't dex (3.7 GB RAM) | accepted |
| 2026-10-11 | Live pipeline proved the 404-abort gap: DNS drop + 4 unpublished far-field frames killed the cycle with no manifest; fixed TDD (skip-with-warn, DONE kept, empty-obs safe), live re-run green | 97 frames, now obs 10 min old, manifest/snapshot/14k tiles verified; remaining deploy gaps: cron, hosting, retention, run probing | accepted |
| 2026-10-11 | Tiles auto-deploy live: tiles-deploy.yml (15-min cron + manual) renders on runners, prunes >12 h frames, force-orphan push to gh-pages:/tiles; workflow write-permission granted via API; Pages enabled | Phone fetches manifest.json + snapshot + tiles with zero local infra | accepted |
| 2026-10-11 | Phase 3 freenet adapter = port of nonfreenet DataHub service (468 lines, same endpoints shapes); must not extend the stub (NonFreeNetSource filtered from freenet by SourceManager:482); key plumbing already flavor-agnostic | Compiles green in CI; lights up on saved locations once DataHub key exists | accepted |
| 2026-10-11 | PC-side visual QA of live tiles (evidence/live-qa-2026-10-11/): LUT colors exact in tiles, XYZ north-up confirmed in code, warp 7/8 wet probes exact (1 off-by-one band at tile edge = resampling, inherent), dry-skip + transparency correct, mask footprint matches UK bbox ~1px | Tap-inversion safe; source spikes to 364 mm/h noted → despeckle is Phase 5 polish; no Gradle/emulator used (PC RAM) | accepted |
| 2026-10-11 | No local APK builds on this PC: 3.7 GB WSL RAM thrashes at mergeExtDex; Gradle capped via ~/.gradle/gradle.properties (Xmx2g, 2 workers) as damage control | Daemon Xmx4g exceeded total RAM; caps stop freezes but can't fit a full build; heavy compile stays in cloud/CI | accepted |
| 2026-10-11 | Personal CI builds: .github/workflows/personal-build.yml (manual dispatch, assembleFreenetDebug, no -Pbreezy, APK artifact 14 d); SDK pkg is platforms;android-37.0, sdkmanager via full $ANDROID_HOME path | Public fork = unlimited free Linux minutes (16 GB runners); upstream push.yml uploads nothing on forks; first green run 38131819530, APK verified org.breezyweather.debug sdk37 | accepted |
