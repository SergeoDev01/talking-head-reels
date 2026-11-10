#!/usr/bin/env python3
"""Check everything the talking-head-reels pipeline needs and print how to fix what is missing.

Run it with the Python you will use for the other scripts:
    python3 scripts/check_setup.py
"""
import importlib
import os
import platform
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SKILL_DIR, ffmpeg_candidates, ffmpeg_has_ass  # noqa: E402

OK, WARN, BAD = 'ok  ', 'warn', 'MISS'
problems = []

VENV_FIX = ('python3 -m venv ~/.venvs/reels && ~/.venvs/reels/bin/pip install numpy faster-whisper imageio-ffmpeg  '
            '(then run every script with ~/.venvs/reels/bin/python)')


def line(state, what, fix=''):
    print('[%s] %s' % (state, what))
    if state != OK and fix:
        print('       -> ' + fix)
        problems.append((state, what))


def main():
    print('talking-head-reels setup check\n')
    if platform.system() == 'Darwin':
        line(OK, 'macOS %s' % platform.mac_ver()[0])
    else:
        line(OK, '%s host - the render engine is platform-neutral (ffmpeg + libass); Didot and Helvetica Neue are'
                 ' replaced by the free substitutes bundled in assets/fonts/win (Playfair Display + Inter, OFL)' % platform.system())

    v = sys.version_info
    line(OK if v >= (3, 9) else BAD, 'Python %d.%d (%s)' % (v.major, v.minor, sys.executable), 'use Python 3.9 or newer')

    for mod, pipname, why in (('numpy', 'numpy', 'compositing every frame, audio analysis, mattes'),
                              ('faster_whisper', 'faster-whisper', 'word-level transcription')):
        try:
            importlib.import_module(mod)
            line(OK, '%s (%s)' % (pipname, why))
        except Exception:
            line(BAD, '%s (%s)' % (pipname, why), VENV_FIX)

    cands = ffmpeg_candidates()
    if not cands:
        line(BAD, 'ffmpeg (not found)', 'brew install ffmpeg   or   pip install imageio-ffmpeg   (or set $FFMPEG)')
    else:
        with_ass = [c for c in cands if ffmpeg_has_ass(c)]
        if with_ass:
            line(OK, 'ffmpeg with libass (%s)' % with_ass[0])
        else:
            line(BAD, 'ffmpeg without the libass "ass" filter (%s) - all on-screen text is drawn with it' % ', '.join(cands),
                 'brew install ffmpeg   (Homebrew builds include libass)   or   pip install imageio-ffmpeg')

    fonts = {
        'Anton (bundled)': os.path.join(SKILL_DIR, 'assets', 'fonts', 'Anton-Regular.ttf'),
    }
    if platform.system() == 'Darwin':
        fonts['Didot / Didot Bold'] = '/System/Library/Fonts/Supplemental/Didot.ttc'
        fonts['Helvetica Neue'] = '/System/Library/Fonts/HelveticaNeue.ttc'
        for name, path in fonts.items():
            line(OK if os.path.exists(path) else BAD, 'font %s' % name,
                 'missing %s - %s' % (path, 're-download the skill' if 'bundled' in name else 'it ships with macOS; restore it in Font Book'))
    else:
        wdir = os.path.join(SKILL_DIR, 'assets', 'fonts', 'win')
        try:
            bundled = [f for f in os.listdir(wdir) if f.lower().endswith(('.ttf', '.otf'))]
        except OSError:
            bundled = []
        if len(bundled) >= 4:
            line(OK, 'substitute fonts bundled (assets/fonts/win: %s)' % ', '.join(sorted(bundled)))
        else:
            line(BAD, 'substitute fonts bundled (assets/fonts/win has %d file(s), 4 expected: Playfair Display 400/700/italic + Inter Medium)'
                      % len(bundled),
                 're-install the skill - the fonts are in assets/fonts/win/ (OFL licensed)')
        extr = [p for p in os.environ.get('REEL_FONT_FILES', '').split(os.pathsep) if p]
        if extr:
            for p in extr:
                line(OK if os.path.exists(p) else BAD, 'REEL_FONT_FILES -> %s' % os.path.basename(p),
                     'missing %s - fix the user env var REEL_FONT_FILES' % p)
        else:
            line(WARN, 'REEL_FONT_FILES env var not set',
                 'set it once per user to the four .ttf files in assets/fonts/win (see SKILL.md - Windows)')

    swiftc = shutil.which('swiftc')
    line(OK if swiftc else WARN, 'swiftc - Apple Vision matte tools (cut-outs, silhouettes, words behind the head)',
         'xcode-select --install   (optional: without it the edit simply skips cut-out effects)')

    print()
    if not problems:
        print('All good.')
    else:
        print('%d item(s) need attention (see -> lines above).' % len(problems))
    return 0 if not any(s == BAD for s, _ in problems) else 2


if __name__ == '__main__':
    sys.exit(main())
