# Wallpaper quality gate

The scheduled publisher may only consume entries whose `review` value is `approved`. New discoveries stay outside the publishing path until they have been reviewed. A rejected record remains in the queue as an audit trail and is skipped.

Approval requires all of the following:

- CC0 or public-domain status recorded by the source and re-checked at publication time.
- Enough source pixels to produce a 1080×1920 crop without enlargement.
- A clean 9:16 composition with a quiet lock-screen clock area.
- No people, faces, brands, logos, watermarks, signs, advertisements or private information.
- No obvious compression artifacts, clipped highlights, muddy shadows or accidental blur.
- Still images must remain readable as a 480×853 thumbnail.
- Motion clips must have visible subject movement in the first two seconds, a stable camera and a clean composition. Avoid sudden cuts, shake, strobing and distracting audio. A large file or a high pixel count does not establish a lively lock-screen result.

Automated checks enforce review state, duplicate IDs, license, source dimensions, output URLs, file presence and catalog schema. Visual taste still requires human review; an automated score cannot guarantee a restrained editorial style.

For each publishing batch, inspect the thumbnail, the full-screen crop and the resulting Live Photo on an iPhone before expanding the approved queue.

## 2026-11-04 refresh

Use original-resolution downloads for stills; source metadata alone is insufficient. Validate decoded pixels before cropping and never enlarge a thumbnail. New stills target 1440×2560 where source pixels allow, otherwise 1080×1920. New thumbnails are 720×1280. Motion uses silent 1080×1920 H.264 at CRF 19, with all 90 frames decoded and motion sampled before approval. Catalog validation rejects repeated resource URLs, byte-identical media and repeated Commons media sources. Visually similar waves and forest sequences require manual selection.

See `quality-review-20261104.json` for additions, full-resolution replacements and withdrawn near-duplicates/weak compositions. Existing files remain in Git so old cached URLs do not break.

## 2026-11-10 HD audit

Audited the original dimensions of all 15 listed motion sources. Withdrew `commons-92787549` and `cc0-canyon-clouds` from the catalog: both originals are landscape 1920×1080 and cannot produce a native 1080×1920 crop. Their files remain available for existing cached URLs. No newly found motion was approved solely for having large dimensions; dark, cluttered and weak compositions were rejected.

Added six manually inspected stills in misty forest, coastline and floral macro styles. New stills use 2160×3840 where the decoded source has enough pixels, otherwise 1440×2560 or 1080×1920. JPEG quality is 94. Thumbnails remain separate 720×1280 previews; downloads use the full image.

The publisher now verifies the decoded video dimensions with ffprobe, including rotation, before cropping. New records retain source and output pixel dimensions, and catalog validation rejects enlargement. More pixels do not establish sharpness, attractive composition or iOS dynamic lock-screen compatibility; those still require visual and device checks.

See `quality-review-20261110.json` for the batch record. Dynamic exports inside the app are tested separately; no 4K Live Wallpaper compatibility is claimed by this catalog update.

Two existing approved motion scenes now use new `-hd` resource URLs: Alaskan Aurora (1440×2560, 3 seconds) and Cat's Head Nebula (2160×3840, 3 seconds). These are silent source clips for preview and conversion, not ready-to-set 4K paired Live Photos. The tested app path uses native-pixel still posters and 1080×1920 motion video. Old 1080 resource files stay online, while new URLs avoid reusing stale cached copies. Both new clips were fully decoded and visually checked before publication.

Discovery may now include pets, flowers opening, bubbles and fireworks. Previously, blanket title exclusions for `cat`, `dog`, `bird` and `firework` excluded these requested themes (and could match parts of unrelated words). This changes the discovery pool only: the scheduled publisher continues to consume reviewed, approved queue entries. Reject low light, cluttered rooms, watermarks and camera shake even if the subject is cute or the source is large.
