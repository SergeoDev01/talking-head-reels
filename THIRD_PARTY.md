# Third-party components

This repository is MIT-licensed, but it bundles or depends on components that
keep their own licenses. This file lists them. When in doubt, the license file
shipped with the component wins.

## Fonts (bundled)

| File | Font | License | Source |
|---|---|---|---|
| `assets/fonts/Anton-Regular.ttf` | Anton | SIL Open Font License 1.1 | https://github.com/google/fonts/tree/main/ofl/anton |
| `assets/fonts/OFL.txt` | OFL text for Anton | SIL OFL 1.1 | — |
| `assets/fonts/win/PlayfairDisplay_400_normal.ttf` | Playfair Display Regular | SIL OFL 1.1 | https://github.com/google/fonts/tree/main/ofl/playfairdisplay |
| `assets/fonts/win/PlayfairDisplay_400_italic.ttf` | Playfair Display Italic | SIL OFL 1.1 | https://github.com/google/fonts/tree/main/ofl/playfairdisplay |
| `assets/fonts/win/PlayfairDisplay_700_bold.ttf` | Playfair Display Bold | SIL OFL 1.1 | https://github.com/google/fonts/tree/main/ofl/playfairdisplay |
| `assets/fonts/win/Inter_500_normal.ttf` | Inter Medium | SIL OFL 1.1 | https://github.com/rsms/inter |
| `assets/fonts/win/PlayfairDisplay-OFL.txt` | OFL text for Playfair Display | SIL OFL 1.1 | — |
| `assets/fonts/win/Inter-OFL.txt` | OFL text for Inter | SIL OFL 1.1 | — |

macOS system fonts (Didot, Helvetica Neue) are **not** bundled and are not
redistributed. On Windows the free OFL substitutes above are used instead.

## Assets

| File | Origin | License |
|---|---|---|
| `assets/textures/halftone_1080x1920.png` | Bundled halftone texture | MIT, as part of this repository (verify before reuse outside the project) |

## MCP servers and tools (not bundled)

| Component | License | Source |
|---|---|---|
| `pixabay-mcp` | MIT | https://github.com/zym9863/pixabay-mcp |
| `@thesvg/mcp-server` | MIT (code) | https://github.com/glincker/thesvg |
| thesvg icon registry | Brand logos are trademarks of their owners | https://thesvg.org |
| ffmpeg | LGPL 2.1+ / GPL 2+ depending on the build | https://ffmpeg.org/ |
| faster-whisper | MIT | https://github.com/SYSTRAN/faster-whisper |
| numpy | BSD-3-Clause | https://numpy.org/ |
| Python | PSF License | https://www.python.org/ |

## Media sourced at runtime (not in this repository)

| Source | License | Attribution |
|---|---|---|
| Pixabay | Pixabay Content License | Not required |
| Wikimedia Commons | Per-file license (public domain, CC BY, CC BY-SA, …) | Per file — record it in `PROJECT/CREDITS.md` |
| thesvg | Brand logos / trademarks | Identification use; check the brand's rules |

The skill writes a `CREDITS.md` file inside each project. Keep it with the
rendered video, especially for Wikimedia Commons material.
