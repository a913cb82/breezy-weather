"""Run schedules + timeline builder (pure logic; S3 I/O lives in s3.py)."""
from datetime import datetime, timedelta, timezone

NOWCAST_HOURS = [1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23]
SHORT_HOURS = [0, 6, 9, 12, 18, 21]
MEDIUM_HOURS = [3, 15]

MODEL_BUCKET_PREFIX = "uk-deterministic-2km"


def _run_id(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H00Z")


def candidate_runs(now: datetime, hours: list, count: int = 30) -> list:
    """Scheduled run ids at or before `now`, newest first."""
    out, day = [], now.date()
    for back in range(3):  # today + 2 days back is plenty
        d = day - timedelta(days=back)
        for h in sorted(hours, reverse=True):
            dt = datetime(d.year, d.month, d.day, h, tzinfo=timezone.utc)
            if dt <= now:
                out.append(_run_id(dt))
                if len(out) >= count:
                    return out
    return out


def select_runs(now: datetime, hours: list, exists, count: int = 8) -> str:
    """Newest scheduled run for which `exists(run_id)` is true."""
    for run in candidate_runs(now, hours, count):
        if exists(run):
            return run
    raise LookupError(f"no published run in {hours}")


def _norm(ts: str) -> datetime:
    return datetime.strptime(ts.rstrip("Z"), "%Y%m%dT%H%M").replace(tzinfo=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_timeline(now, radar_valids, nowcast_run, nowcast_valids,
                   short_run, medium_run, base_url: str = "tiles") -> list:
    """Full frame list, oldest first. Model grid snaps to :00/:15/:30/:45."""
    nc = {_norm(v) for v in nowcast_valids}
    frames = []
    start_obs = now - timedelta(hours=6)
    for v in sorted(radar_valids):
        dt = _norm(v)
        if start_obs <= dt <= now:
            stamp = dt.strftime("%Y%m%dT%H%M")
            frames.append({"t": _iso(dt), "kind": "obs", "run": "-",
                           "tiles": f"{base_url}/obs/{stamp}/{{z}}/{{x}}/{{y}}.png"})
    grid0 = now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)
    seen = {f["t"] for f in frames}
    # +15min..+12h at 15-min (nowcast where published, else hourly short)
    for i in range(1, 49):
        dt = grid0 + timedelta(minutes=15 * i)
        if dt in nc:
            run, lead = nowcast_run, None
        elif dt.minute == 0:
            run, lead = short_run, None
        else:
            continue
        stamp = dt.strftime("%Y%m%dT%H%MZ")
        if _iso(dt) not in seen:
            seen.add(_iso(dt))
            frames.append({"t": _iso(dt), "kind": "model", "run": run,
                           "tiles": f"{base_url}/model/{stamp}/{{z}}/{{x}}/{{y}}.png"})
    # hourly +13..+54h, 3-hourly +57..+120h
    for h in range(13, 55):
        dt = grid0.replace(minute=0) + timedelta(hours=h)
        stamp = dt.strftime("%Y%m%dT%H%MZ")
        if _iso(dt) not in seen:
            seen.add(_iso(dt))
            frames.append({"t": _iso(dt), "kind": "model", "run": short_run,
                           "tiles": f"{base_url}/model/{stamp}/{{z}}/{{x}}/{{y}}.png"})
    base_h = grid0.replace(minute=0)
    for h in range(57, 121, 3):
        dt = base_h + timedelta(hours=h)
        stamp = dt.strftime("%Y%m%dT%H%MZ")
        if _iso(dt) not in seen:
            seen.add(_iso(dt))
            frames.append({"t": _iso(dt), "kind": "model", "run": medium_run,
                           "tiles": f"{base_url}/model/{stamp}/{{z}}/{{x}}/{{y}}.png"})
    frames.sort(key=lambda f: f["t"])
    return frames
