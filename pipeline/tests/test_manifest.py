"""Manifest tests: schema keys + JSON-stability (TDD)."""
import json

from wx_tiles.manifest import build_manifest


def _frames():
    return [
        {"t": "2026-10-09T17:45:00Z", "kind": "obs", "run": "-",
         "tiles": "https://x/obs/202610091745/{z}/{x}/{y}.png"},
        {"t": "2026-10-09T18:00:00Z", "kind": "model", "run": "20261009T1400Z",
         "tiles": "https://x/model/202610091800/{z}/{x}/{y}.png"},
    ]


def test_manifest_schema():
    m = build_manifest(_frames(), now_index=1, base_url="https://x",
                       snapshot="https://x/snapshot.png", coverage="https://x/mask.png")
    assert set(m) == {"generated", "now_index", "lut", "frames", "snapshot", "coverage"}
    assert m["now_index"] == 1
    assert len(m["frames"]) == 2
    assert all(set(f) == {"t", "kind", "run", "tiles"} for f in m["frames"])
    assert m["lut"][0]["min_mm_h"] == 0.1
    json.dumps(m)  # must serialize


def test_manifest_frame_order_preserved():
    frames = _frames()[::-1]
    m = build_manifest(frames, now_index=0, base_url="https://x",
                       snapshot="s", coverage="c")
    assert [f["t"] for f in m["frames"]] == [f["t"] for f in frames]
