#!/usr/bin/env python3
"""Release one reviewed reserve item into both wallpaper catalog formats.

Run in a full checkout. The workflow commits only after this script exits
successfully. An empty reserve is a failure, never a false daily-update claim.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

BASE = 'https://raw.githubusercontent.com/cc9166/video-to-live-wallpapers/main/'
PROFILE = 'db62e673199e'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def local_path(root, url):
    parsed = urlsplit(url)
    expected = urlsplit(BASE)
    require(parsed.scheme == 'https' and parsed.netloc == expected.netloc and
            parsed.path.startswith(expected.path) and not parsed.query and not parsed.fragment,
            'Catalog page points outside the configured repository')
    relative = parsed.path[len(expected.path):]
    require(relative and not relative.startswith('/') and '..' not in Path(relative).parts,
            'Invalid catalog path')
    return root / relative


def release(root: Path):
    root = root.resolve()
    index = read(root / 'catalog-v2.json')
    queue_path = root / 'daily-reserve' / 'queue.json'
    queue = read(queue_path)
    require(index.get('version') == 2 and isinstance(index.get('pages'), list), 'Invalid paged index')
    require(queue.get('version') == 1 and isinstance(queue.get('items'), list), 'Invalid daily reserve')
    today = dt.datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    if queue.get('lastPublishedDate') == today:
        print('Today already has a scheduled wallpaper; no duplicate release')
        return
    records = []
    for page in index['pages']:
        doc = read(local_path(root, page['url']))
        require(doc.get('version') == 2 and len(doc.get('items', [])) == page.get('count'), 'Invalid page')
        records.extend(doc['items'])
    require(len(records) == index.get('total'), 'Paged catalog count mismatch')
    ids = [record['id'] for record in records]
    require(len(ids) == len(set(ids)), 'Published catalog has duplicate IDs')
    resources = {r['resource'] for r in records}
    choices = [q for q in queue['items'] if q.get('status') == 'approved' and q.get('record', {}).get('id') not in ids and q.get('record', {}).get('resource') not in resources]
    require(choices, 'No reviewed, unpublished wallpaper remains in the daily reserve')
    item = choices[0]
    record = item['record']
    require(record.get('kind') == 'still' and record.get('id') and record.get('title') and record.get('credit') and record.get('license'), 'Invalid reserve item')
    require(urlsplit(record.get('sourceURL', '')).scheme == 'https', 'Invalid source')
    require(record.get('studioFolder') in {f['id'] for f in index['categories']}, 'Unknown folder')
    for role in ['resource', 'thumbnail']:
        path = local_path(root, record[role])
        require(path.is_file(), 'Reserve asset is missing: ' + str(path))
        expected_hash = item.get('sha256', {}).get(role)
        require(expected_hash and hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash, 'Reserve asset changed: ' + role)
    records.insert(0, record)
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    release_id = uuid.uuid4().hex[:16]
    documents = {}
    pages = []
    for start in range(0, len(records), 40):
        chunk = records[start:start + 40]
        relative = 'releases/' + release_id + '/page-%03d.json' % (start // 40 + 1)
        documents[relative] = {'version': 2, 'items': chunk}
        groups = {}
        for entry in chunk:
            key = (entry.get('studioFolder', ''), entry['kind'])
            groups[key] = groups.get(key, 0) + 1
        pages.append({'url': BASE + relative, 'count': len(chunk),
                      'folders': sorted({r.get('studioFolder', '') for r in chunk}),
                      'kinds': sorted({r['kind'] for r in chunk}),
                      'groups': [{'folder': f, 'kind': k, 'count': count} for (f, k), count in sorted(groups.items())]})
    categories = index['categories']
    for category in categories:
        scope = {category['id']}
        while True:
            expanded = scope | {child['id'] for child in categories if child.get('parent', '') in scope}
            if expanded == scope: break
            scope = expanded
        category['counts'] = {kind: sum(r['kind'] == kind and r.get('studioFolder', '') in scope for r in records) for kind in ['still', 'live']}
    index.update(updatedAt=timestamp, release=release_id, total=len(records), categories=categories,
                 pages=pages, compatibilityIDs=[r['id'] for r in records])
    # Old versions do not understand original paired-photo records reliably.
    # Keep them in v2 and reserve legacy slots for compatible still/video items.
    compatible = [r for r in records if not (r['kind'] == 'live' and r.get('pairedPhoto'))]
    legacy_items = [{k: v for k, v in r.items() if k != 'studioFolder'} for r in reversed(compatible[:200])]
    legacy = {'version': 1, 'updatedAt': timestamp, 'items': legacy_items}
    require(len(json.dumps(legacy, ensure_ascii=False).encode()) <= 512_000, 'Legacy catalog is too large')
    layout_path = root / 'studio' / (PROFILE + '.json')
    layout = read(layout_path)
    require(layout.get('version') == 1 and isinstance(layout.get('entries'), list), 'Invalid studio layout')
    require(record['id'] not in {e['catalogID'] for e in layout['entries']}, 'Item already in studio layout')
    layout['entries'].insert(0, {'id': item['entryID'], 'folder': record['studioFolder'], 'catalogID': record['id']})
    item.update(status='published', publishedAt=timestamp, release=release_id)
    queue['lastPublishedDate'] = today
    documents.update({'catalog.json': legacy, 'catalog-v2.json': index,
                      'studio/' + PROFILE + '.json': layout, 'daily-reserve/queue.json': queue})
    for name, document in documents.items(): write(root / name, document)
    manifest_path = root / 'manifest.json'
    manifest = read(manifest_path)
    require(isinstance(manifest, list), 'Invalid manifest')
    by_name = {entry['file']: entry for entry in manifest}
    for path in [local_path(root, record['resource']), local_path(root, record['thumbnail'])] + [root / name for name in documents]:
        content = path.read_bytes()
        name = path.relative_to(root).as_posix()
        by_name[name] = {'file': name, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    write(manifest_path, sorted(by_name.values(), key=lambda e: e['file']))
    print('Published one reviewed wallpaper:', record['id'], '; reserve left:', sum(q.get('status') == 'approved' for q in queue['items']))

if __name__ == '__main__':
    try: release(Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print('Daily wallpaper release stopped:', error, file=sys.stderr)
        raise SystemExit(1)
