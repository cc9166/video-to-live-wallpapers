#!/usr/bin/env python3
"""Add a small daily batch of CC0 wallpapers from Wikimedia Commons."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "VideoToLiveWallpaperCurator/1.0 (https://github.com/cc9166/video-to-live-wallpapers)"
BASE = "https://raw.githubusercontent.com/cc9166/video-to-live-wallpapers/main"
LICENSES = {"CC0", "CC0 1.0", "Public domain", "Public domain mark"}
STILL_SEARCHES = {
    "mountains": ("mountain landscape", "glacier landscape"),
    "ocean": ("ocean waves", "coast sea"),
    "nature": ("forest mist", "botanical leaf", "cloud landscape"),
    "minimal": ("desert sand", "snow landscape", "minimal landscape"),
    "abstract": ("abstract texture", "mineral macro", "water texture"),
    "architecture": ("modern architecture", "building facade", "architectural detail"),
}
VIDEO_SEARCHES = {
    "ocean": ("ocean waves", "sea water"),
    "nature": ("waterfall", "rain", "clouds timelapse", "river", "snow"),
    "abstract": ("water slow motion", "light abstract"),
}
DENY = {
    "person", "people", "portrait", "selfie", "woman", "women", "man ", "men ", "child", "baby",
    "car", "train", "aircraft", "airport", "ship", "boat", "bird", "dog", "cat", "concert", "music",
    "logo", "poster", "diagram", "map", "screenshot", "advert", "food", "chocolate", "weapon", "firework",
}


def api(params: dict) -> dict:
    query = {"action": "query", "format": "json", "origin": "*", **params}
    request = urllib.request.Request(API + "?" + urllib.parse.urlencode(query), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def title_for(filename: str) -> str:
    value = Path(filename.removeprefix("File:")).stem
    value = re.sub(r"\s*\((?:Unsplash|Tumblr)\)\s*$", "", value, flags=re.I)
    quoted = re.match(r"^[\"']([^\"']{2,40})[\"']", value)
    if quoted:
        return quoted.group(1)
    value = re.split(r"\s+[–—-]\s+", value, maxsplit=1)[0]
    value = re.sub(r",?\s*20\d{2}(?:[-_ ].*)?$", "", value)
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = re.sub(r"[_-]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    words = value.split()
    if len(words) > 6:
        value = " ".join(words[:6])
    return value[:40] or "Untitled Scene"


def candidates(term: str, media: str) -> list[dict]:
    response = api({
        "generator": "search", "gsrsearch": f'filetype:{media} incategory:"CC-Zero" {term}',
        "gsrnamespace": "6", "gsrlimit": "40", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1800",
    })
    result = []
    for page in response.get("query", {}).get("pages", {}).values():
        info = page.get("imageinfo", [{}])[0]
        metadata = info.get("extmetadata", {})
        license_name = clean(metadata.get("LicenseShortName", {}).get("value", ""))
        lowered = page.get("title", "").lower()
        if license_name not in LICENSES or any(word in lowered for word in DENY):
            continue
        if info.get("width", 0) < 900 or info.get("height", 0) < 900:
            continue
        result.append({"page": page, "info": info, "metadata": metadata, "license": license_name})
    return sorted(result, key=lambda item: (item["info"].get("height", 0) < item["info"].get("width", 0), -item["info"].get("height", 0)))


def candidate_by_pageid(pageid: int) -> dict:
    response = api({
        "pageids": str(pageid), "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1800",
    })
    page = next(iter(response.get("query", {}).get("pages", {}).values()))
    info = page.get("imageinfo", [{}])[0]
    metadata = info.get("extmetadata", {})
    license_name = clean(metadata.get("LicenseShortName", {}).get("value", ""))
    if license_name not in LICENSES or info.get("width", 0) < 900 or info.get("height", 0) < 900:
        raise ValueError("source no longer passes the license or resolution gate")
    return {"page": page, "info": info, "metadata": metadata, "license": license_name}


def download(url: str, destination: Path, maximum: int = 180_000_000) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > maximum:
                raise ValueError("source file exceeds byte limit")
            output.write(chunk)


def common_item(candidate: dict, category: str, kind: str, asset_id: str) -> dict:
    page, info, metadata = candidate["page"], candidate["info"], candidate["metadata"]
    artist = clean(metadata.get("Artist", {}).get("value", "")) or info.get("user", "Wikimedia Commons contributor")
    return {
        "id": asset_id,
        "title": title_for(page["title"]),
        "kind": kind,
        "category": category,
        "credit": (artist[:120] + " · Wikimedia Commons") if artist else "Wikimedia Commons",
        "sourceURL": info.get("descriptionurl") or "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_")),
        "license": candidate["license"],
    }


def add_still(root: Path, candidate: dict, category: str, base: str) -> dict:
    asset_id = f"commons-{candidate['page']['pageid']}"
    image_name, thumb_name = asset_id + ".jpg", asset_id + "-thumb.jpg"
    source_url = candidate["info"].get("thumburl") or candidate["info"]["url"]
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "source"
        download(source_url, source, 60_000_000)
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            wallpaper = ImageOps.fit(image, (1080, 1920), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            wallpaper.save(root / image_name, "JPEG", quality=89, optimize=True, progressive=True)
            wallpaper.resize((480, 853), Image.Resampling.LANCZOS).save(root / thumb_name, "JPEG", quality=80, optimize=True, progressive=True)
    item = common_item(candidate, category, "still", asset_id)
    item.update(thumbnail=f"{base}/{thumb_name}", resource=f"{base}/{image_name}")
    return item


def add_video(root: Path, candidate: dict, category: str, base: str) -> dict:
    asset_id = f"commons-{candidate['page']['pageid']}"
    video_name, thumb_name = asset_id + ".mp4", asset_id + "-thumb.jpg"
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "source"
        download(candidate["info"]["url"], source)
        video_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "0", "-i", str(source), "-t", "3",
            "-vf", video_filter, "-an", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(root / video_name),
        ], check=True, timeout=180)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "1", "-i", str(root / video_name),
            "-frames:v", "1", "-q:v", "3", str(root / thumb_name),
        ], check=True, timeout=60)
    item = common_item(candidate, category, "live", asset_id)
    item.update(thumbnail=f"{base}/{thumb_name}", resource=f"{base}/{video_name}")
    return item


def update_manifest(root: Path) -> None:
    files = sorted(path for path in root.iterdir() if path.is_file() and path.name not in {"manifest.json"})
    manifest = [{"file": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def add_batch(root: Path, searches: dict, wanted: int, kind: str, existing: list[dict], base: str) -> int:
    used = {item["id"] for item in existing}
    categories = list(searches)
    added = 0
    cursor = 0
    while added < wanted and cursor < len(categories) * 8:
        category = categories[cursor % len(categories)]
        terms = searches[category]
        term = terms[(cursor // len(categories)) % len(terms)]
        cursor += 1
        try:
            pool = candidates(term, "bitmap" if kind == "still" else "video")
        except Exception as error:
            print(f"skip search {term}: {error}")
            continue
        for candidate in pool:
            asset_id = f"commons-{candidate['page']['pageid']}"
            if asset_id in used:
                continue
            try:
                item = add_still(root, candidate, category, base) if kind == "still" else add_video(root, candidate, category, base)
            except Exception as error:
                print(f"skip {candidate['page']['title']}: {error}")
                continue
            existing.append(item)
            used.add(asset_id)
            added += 1
            print(f"added {kind}: {item['title']} [{category}]")
            break
    return added


def add_from_queue(root: Path, queue: list[dict], still_wanted: int, video_wanted: int,
                   existing: list[dict], base: str) -> int:
    used = {item["id"] for item in existing}
    remaining = {"still": still_wanted, "live": video_wanted}
    added = 0
    for entry in queue:
        kind = entry["kind"]
        asset_id = f"commons-{entry['pageid']}"
        if remaining.get(kind, 0) <= 0 or asset_id in used:
            continue
        try:
            candidate = candidate_by_pageid(entry["pageid"])
            item = add_still(root, candidate, entry["category"], base) if kind == "still" else add_video(root, candidate, entry["category"], base)
        except Exception as error:
            print(f"skip queued page {entry['pageid']}: {error}")
            continue
        existing.append(item)
        used.add(asset_id)
        remaining[kind] -= 1
        added += 1
        print(f"added queued {kind}: {item['title']} [{entry['category']}]")
        if not any(remaining.values()):
            break
    return added


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--base-url", default=BASE)
    parser.add_argument("--still-count", type=int, default=2)
    parser.add_argument("--video-count", type=int, default=1)
    parser.add_argument("--max-stills", type=int, default=60)
    parser.add_argument("--max-videos", type=int, default=24)
    args = parser.parse_args()
    catalog_path = args.root / "catalog.json"
    catalog = json.loads(catalog_path.read_text())
    items = catalog["items"]
    still_count = min(args.still_count, max(0, args.max_stills - sum(i["kind"] == "still" for i in items)))
    video_count = min(args.video_count, max(0, args.max_videos - sum(i["kind"] == "live" for i in items)))
    queue = json.loads((args.root / "curation-queue.json").read_text())
    added = add_from_queue(args.root, queue, still_count, video_count, items, args.base_url.rstrip("/"))
    if added:
        catalog["updatedAt"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
        update_manifest(args.root)
    print(f"finished: {added} new items; {len(items)} total")


if __name__ == "__main__":
    main()
