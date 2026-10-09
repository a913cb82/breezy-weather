# Met Office data — API research

## TL;DR
- **DataPoint is dead** (retired 1 Dec 2025, no like-for-like replacement).
- Successor is **Weather DataHub** (`datahub.metoffice.gov.uk`): API-key products, per-call pricing, generous-ish free tiers for dev but **not for a production consumer app without a caching proxy**.
- Sleeper hit: **Met Office open data on AWS** (incl. blended forecasts + UK radar HDF5, CC BY-SA) — best long-term bet for cost + radar.
- Warnings (NSWWS) has a DataHub API — pricing not yet checked (open question).

## 1. DataPoint (legacy) — DO NOT USE
Decommissioned; retirement FAQs confirm 1 Dec 2025 shutdown. No new registrations. Some FAQs point at DataHub alternatives per product, with parameter differences. Anything referencing DataPoint keys/endpoints is obsolete.

Sources: https://www.metoffice.gov.uk/services/data/datapoint · …/datapoint-retirement-faqs

## 2. Weather DataHub (current commercial route)
Flow: register → choose product → select data/order → subscribe → API credentials (under My Subscriptions). Contact: dpt@metoffice.gov.uk / enquiries@metoffice.gov.uk.

| Product | What you get | Free tier | Paid (ex-VAT) |
|---|---|---|---|
| Site-specific **Global spot** (hourly / 3-hourly / daily) | Point forecast, global | 360 calls/day | £9/mo @900/d → £32 @3.6k/d → £146 @18k/d → £250 @36k/d → £437 @72k/d |
| Site-specific **Blended probabilistic** (hourly, all params, 1 site) | UKMO-blended + IMPROVER calibration | 55 calls/day | £9/mo @550/d → £58 @4k/d → … |
| **Land observations** | UK station obs | 360 calls/day | same tiers as spot |
| **Map images** (beta) | PNG viz (temp, precip rate, cloud, MSLP), UK & Europe, ~10 km | 1000 images/day, currently free | fee-based later |
| **NSWWS warnings** | Severe weather warnings API | ? (TBD) | ? (TBD) |
| **Atmospheric** (gridded model data) | Model fields by region/order | 2 free entry plans | tiered |

Notes:
- Per-call pricing means **every user polling = money**. A shipped app needs a backend that fetches once and fans out (cache + push), otherwise costs scale linearly with users.
- Map Images is *model visualization*, **not radar** — no use for our P0.
- Blended probabilistic free tier (55/d, 1 site) is fine for a prototype, not for multi-location users.

Sources: https://datahub.metoffice.gov.uk/docs/getting-started · https://datahub.metoffice.gov.uk/pricing/site-specific · …/pricing/observations · …/pricing/map-images

## 3. Met Office open data on AWS (most promising)
Registry of Open Data on AWS, managed by the Met Office:
- **8× Blended Probabilistic Forecast products** (global + UK, gridded + spot, percentiles + probabilities).
- **UK Radar Observations — 2-year rolling archive** (see `radar-options.md`): 15-min UK composite rain-rate, HDF5, CC BY-SA.
- Pay only AWS egress/compute; data itself free. License CC BY-SA (share-alike — check app-store implications, likely fine with attribution).

Sources: https://registry.opendata.aws/?search=managedBy%3Amet%20office · https://registry.opendata.aws/met-office-uk-radar-observations

## 4. Licensing / attribution
- DataHub: bound by DataHub T&Cs on order confirm; enterprise/invoice tiers via Data Provisioning team.
- Open data: CC BY-SA — attribute Met Office, share adaptations alike.

## Verdict
- **Prototype forecast**: Open-Meteo (free, Breezy-compatible) + DataHub blended-probabilistic free tier to compare UK accuracy side by side.
- **Production UK data**: DataHub behind our own caching proxy, or AWS open-data grids if the latency/resolution checks out.
- **Radar**: AWS open-data HDF5, not DataHub (see radar note).
- **Still to check**: NSWWS warnings pricing/terms; DataHub rate-limit behavior; AWS open-data forecast latency.

## Personal-use free-quota check (1 user, Android, 2–3 locations) — 2026-10-09
**Fits comfortably. No paid tier needed.**

| Product | Free quota | Personal-use burn | Headroom |
|---|---|---|---|
| Site-specific global spot | 360 calls/day | 3 locs × hourly = 72/d (144/d at 30-min) | ~2.5–5× |
| Blended probabilistic (home site) | 55 calls/day, 1 site | hourly = 24/d | ~2× |
| Land observations | 360 calls/day | hourly = 24/d | 15× |
| Map images | 1000/day | barely needed | huge |
| AWS open data (UKV 2 km, radar, obs) | free data | phone-friendly only via tile/thin proxy (see radar note) | n/a |

Rules to stay free: poll hourly (not minutely); blended-probabilistic for home site only, spot for secondary locations; one API key, one device; cache aggressively (Room + HTTP cache). If locations/poll rate grow, re-check before DataHub overage bites — there is no hard stop, only paid tiers.

## Sources
- https://datahub.metoffice.gov.uk/ (pricing, docs, glossary, support)
- https://www.metoffice.gov.uk/services/data/datapoint/datapoint-retirement-faqs
- https://www.metoffice.gov.uk/services/data
