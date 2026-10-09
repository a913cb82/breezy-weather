"""S3 unsigned-access tests: XML parsing offline, live calls opt-in (TDD)."""
import os

import pytest

from wx_tiles.s3 import parse_list_xml

SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
<Name>b</Name><KeyCount>2</KeyCount><MaxKeys>2</MaxKeys>
<IsTruncated>true</IsTruncated>
<NextContinuationToken>tok123</NextContinuationToken>
<Contents><Key>a/1.h5</Key><Size>10</Size></Contents>
<Contents><Key>a/2.h5</Key><Size>20</Size></Contents>
<CommonPrefixes><Prefix>a/sub/</Prefix></CommonPrefixes>
</ListBucketResult>"""


def test_parse_list_xml():
    keys, prefixes, token, truncated = parse_list_xml(SAMPLE)
    assert [k for k, _ in keys] == ["a/1.h5", "a/2.h5"]
    assert [s for _, s in keys] == [10, 20]
    assert prefixes == ["a/sub/"]
    assert token == "tok123" and truncated is True


def test_live_listing_opt_in():
    if os.environ.get("WX_LIVE_S3") != "1":
        pytest.skip("set WX_LIVE_S3=1 for network test")
    from wx_tiles.s3 import list_prefix
    keys, _, _, _ = list_prefix("met-office-radar-obs-data", "radar/2026/10/09/", max_keys=3)
    assert len(keys) == 3
