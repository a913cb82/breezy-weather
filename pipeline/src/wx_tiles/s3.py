"""Unsigned S3 access over plain HTTPS (no AWS account, stdlib only)."""
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
TIMEOUT = 25
UA = {"User-Agent": "wx-tiles/0.1 (personal research pipeline)"}


def _bucket_url(bucket: str, region: str = "eu-west-2") -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com"


def parse_list_xml(xml_text: str):
    x = ET.fromstring(xml_text)
    keys = [(c.find("s:Key", NS).text, int(c.find("s:Size", NS).text))
            for c in x.findall("s:Contents", NS)]
    prefixes = [p.text for p in x.findall("s:CommonPrefixes/s:Prefix", NS)]
    tok = x.find("s:NextContinuationToken", NS)
    trunc = x.find("s:IsTruncated", NS)
    return keys, prefixes, (tok.text if tok is not None else None), \
        (trunc.text == "true" if trunc is not None else False)


def list_prefix(bucket, prefix, delimiter=None, max_keys=1000, token=None):
    q = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
    if delimiter:
        q["delimiter"] = delimiter
    if token:
        q["continuation-token"] = token
    url = _bucket_url(bucket) + "/?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return parse_list_xml(r.read().decode())


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


def exists(url: str) -> bool:
    """Cheap existence probe: 1-byte range GET (unsigned buckets answer 206)."""
    req = urllib.request.Request(url, headers={**UA, "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status in (200, 206)
    except Exception:
        return False
