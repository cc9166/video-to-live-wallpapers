#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
queue = json.loads((root / "curation-queue.json").read_text())
categories = {"mountains", "ocean", "nature", "minimal", "abstract", "architecture"}
reviews = {"approved", "rejected-upscale"}

assert isinstance(queue, list) and queue
pageids = [entry["pageid"] for entry in queue]
assert len(pageids) == len(set(pageids))
for entry in queue:
    assert isinstance(entry["pageid"], int) and entry["pageid"] > 0
    assert entry["kind"] in {"still", "live"}
    assert entry["category"] in categories
    assert entry["review"] in reviews

approved = sum(entry["review"] == "approved" for entry in queue)
rejected = len(queue) - approved
print(f"validated {len(queue)} reviewed candidates: {approved} approved, {rejected} rejected")
