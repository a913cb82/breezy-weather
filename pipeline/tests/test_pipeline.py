"""Pipeline robustness tests: unfetchable frames must not abort the cycle (TDD)."""
import urllib.error

import wx_tiles.pipeline as P
from wx_tiles import grid


def _frames():
    return [
        {"t": "2026-10-09T17:45:00Z", "kind": "obs", "run": "-",
         "tiles": "https://x/obs/202610091745/{z}/{x}/{y}.png"},
        {"t": "2026-10-09T18:00:00Z", "kind": "model", "run": "20261009T1400Z",
         "tiles": "https://x/model/202610091800/{z}/{x}/{y}.png"},
    ]


def _404(url, **kw):
    raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)


def _fake_grid(monkeypatch):
    monkeypatch.setattr(grid, "parse_radar",
                        lambda blob: {"data": None, "proj": None, "extent": None})
    monkeypatch.setattr(grid, "parse_ukv",
                        lambda blob: {"data": None, "proj": None, "extent": None})
    def fake_tiles(*a, **k):
        sink = k.get("sink")
        if sink is not None:
            sink((0, 0, 0), b"tile")  # real impl sinks ≥1 tile, creating dirs
        return [(0, 0, 0)]
    monkeypatch.setattr(grid, "render_tiles", fake_tiles)
    monkeypatch.setattr(grid, "render_snapshot", lambda *a, **k: b"png")


def test_run_cycle_skips_unfetchable_frames(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "build_timeline", lambda *a, **k: _frames())
    monkeypatch.setattr(P, "latest_run", lambda *a, **k: "20261009T1400Z")
    monkeypatch.setattr(P, "radar_valids", lambda *a, **k: ["20261009T1745"])
    monkeypatch.setattr(P, "list_prefix", lambda *a, **k: ([], None, None, False))

    def fetch(url):
        if "/radar/" in url:
            return b"fake-h5"
        return _404(url)
    monkeypatch.setattr(P, "fetch", fetch)
    _fake_grid(monkeypatch)

    m = P.run_cycle(str(tmp_path), "https://x")
    assert [f["t"] for f in m["frames"]] == ["2026-10-09T17:45:00Z"]
    assert m["now_index"] == 0
    assert (tmp_path / "manifest.json").exists()


def test_run_cycle_keeps_done_frames_in_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "build_timeline", lambda *a, **k: _frames())
    monkeypatch.setattr(P, "latest_run", lambda *a, **k: "20261009T1400Z")
    monkeypatch.setattr(P, "radar_valids", lambda *a, **k: ["20261009T1745"])
    monkeypatch.setattr(P, "list_prefix", lambda *a, **k: ([], None, None, False))
    monkeypatch.setattr(P, "fetch", _404)
    _fake_grid(monkeypatch)
    done_dir = tmp_path / "obs" / "20261009T1745"
    done_dir.mkdir(parents=True)
    (done_dir / "DONE").write_text("2026-10-09T17:45:00Z")

    m = P.run_cycle(str(tmp_path), "https://x")
    assert [f["t"] for f in m["frames"]] == ["2026-10-09T17:45:00Z"]
    assert m["now_index"] == 0


def test_run_cycle_no_renderable_frames_still_writes_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "build_timeline", lambda *a, **k: _frames())
    monkeypatch.setattr(P, "latest_run", lambda *a, **k: "20261009T1400Z")
    monkeypatch.setattr(P, "radar_valids", lambda *a, **k: ["20261009T1745"])
    monkeypatch.setattr(P, "list_prefix", lambda *a, **k: ([], None, None, False))
    monkeypatch.setattr(P, "fetch", _404)
    _fake_grid(monkeypatch)

    m = P.run_cycle(str(tmp_path), "https://x")
    assert m["frames"] == []
    assert m["now_index"] == -1
    assert (tmp_path / "manifest.json").exists()
