"""Cycle runner: timeline -> fetch -> tiles -> snapshot/mask -> manifest.json."""
import argparse
import io
import json
import os
import urllib.error
from datetime import datetime, timedelta, timezone

from wx_tiles import grid, lut, manifest as manifest_mod
from wx_tiles.runs import MEDIUM_HOURS, NOWCAST_HOURS, SHORT_HOURS, build_timeline, select_runs
from wx_tiles.s3 import exists, fetch, list_prefix

RADAR_BUCKET = "met-office-radar-obs-data"
MODEL_BUCKET = "met-office-atmospheric-model-data"
RADAR_PREFIX = "radar"
MODEL_PREFIX = "uk-deterministic-2km"


def _https(bucket: str, key: str) -> str:
    return f"https://{bucket}.s3.eu-west-2.amazonaws.com/{key}"


def radar_key(dt) -> str:
    stamp = dt.strftime("%Y%m%dT%H%M").replace("T", "")
    d = dt.strftime("%Y/%m/%d")
    return f"{RADAR_PREFIX}/{d}/{stamp}_ODIM_ng_radar_rainrate_composite_1km_UK.h5"


def model_key(run: str, validity: str, param: str = "precipitation_rate") -> str:
    run_dt = datetime.strptime(run, "%Y%m%dT%H00Z").replace(tzinfo=timezone.utc)
    val_dt = datetime.strptime(validity, "%Y%m%dT%H%MZ").replace(tzinfo=timezone.utc)
    secs = int((val_dt - run_dt).total_seconds())
    lead = f"PT{secs // 3600:04d}H{(secs % 3600) // 60:02d}M"
    return f"{MODEL_PREFIX}/{run}/{validity}-{lead}-{param}.nc"


def latest_run(now, hours, param="precipitation_rate") -> str:
    def probe(run: str) -> bool:
        validity = run  # every run folder holds its own T+0 step
        return exists(_https(MODEL_BUCKET, f"{MODEL_PREFIX}/{run}/{validity}-PT0000H00M-{param}.nc"))
    return select_runs(now, hours, probe)


def radar_valids(now, hours_back=6):
    """Trailing 15-min radar validities via one day-prefix listing."""
    out = []
    for back in (0, 1):
        day = (now - timedelta(days=back)).strftime("%Y/%m/%d")
        keys, _, _, _ = list_prefix(RADAR_BUCKET, f"{RADAR_PREFIX}/{day}/", max_keys=100)
        for k, _ in keys:
            stamp = k.split("/")[-1][:12]  # YYYYMMDDHHMM (no T in radar names)
            dt = datetime.strptime(stamp, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
            if now - timedelta(hours=hours_back) <= dt <= now:
                out.append(dt.strftime("%Y%m%dT%H%M"))
    return sorted(set(out))


def run_cycle(out_dir: str, base_url: str, now=None, zmin=0, zmax=7,
              tile_size=256, param="precipitation_rate", max_new_frames=None) -> dict:
    now = now or datetime.now(timezone.utc)
    print("now:", now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    nc_run = latest_run(now, NOWCAST_HOURS, param)
    short_run = latest_run(now, SHORT_HOURS, param)
    med_run = latest_run(now, MEDIUM_HOURS, param)
    print("runs:", nc_run, short_run, med_run)
    # nowcast validities actually published in that run folder
    nc_valids = set()
    token = None
    while True:
        keys, _, token, trunc = list_prefix(
            MODEL_BUCKET, f"{MODEL_PREFIX}/{nc_run}/", max_keys=1000, token=token)
        for k, _ in keys:
            leaf = k.split("/")[-1]
            if leaf.endswith(f"-{param}.nc"):
                nc_valids.add(leaf.split("-")[0] + "Z")
        if not trunc:
            break
    frames = build_timeline(now, radar_valids(now), nc_run, nc_valids,
                            short_run, med_run, base_url=base_url)
    print(f"{len(frames)} frames")
    os.makedirs(out_dir, exist_ok=True)
    rendered = []
    rendered_frames = []
    latest_obs = None

    def _write_snapshot_and_mask(g):
        snap = grid.render_snapshot(g["data"], g["proj"], g["extent"],
                                    (-11.0, 49.5, 3.5, 59.5))
        with open(os.path.join(out_dir, "snapshot.png"), "wb") as fh:
            fh.write(snap)
        def msink(idx, png):
            z, x, y = idx
            p = os.path.join(out_dir, "mask", str(z), str(x))
            os.makedirs(p, exist_ok=True)
            with open(os.path.join(p, f"{y}.png"), "wb") as fh:
                fh.write(png)
        grid.render_tiles(g["data"], g["proj"], g["extent"], 0, 5,
                          tile_size=tile_size, sink=msink, colorize=grid.mask_colorize)
    new_count = 0
    for f in frames:
        if max_new_frames is not None and new_count >= max_new_frames:
            rendered.append((f["t"], -2))
            continue
        if f["kind"] == "obs":
            dt = datetime.strptime(f["t"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            sub = "obs/" + dt.strftime("%Y%m%dT%H%M")
        else:
            sub = "model/" + f["t"][:16].replace("-", "").replace(":", "") + "Z"
        if os.path.exists(os.path.join(out_dir, sub, "DONE")):
            rendered.append((f["t"], -1))
            rendered_frames.append(f)  # tiles already on disk: keep in manifest
            continue
        try:
            if f["kind"] == "obs":
                blob = fetch(_https(RADAR_BUCKET, radar_key(dt)))
                g = grid.parse_radar(blob)
            else:
                blob = fetch(_https(MODEL_BUCKET, model_key(f["run"], f["t"][:16].replace("-", "").replace(":", "") + "Z")))
                g = grid.parse_ukv(blob)
        except urllib.error.URLError as e:
            # Frame not (yet) published or network down: skip it, keep the
            # cycle alive so manifest.json still reflects rendered frames.
            print(f"warn: skip {f['t']} ({e})")
            rendered.append((f["t"], -3))
            continue
        def sink(idx, png, _sub=sub):
            z, x, y = idx
            p = os.path.join(out_dir, _sub, str(z), str(x))
            os.makedirs(p, exist_ok=True)
            with open(os.path.join(p, f"{y}.png"), "wb") as fh:
                fh.write(png)
        tiles = grid.render_tiles(g["data"], g["proj"], g["extent"], zmin, zmax,
                                  tile_size=tile_size, sink=sink)
        with open(os.path.join(out_dir, sub, "DONE"), "w") as fh:
            fh.write(f["t"])
        new_count += 1
        rendered.append((f["t"], len(tiles)))
        rendered_frames.append(f)
        if f["kind"] == "obs":
            latest_obs = g
    if latest_obs is not None:
        _write_snapshot_and_mask(latest_obs)
    obs_idx = [i for i, f in enumerate(rendered_frames) if f["kind"] == "obs"]
    now_index = max(obs_idx) if obs_idx else -1
    m = manifest_mod.build_manifest(rendered_frames, now_index, base_url,
                                    snapshot=base_url + "/snapshot.png",
                                    coverage=base_url + "/mask/{z}/{x}/{y}.png")
    with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
        json.dump(m, fh, indent=1)
    print("frames rendered:", len(rendered), "now_index:", now_index)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--zmin", type=int, default=0)
    ap.add_argument("--zmax", type=int, default=7)
    ap.add_argument("--tile-size", type=int, default=256)
    ap.add_argument("--max-new-frames", type=int, default=None)
    args = ap.parse_args()
    run_cycle(args.out, args.base_url.rstrip("/"), zmin=args.zmin, zmax=args.zmax,
              tile_size=args.tile_size, max_new_frames=args.max_new_frames)


if __name__ == "__main__":
    main()
