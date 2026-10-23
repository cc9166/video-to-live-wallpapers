# Video To Live · Wallpaper collection

A versioned wallpaper collection for Video To Live. It starts with 17 original still images and one CC0 nature-video excerpt, then adds a small CC0 batch from Wikimedia Commons each day.

## Catalog

`catalog.json` is the app-readable version 1 feed. It includes titles, types, HTTPS media URLs, and provenance records. Publish media before updating the catalog. Keep existing asset paths immutable; use a new ID and filename for a replacement.

The original stills explore mountains, oceans, dunes, forest mist, architecture and soft mineral color. These are AI-created artworks, not photographs documenting real locations. No images or videos were extracted from Cuto.

## Source record

Snowy Creek is a three-second transcoded excerpt from **Sahalie Falls during Winter jm1101.webm** by **CubanMojitoCrisis69**, offered under **CC0 1.0**.

- Original: https://commons.wikimedia.org/wiki/File:Sahalie_Falls_during_Winter_jm1101.webm
- CC0: https://creativecommons.org/publicdomain/zero/1.0/
- Modifications: excerpt from 10 to 13 seconds; H.264/AAC transcode, 1080 × 1920, 30 fps.

The CC0 designation applies to that source clip, not automatically to all files in this repository. Original still artworks are provided for use in the Video To Live wallpaper collection; this repository does not grant a general third-party stock-library license.

## Daily curation

The scheduled GitHub Action runs every day at 03:23 UTC and attempts to add two still wallpapers and one short live-wallpaper clip from `curation-queue.json`. Queue entries are selected from Wikimedia Commons in advance; the publisher re-checks their current license and resolution, rejects sources that would need enlargement after a 9:16 crop, transcodes video to a three-second H.264 MP4, creates a small thumbnail, validates the catalog, and then commits the result. This prevents broad search results from being published without visual review. The collection caps automated growth at 60 stills and 24 live clips.

The source URL, creator record, and detected license remain in `catalog.json` for audits. The app does not place source metadata in the main wallpaper flow. Cuto is only a reference for breadth and visual restraint; the automation does not access or copy Cuto assets.

Only queue entries marked `review: approved` can be published. The workflow also validates unique IDs, category values, optional discovery tags, live source license, source dimensions and local files. The visual checklist is documented in `QUALITY.md`; automated checks support human curation rather than replacing it.

## Operation

GitHub raw URLs are used for this initial small collection. Availability and download speed depend on the user's network. The app includes this first collection locally as an offline fallback. Future growth can move media to an object store/CDN while retaining the same JSON schema.

`manifest.json` records the published files and SHA-256 hashes for release checks.
