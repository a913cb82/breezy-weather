# Build PC setup (builds happen here, not on the limited-bandwidth dev PC)

Source of truth for the plan lives in `plan/` (this is a copy; edit `../PLAN.md` etc. on the dev PC... actually: this repo IS the fork — `plan/` is maintained here once editing moves to this PC).

## Requirements
- JDK 17+ (AGP 9.4.0 + Gradle 9.7.1; JDK 17 minimum, 21 also fine)
- Android SDK: `platforms;android-37` + `build-tools;37.0.0` (+ platform-tools for adb)
- `local.properties` (optional — build works without keys, sources needing keys just stay empty):
  ```
  breezy.<sourceid>.key=<key>
  ```
  e.g. `breezy.metoffice.key` once the DataHub key exists. Never commit this file.

## Validate (Phase 1 exit criteria)
```
./gradlew assembleFreenetDebug
adb install -r app/build/outputs/apk/freenet/debug/*.apk
```
Pass = app launches on the Xiaomi. No keys, no Play, no Google services needed for freenet flavor.

## Upstream sync (keeps our diff small and rebases cheap)
```
git fetch upstream
git merge upstream/main   # personal fork: merge, don't rebase
```
Our work lives in: `plan/`, `app/src/.../sources/metoffice/`, radar card + detail screen, `maplibre-compose` dep. Everything else stays upstream-identical.

## Branch strategy
- `main` = ours (plan + features merged in).
- `phase/<n>-<topic>` branches for each PLAN phase, merged to main when exit criteria pass.
