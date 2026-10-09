"""Timeline-builder tests: run selection + frame list (TDD, no network)."""
from datetime import datetime, timedelta, timezone

import pytest

from wx_tiles.runs import (
    MEDIUM_HOURS,
    NOWCAST_HOURS,
    SHORT_HOURS,
    build_timeline,
    candidate_runs,
    select_runs,
)


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y%m%dT%H%M").replace(tzinfo=timezone.utc)


def test_schedules_match_metoffice_docs():
    assert sorted(SHORT_HOURS) == [0, 6, 9, 12, 18, 21]
    assert sorted(MEDIUM_HOURS) == [3, 15]
    assert len(NOWCAST_HOURS) == 16
    assert 15 not in NOWCAST_HOURS  # no 15Z nowcast run


def test_candidate_runs_newest_first():
    now = _parse("20261009T1806")
    cands = candidate_runs(now, NOWCAST_HOURS, count=4)
    assert cands == ["20261009T1700Z", "20261009T1600Z", "20261009T1400Z", "20261009T1300Z"]


def test_select_runs_prefers_newest_published():
    published = {"20261009T1400Z", "20261009T1300Z"}

    def exists(run: str) -> bool:
        return run in published

    now = _parse("20261009T1806")
    assert select_runs(now, NOWCAST_HOURS, exists) == "20261009T1400Z"


def test_select_runs_skips_unpublished():
    published = {"20261009T1200Z"}

    def exists(run: str) -> bool:
        return run in published

    now = _parse("20261009T1806")
    assert select_runs(now, SHORT_HOURS, exists) == "20261009T1200Z"


def test_build_timeline_shape():
    # Fake inventory: nowcast run covers +0..+12h at 15-min, short covers hourly.
    now = _parse("20261009T1800")
    nowcast_valid = {
        (now + timedelta(minutes=15 * i)).strftime("%Y%m%dT%H%MZ") for i in range(49)
    }
    frames = build_timeline(
        now,
        radar_valids=[(now - timedelta(minutes=15 * i)).strftime("%Y%m%dT%H%M") for i in range(24)],
        nowcast_run="20261009T1400Z",
        nowcast_valids=nowcast_valid,
        short_run="20261009T1200Z",
        medium_run="20261009T0300Z",
    )
    kinds = [f["kind"] for f in frames]
    assert kinds[0] == "obs" and kinds[-1] == "model"
    assert len([k for k in kinds if k == "obs"]) == 24
    # strictly increasing validity
    ts = [f["t"] for f in frames]
    assert ts == sorted(ts)
    # every frame has a tile url + run
    assert all(f["tiles"] and f["run"] for f in frames)


def test_build_timeline_falls_back_to_hourly():
    # nowcast missing the far tail -> those validities come from the short run
    now = _parse("20261009T1806")
    grid0 = now.replace(minute=0)  # model grid snaps to :00/:15/:30/:45
    valids = {(grid0 + timedelta(minutes=15 * i)).strftime("%Y%m%dT%H%MZ") for i in range(33)}
    frames = build_timeline(
        now,
        radar_valids=[now.strftime("%Y%m%dT%H%M")],
        nowcast_run="20261009T1400Z",
        nowcast_valids=valids,  # only +0..+8h
        short_run="20261009T1200Z",
        medium_run="20261009T0300Z",
    )
    by_t = {f["t"]: f for f in frames}
    tail = (grid0 + timedelta(hours=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert by_t[tail]["run"] == "20261009T1200Z"
    assert by_t[tail]["kind"] == "model"
