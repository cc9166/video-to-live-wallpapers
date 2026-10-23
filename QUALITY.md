# Wallpaper quality gate

The scheduled publisher may only consume entries whose `review` value is `approved`. New discoveries stay outside the publishing path until they have been reviewed. A rejected record remains in the queue as an audit trail and is skipped.

Approval requires all of the following:

- CC0 or public-domain status recorded by the source and re-checked at publication time.
- Enough source pixels to produce a 1080×1920 crop without enlargement.
- A clean 9:16 composition with a quiet lock-screen clock area.
- No people, faces, brands, logos, watermarks, signs, advertisements or private information.
- No obvious compression artifacts, clipped highlights, muddy shadows or accidental blur.
- Still images must remain readable as a 480×853 thumbnail.
- Motion clips must be calm, loop-friendly and free of sudden cuts, camera shake, flashing or distracting audio.

Automated checks enforce review state, duplicate IDs, license, source dimensions, output URLs, file presence and catalog schema. Visual taste still requires human review; an automated score cannot guarantee a restrained editorial style.

For each publishing batch, inspect the thumbnail, the full-screen crop and the resulting Live Photo on an iPhone before expanding the approved queue.
