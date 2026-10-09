# Breezy Weather — UI/UX research

Source repo: https://github.com/breezy-weather/breezy-weather (free & open source, no proprietary blobs, F-Droid + GitHub releases)
Tech: **Kotlin + Jetpack Compose + Material 3 Expressive** (Android-native).
Docs read: `README.md`, `docs/HOMEPAGE.md` (raw GitHub); feature list via web search.

## What it is
Feature-rich Material-You weather app, fork lineage from Geometric Weather. Privacy-friendly (no trackers, location optional, IP-location option), accessibility-conscious, fully usable with Open-Meteo as the FOSS source. Supports **50+ weather sources** behind one abstraction.

Data coverage: 16-day daily + hourly, minute-by-minute nowcasting, severe + precipitation alerts, temp/feels-like/normals, precip, wind, AQ, pollen & mold, humidity, UV, visibility, pressure, sun, moon.

## Main-screen anatomy (steal this structure)
1. **App bar** — location-list back button + city name left; "open in another app" + per-location Edit right. Last-refresh timestamp below.
2. **Header** — condition description, big temperature that **animates from the previous value** (1–2s, disableable), feels-like if different, half-day min/max line. Day split at **06:00** (day 06:00–17:59, night 18:00–05:59).
3. **Blocks** (user-reorderable, 1–5 per row by width): Alerts (pinned top, always visible) → nowcasting → daily → hourly → precipitation → wind → AQ → pollen → humidity → UV → visibility → pressure → sun → moon → clock (opt-in). **Every block taps through to details.** Blocks hide gracefully when the source lacks data.
4. **24-hour detail charts** per block — the signature "well-thought-out visualizations" bit.

## Theme system (the part that makes it feel alive)
- **Location-based dark mode**: theme follows sun position *at the viewed location*, not the device. Options: follow day/night, or always-dark-when-app-dark (accessibility default).
- **Weather-reactive animated background** (sun, clouds…) with toggles for animation and a tilt/gravity-sensor parallax. Fallback to static white/black.
- Automatic dark mode + full unit/numeral-system/calendar localization.

## Multi-source architecture (most important structural idea)
- One **main source** for core forecast + **secondary sources per category** (AQ, allergens, minutely precip, alerts), each with source-specific prefs. Documented comparison in `docs/SOURCES.md`.
- Contribution guide includes "how to add a new weather source" → sources are pluggable adapters. **We should copy this pattern** (Met Office adapter, Open-Meteo adapter, etc.).

## Radar status (validates our P0)
Breezy has **no radar today**. Maintainers are studying feasibility with self-hostable **LibreWRX** (https://librewxr.net/) and a **future Open-Meteo radar** (open-meteo/open-meteo#1437). → Radar is genuinely hard in FOSS; nailing it is a real differentiator.

## Top patterns to steal
1. Header with animated temperature + half-day min/max.
2. Reorderable tappable blocks with per-block detail pages + 24h charts.
3. Location-based (sun-driven) theming with accessibility override.
4. Per-category pluggable sources (don't hard-code one provider).
5. Nowcasting strip directly under alerts.
6. Widgets + live wallpaper as v2 retention (large widget selection is a loved feature).
7. Privacy posture as a feature (no trackers, optional location).

## Open questions
- Exact license of current tree (fork metadata says LGPL-3.0 — verify before reusing code).
- Chart library used for 24h charts (check repo when we pick stack).
- Widget overhaul (#937) is stalled — don't copy widget code blindly.

## Sources
- https://github.com/breezy-weather/breezy-weather
- https://raw.githubusercontent.com/breezy-weather/breezy-weather/main/README.md
- https://raw.githubusercontent.com/breezy-weather/breezy-weather/main/docs/HOMEPAGE.md
- https://raw.githubusercontent.com/breezy-weather/breezy-weather/main/docs/SOURCES.md (full source list)
- https://librewxr.net/ · https://github.com/open-meteo/open-meteo/issues/1437
