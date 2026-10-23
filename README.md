# Video To Live · Wallpaper collection

A versioned wallpaper collection for Video To Live. It combines original artwork with reviewed CC0 images and short video excerpts, then adds a small CC0 batch from Wikimedia Commons each day.

## Catalog

`catalog.json` is the app-readable version 1 feed. It includes titles, types, HTTPS media URLs, and provenance records. Publish media before updating the catalog. Keep existing asset paths immutable; use a new ID and filename for a replacement.

The original stills explore mountains, oceans, dunes, forest mist, architecture and soft mineral color. These are AI-created artworks, not photographs documenting real locations. No images or videos were extracted from Cuto.

## Source record

Snowy Creek is a three-second transcoded excerpt from **Sahalie Falls during Winter jm1101.webm** by **CubanMojitoCrisis69**, offered under **CC0 1.0**.

- Original: https://commons.wikimedia.org/wiki/File:Sahalie_Falls_during_Winter_jm1101.webm
- CC0: https://creativecommons.org/publicdomain/zero/1.0/
- Modifications: excerpt from 10 to 13 seconds; H.264/AAC transcode, 1080 × 1920, 30 fps.

The following reviewed CC0 clips were also added as three-second, muted H.264 excerpts at 1080 × 1920 and 30 fps. Landscape originals were cropped for a clean 9:16 lock-screen composition.

- **Coastal Rhythm** from *Ocean surface waves 10.ogv* by Mostafameraji: https://commons.wikimedia.org/wiki/File:Ocean_surface_waves_10.ogv
- **Molten Sunset** from *Golden sunset filmed in January.webm* by Vicky Ponce: https://commons.wikimedia.org/wiki/File:Golden_sunset_filmed_in_January.webm
- **Canyon Sky** from *Timelapse of Clouds over Bellevue Canyon.webm* by Extemporalist: https://commons.wikimedia.org/wiki/File:Timelapse_of_Clouds_over_Bellevue_Canyon.webm

The live collection follows a restrained mix of slow natural motion and occasional abstract texture: ocean surfaces, shore breaks, drifting snow, cloud movement, waterfalls and soft light. This gives the app several distinct styles without copying another app's media.

A manually reviewed October 2026 refresh added **Stillwater**, **Green Veil Falls**, **Ember Night**, and **Snowfall Quiet**, all from CC0 Commons sources recorded in `catalog.json`. Five visually busy or artifact-prone live entries were removed from the active catalog after full-frame review; their immutable files remain available for older cached catalogs.

The CC0 designation applies to that source clip, not automatically to all files in this repository. Original still artworks are provided for use in the Video To Live wallpaper collection; this repository does not grant a general third-party stock-library license.

## Daily curation

The scheduled GitHub Action runs every day at 03:23 UTC and attempts to add four still wallpapers and two short live-wallpaper clips from `curation-queue.json`. A manual workflow run can choose a larger or smaller one-off batch. Queue entries are selected from Wikimedia Commons in advance; the publisher re-checks their current license and resolution, rejects sources that would need enlargement after a 9:16 crop, transcodes video to a three-second H.264 MP4, creates a small thumbnail, validates the catalog, and then commits the result. This prevents broad search results from being published without visual review. The collection caps automated growth at 120 stills and 40 live clips.

The source URL, creator record, and detected license remain in `catalog.json` for audits. The app does not place source metadata in the main wallpaper flow. Cuto is only a reference for breadth and visual restraint; the automation does not access or copy Cuto assets.

Only queue entries marked `review: approved` can be published. The workflow also validates unique IDs, category values, optional discovery tags, live source license, source dimensions and local files. The visual checklist is documented in `QUALITY.md`; automated checks support human curation rather than replacing it.

## Manual additions

New reviewed Commons media can be added at any time by appending a record to `curation-queue.json`, validating it with `python tools/validate_queue.py`, committing the queue, and running **Update wallpaper collection** from the Actions tab. Set `review` to `approved` only after checking the full-size source against `QUALITY.md`; unreviewed and rejected records remain unpublished. Use `rejected-visual` for candidates that fail composition or cleanliness review, and `rejected-upscale` for sources that lack enough pixels. The manual run accepts still and video batch sizes, so a larger reviewed release does not require a workflow edit.

Original or separately licensed media can also be committed directly with an immutable ID, full-size file, thumbnail and matching `catalog.json` record. Run `python tools/validate_catalog.py`, regenerate `manifest.json`, and inspect the result in the app before publishing. Never replace an existing asset path in place because app and CDN caches may keep the earlier bytes.

Use one backward-compatible primary category: `mountains`, `ocean`, `nature`, `minimal`, `abstract`, or `architecture`. Add any of `sky`, `botanical`, `city`, and `night` as discovery tags. Tags allow overlapping styles without fragmenting the main navigation, and older app versions safely ignore them.

## Operation

GitHub raw URLs are used for this initial small collection. Availability and download speed depend on the user's network. The app includes this first collection locally as an offline fallback. Future growth can move media to an object store/CDN while retaining the same JSON schema.

`manifest.json` records the published files and SHA-256 hashes for release checks.
