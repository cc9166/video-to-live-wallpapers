#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
categories = {"mountains", "ocean", "nature", "minimal", "abstract", "architecture"}
tags = {"sky", "botanical", "city", "night"}
catalog = json.loads((root / "catalog.json").read_text())
assert catalog["version"] == 1
assert 1 <= len(catalog["items"]) <= 200
ids = [item["id"] for item in catalog["items"]]
assert len(ids) == len(set(ids))
for item in catalog["items"]:
    assert item["kind"] in {"still", "live"}
    assert item.get("category") in categories
    assert isinstance(item.get("tags", []), list)
    assert len(item.get("tags", [])) == len(set(item.get("tags", [])))
    assert set(item.get("tags", [])) <= tags
    assert item["license"] and item["credit"]
    assert urlparse(item["thumbnail"]).scheme == "https"
    assert urlparse(item["resource"]).scheme == "https"
    assert urlparse(item["sourceURL"]).scheme == "https"
    for key in ("thumbnail", "resource"):
        if "raw.githubusercontent.com/cc9166/video-to-live-wallpapers/" in item[key]:
            assert (root / Path(urlparse(item[key]).path).name).is_file()
print(f"validated {len(ids)} wallpaper records")
