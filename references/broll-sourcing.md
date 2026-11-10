# B-roll - finding and preparing footage (free-first)

## Contents
1. What good B-roll looks like here
2. Where it may come from (and rights)
3. Free sources and tested retrieval methods (Pixabay MCP, Wikimedia Commons, thesvg MCP)
4. Download, verify, prepare
5. Preparing clips: in-points, focus, mattes
6. Swapping clips later
Appendix A - paid generation with Seedance via Higgsfield (only on explicit request)
Appendix B - prompt template for generated shots (appendix A material)

## 1. What good B-roll looks like here

- It shows exactly the thing being said, recognisable in half a second.
- It moves: a camera move, a gesture, a crowd surging, a light pulsing. 2-5 s of usable motion.
- It survives black-and-white: strong shapes and contrast, a clear subject.
- It crops to 9:16 (or to the top half, 1080x960, for split layouts): the subject must sit where
  the crop lands. Wide footage is fine - set `fx` to the subject's horizontal position.
- Cinematic beats generic: a lit close-up of hands on a keyboard beats a stock "office" wide shot.
- Interface footage (screen recordings, UI mock-ups) works well for tech topics; for logos and
  inline brand marks, the thesvg MCP section below.

## 2. Where it may come from

In order of preference:
1. **The user's own material** - other recordings, screen captures, product shots, photos (photos
   need motion: push-in or photo-on-photo stacking).
2. **Free-licence stock and archives** - sourced with the tested methods in section 3: Pixabay
   (MCP), Wikimedia Commons (HTTP API, huge public-domain archive), logos/icons via the thesvg
   MCP. This is the default route: it costs nothing and needs no approval.
3. **Licensed or press material** the user has the right to use.
4. **Paid AI generation** (appendix A) - only when the user explicitly asks for generated shots
   and approves the credit cost.

Do not download or use clips from films, series, ads or other people's social posts unless the
user owns the rights or explicitly confirms they have a licence. When the user asks for "a scene
like the one in film X", do not copy the scene: pick or film an original shot with the same idea,
camera and motion, entirely original people, wardrobe and design (in the paid appendix, this is
what text-to-video is for).

Save files as `PROJECT/broll/<insert-id>_<n>.mp4` (or similar readable names). Keep attribution
requirements in `PROJECT/CREDITS.md` (Commons files often require a credit line; Pixabay does not).

## 3. Free sources and tested retrieval methods

Everything below was executed end-to-end during a live run (search -> URL -> HEAD -> download ->
integrity check), so the recipes are proven, not theoretical.

### 3.1 Pixabay MCP (images + video footage)
Tools (inside OpenCode): `pixabay.search_pixabay_images` and `pixabay.search_pixabay_videos`.
- Images: `{ query, image_type: "photo" | "illustration" | "vector", orientation: "all" |
  "horizontal" | "vertical", per_page: 3..200 }`. Results come with tags, author and a direct
  URL (pattern: `https://pixabay.com/get/<hash>_640.jpg`, served `image/jpeg`).
- Videos: `{ query, video_type: "film" | "animation", orientation, per_page, min_duration,
  max_duration }` - results list duration per clip and a direct MP4
  (pattern: `https://cdn.pixabay.com/video/<y>/<m>/<d>/<id>_medium.mp4`, served `video/mp4`),
  tested ~16 MB for a 40 s 1080p clip.
- Query tips: tag lists in results show how Pixabay indexes; reuse a result's own tags to refine
  the next query. Prefer `orientation: "vertical"` when available - it saves a recrop; otherwise
  crop wide footage per section 1.
- No API key handling and no credits on our side - the MCP is free.

### 3.2 Wikimedia Commons (HTTP API - no key, no account, huge PD archive)
Two steps, both tested:
```bash
# 1) search (video; use filetype:image / filetype:bitmap for stills, filetype:audio for music)
curl -s "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=filetype:video%20<URLENCODED_TERMS>&srnamespace=6&srlimit=5&format=json"
# 2) metadata + direct URL for the chosen File:<title>
curl -s "https://commons.wikimedia.org/w/api.php?action=query&titles=<URLENCODED_File_title>&prop=imageinfo&iiprop=url|size|mime|duration|sha1&format=json"
```
- `imageinfo.url` is the direct file (e.g. `https://upload.wikimedia.org/.../Name_09.ogv`),
  with mime, duration, resolution, size bytes and `sha1`.
- Commons video is usually `.ogv` or `.webm`: transcode to MP4 before QA (section 4).
- **Rate limit warning (tested)**: a bare `Invoke-WebRequest` was refused with HTTP 429; the same
  download succeeded with `curl -L` + a descriptive User-Agent + retries. Always use the curl
  recipe in section 4 for `upload.wikimedia.org`.
- **Integrity (tested)**: compare the `sha1` from `imageinfo` with `shasum -a 1 <file>` - the
  real-world check matched on a 15 442 896-byte file.
- Licence field comes on the file page; many are public domain - ideal for archival looks. Record
  file + licence + author in `PROJECT/CREDITS.md`.

### 3.3 thesvg MCP (logos, brand icons, UI icons)
Tools: `thesvg.search_icons {query}` -> `thesvg.list_variants {slug}` -> `thesvg.get_icon_url
{slug, variant}` (cheap) or `thesvg.get_icon` (returns the raw SVG markup too).
- 154 categories / 7 633 icons; variants include `default`, `mono`, `light`, `dark`, `wordmark`...
- For the reel's dark overlays pick the `light` or `mono` variant (white-on-transparent), which is
  exactly what "logos: transparent PNGs, preferably white versions" wants.
- CDN pattern (tested): `https://cdn.jsdelivr.net/gh/glincker/thesvg@v0.6.0/public/icons/<slug>/<variant>.svg`,
  HEAD-checkable (`image/svg+xml`).
- SVG needs rasterising for the EDL's logo overlays (PNG): QuickLook ships with macOS
  (`qlmanage -t -s 512 -o <dir> icon.svg` -> `icon.svg.png`), or `rsvg-convert`/`inkscape` when
  installed; when the logo exists on Commons, prefer the PNG render route:
  `https://commons.wikimedia.org/wiki/Special:FilePath/<File name>.svg?width=512`.
- Icons of AI/tech brands (openai, github, ...) are covered - check the licence of the specific
  icon before use and note it in `PROJECT/CREDITS.md`.
- If a spoken brand has no icon: fall back to Commons; if it exists nowhere, ask the user.

## 4. Download, verify, prepare

Universal bash recipe (macOS ships curl and shasum):
```bash
# HEAD check - capture content-type AND content-length before any big download
curl -sIL "$URL" | grep -iE "HTTP/|content-type|content-length"
# download - the descriptive UA is required by Wikimedia policy and avoided a tested 429;
# --retry keeps a rate-limited moment from failing the run
curl -L -o "<out>.<ext>" -A "TalkingHeadReel-sourcing/1.0 (contact: project user)" \
     --retry 4 --retry-delay 8 --retry-all-errors "$URL"
# sanity: file size on disk vs the content-length above
ls -l "<out>.<ext>"
# integrity where a hash was published (Commons imageinfo)
shasum -a 1 "<out>.<ext>"
```
- HEAD first, always: buffering a full video download can time out; HEAD does not.
- Pixabay video files land `video/mp4` directly; Commons video lands `.ogv`/`.webm`:
  ```bash
  ffmpeg -y -i in.ogv -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -an out.mp4   # or .webm
  ```
- A photo needing motion: push-in with ffmpeg (`zoompan`), e.g.
  ```bash
  ffmpeg -y -loop 1 -i still.jpg \
    -vf "scale=-2:1080,zoompan=z='min(1.0+0.0009*on,1.12)':d=<seconds*25>:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1080:fps=25" \
    -t <seconds> -r 25 -c:v libx264 -pix_fmt yuv420p -an still_pushin.mp4
  ```
  (adapt `s=` to the target crop; for the top half layouts render 1080x960).
- Keep every prompt/URL with its file: write the source URL inside `PROJECT/CREDITS.md` as you go.

## 5. Preparing clips

- `python3 scripts/clip_sheet.py PROJECT/qa/clips broll/*.mp4` - six frames per clip and the times
  of hard cuts inside it. Choose `t_in` after any hard cut, and `fx` where the subject is.
- Cut-out subjects (for `band` with `front` words, or silhouettes breaking out of a strip):
  `python3 scripts/clip_matte.py broll/x.mp4 matte/x_cut.mov --mode person|subject|largest [--smooth]`
  then `"cutout_matte": "matte/x_cut.mov"` on the clip.
- Coloured figures on a B&W clip: `--mode colorful` (or `person`), then
  `"color_figures_matte": "matte/x_figs.mov"`.
- Logos: transparent PNGs, preferably white versions, in `PROJECT/logos/` - source them through
  the thesvg MCP / Commons routes in section 3.3 and record the licence in `PROJECT/CREDITS.md`.

## 6. Swapping clips later

When the user wants different footage for one shot, change only that clip in a new EDL version
(`edl-schema.md`, "Swapping clips"), check the beat with `--stills`, then render. To revert a swap,
put the old `src` / `t_in` / `speed` back.

---

## Appendix A - paid generation with Seedance via Higgsfield (ONLY on explicit request)

Do not open this appendix unless the user explicitly asks for AI-generated shots and approves the
credit cost. When they do, this is the historical, battle-tested procedure.

If a Higgsfield connector is available (tools such as `generate_video`, `generate_video_batch`,
`media_upload`, `media_confirm`, `jobs_wait`), Seedance 2.5 (`seedance_2_5`) works well:

- **Text-to-video** (`mode: "t2v"`, `aspect_ratio: "9:16"` or `"1:1"`, `duration` 4-15,
  `resolution: "1080p"`, `generate_audio: false`, `bitrate_mode: "high"`): describe the whole shot in
  words (appendix B). This is the default for new footage.
- **Video edit** (`mode: "video_edit"`, the reference clip as `video_references`): re-makes a
  reference clip with new people/wardrobe while keeping camera and motion. Only for footage the
  user has the rights to restyle (their own clips, licensed stock).
- Before a big batch, ask for the cost with `get_cost: true` and tell the user.
- Uploading a local file: `media_upload` returns a presigned URL; PUT the bytes with curl and the
  headers `Content-Type: video/mp4` **and** `If-None-Match: *` (the URL is signed for it - without it
  the upload fails), then `media_confirm`. References must be 2-30 s long; slow a shorter clip down
  (ffmpeg `setpts`) before uploading.
- Batch independent shots with `generate_video_batch` (up to 12) and poll with `jobs_wait`.
- `ip_detected` means the reference or the prompt was recognised as a protected film/person/
  character. Do not try to get around it - write an original shot from words instead (t2v), with
  people and designs that do not resemble any real actor or famous character.
- Check every result: a face that resembles a real celebrity, readable text or logos in the frame,
  or a famous costume = regenerate with a more specific, different description (face shape, hair,
  age, distinctive details). For readable signs, a short "local fix" video edit of the result
  ("replace the lettering with neon shapes, change nothing else") usually works.
- Seedance changes clip length: outputs come back ~3.7-5 s, and a video edit of a short reference
  is stretched evenly in time. Measure the result (ffmpeg) and set `t_in`/`dur` accordingly; when a
  re-made shot replaces the original in the EDL, set `"speed": new_duration / old_duration` and
  scale `t_in` by the same factor so the motion stays in sync (`edl-schema.md`, "Swapping clips").
  1:1 outputs come back 1440x1440.
- Download results into `PROJECT/broll/` (keep the prompt next to them) - the EDL points at local
  files only.
- Generated shots are in colour; the renderer turns them B&W unless `"color": true`.

## Appendix B - prompt template for generated shots (appendix A material)

Long, structured prompts give far more control than one-liners. Write them in English:

```
<SHOT TITLE> - SEEDANCE TEXT-TO-VIDEO

FORMAT
9:16 vertical, 1080p, 5 seconds, ONE continuous shot, no cuts. Ultra-realistic cinematic film frame shot on 35 mm,
not illustration, not a game render, not CGI-looking. No text of any kind: no captions, signs, logos, watermarks, numbers.

THE ONE TRICK
One or two sentences: the single idea the viewer must read in one glance.

RULE A - FRAMING
Exact crop (from where to where), where the subject sits in the frame, camera height, lens feel,
which way the subject faces and where the eyes look ("draw a line from the eyes - it leaves the frame on the left").
IF <checkable failure>; IF <...>, THE VIDEO IS WRONG AND UNUSABLE. HARD FAILURE CONDITION.

RULE B - ACTION, SECOND BY SECOND
0-1 s: ... / 1-2 s: ... / 2-3 s: ... / 3-5 s: ...
Camera: what it does (slow push 5 %, handheld float) and what it never does (no pan, no cut, no zoom snap).

RULE C - PEOPLE (unknown faces, nobody famous)
Age, build, skin, face shape, hair, distinctive details (a mole, a scar, a moustache), expression described as
muscles ("only one corner of the mouth rises", "upper lids relaxed, no white above the iris").
IF THEY LOOK LIKE ANY REAL ACTOR OR PUBLIC FIGURE, THE VIDEO IS WRONG AND UNUSABLE. HARD FAILURE CONDITION.

RULE D - WARDROBE AND PROPS
Exact garments and colours, what must NOT appear (uniforms, badges, logos, famous costumes).

RULE E - PLACE, FOCUS, LIGHT
Setting; what is sharp and what is soft; key light direction and quality; tonal separation if the shot
will be converted to black-and-white.

LOOK
Organic 35 mm grain, soft highlight roll-off, slightly lifted blacks, gentle halation, natural skin with pores.
IF IT LOOKS LIKE CLEAN DIGITAL VIDEO, HDR, OVER-SHARPENED OR AI-SMOOTH, THE VIDEO IS WRONG AND UNUSABLE.

COUNT
ONE man, ONE hand (five fingers), ZERO other people, ZERO text.

BANS
Layout / Camera / Identity / Wardrobe / Text / Style / Anatomy - one line each.
```

Why this shape works: the model follows concrete, checkable statements ("the ear on the
frame-right side is visible") much better than adjectives, and the explicit failure conditions
stop the most common drifts (famous lookalikes, text in frame, plastic skin, extra cuts).

Keep each prompt in `PROJECT/broll/prompts/<shot>.txt` - never overwrite a prompt, write `_v2`,
`_v3` so the user can compare.
