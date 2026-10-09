"""manifest.json builder (schema mirrors ARCHITECTURE.md)."""
from datetime import datetime, timezone

from wx_tiles.lut import lut_for_manifest


def build_manifest(frames: list, now_index: int, base_url: str,
                   snapshot: str, coverage: str) -> dict:
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "now_index": now_index,
        "lut": lut_for_manifest(),
        "frames": [{"t": f["t"], "kind": f["kind"], "run": f["run"],
                    "tiles": f["tiles"]} for f in frames],
        "snapshot": snapshot,
        "coverage": coverage,
    }
