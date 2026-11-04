#!/usr/bin/env python3
import json
import hashlib
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
resources, sources, hashes = set(), set(), set()
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
    resource_key = (item["kind"], item["resource"])
    assert resource_key not in resources, f"duplicate resource: {item['id']}"
    resources.add(resource_key)
    source = urlparse(item["sourceURL"])
    if source.hostname == "commons.wikimedia.org" and source.path.startswith("/wiki/File:"):
        from urllib.parse import unquote
        source_key = (item["kind"], unquote(source.path).replace("_", " "))
        assert source_key not in sources, f"duplicate source: {item['id']}"
        sources.add(source_key)
    for key in ("thumbnail", "resource"):
        if "raw.githubusercontent.com/cc9166/video-to-live-wallpapers/" in item[key]:
            assert (root / Path(urlparse(item[key]).path).name).is_file()
    if "raw.githubusercontent.com/cc9166/video-to-live-wallpapers/" in item["resource"]:
        media = root / Path(urlparse(item["resource"]).path).name
        digest = hashlib.sha256(media.read_bytes()).hexdigest()
        assert digest not in hashes, f"duplicate media bytes: {item['id']}"
        hashes.add(digest)
print(f"validated {len(ids)} wallpaper records")
