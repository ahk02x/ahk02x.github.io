#!/usr/bin/env python3
"""Screenshot the built site, so a design change can be reviewed as pictures and not as a diff.

    python3 tools/build.py && python3 tools/shots.py            # the six sections, light, desktop
    python3 tools/shots.py --dark --mobile                      # same pages, dark, 390px wide
    python3 tools/shots.py --pages /infra.html,/writing/ --out /tmp/shots

Serves `_site/` on a free port with the stdlib server and drives headless Chrome. No dependencies.
Chrome writes the whole scrolled page, so a shot shows the section rhythm, not just the fold.
"""
import argparse, http.server, os, shutil, socket, socketserver, subprocess, sys, threading

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
SITE = os.path.join(ROOT, '_site')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
MIN_WINDOW = 500  # headless Chrome clamps the window here; narrower shots go through an iframe
PAGES = ['/', '/about.html', '/projects/', '/infra.html', '/writing/', '/ask/', '/sq/']


def serve(directory):
    """A background server on a free port. Returns (port, shutdown)."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=directory, **kw)

        def log_message(self, *a):
            pass

    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return port, httpd.shutdown


def themed_copy(src, theme):
    """A throwaway copy of the site with one theme chosen, the way the toggle chooses it.

    Both themes are stamped, never left to the renderer: headless Chrome follows the host's own
    appearance setting, so on a dark Mac an unstamped run silently grades the dark theme twice.
    Chrome's --force-dark-mode is no use either: it repaints the page and would grade Chrome's
    filter instead of this site's palette. data-theme is exactly what the toggle sets.
    """
    dest = f'{src}.{theme}'
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)
    for folder, _, files in os.walk(dest):
        for f in files:
            if f.endswith('.html'):
                p = os.path.join(folder, f)
                with open(p, encoding='utf-8') as fh:
                    html = fh.read()
                with open(p, 'w', encoding='utf-8') as fh:
                    fh.write(html.replace('<html lang="en">', f'<html lang="en" data-theme="{theme}">', 1))
    return dest


def name_for(path, theme, width):
    stem = (path.strip('/').replace('/', '-') or 'home').removesuffix('.html')
    return f'{stem}-{theme}-{width}.png'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pages', default=','.join(PAGES), help='comma-separated site paths')
    ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'shots'))
    ap.add_argument('--width', type=int, default=1440)
    ap.add_argument('--height', type=int, default=1400)
    ap.add_argument('--mobile', action='store_true', help='390px wide, the phone check')
    ap.add_argument('--dark', action='store_true', help='render the dark theme')
    ap.add_argument('--both-themes', action='store_true')
    ap.add_argument('--frame-height', type=int, default=3200, help='how much of a narrow page to capture')
    args = ap.parse_args()

    if not os.path.isdir(SITE):
        sys.exit('no _site/ — run python3 tools/build.py first')
    if not os.path.exists(CHROME):
        sys.exit(f'Chrome not found at {CHROME}')
    width = 390 if args.mobile else args.width
    height = 1000 if args.mobile else args.height
    themes = ['light', 'dark'] if args.both_themes else ['dark' if args.dark else 'light']

    os.makedirs(args.out, exist_ok=True)
    written = []
    for theme in themes:
        root = themed_copy(SITE, theme)
        port, shutdown = serve(root)
        try:
            for path in [p for p in args.pages.split(',') if p]:
                out = os.path.join(args.out, name_for(path, theme, width))
                target, win_w = path, width
                if width < MIN_WINDOW:
                    # Headless Chrome will not open a window narrower than about 500px, so a 390px
                    # "phone" shot is really a 500px layout with the right-hand side cropped off —
                    # which reads exactly like a page overflowing sideways. Put the page in an iframe
                    # of the real width instead: the frame is its own viewport, so the media queries
                    # fire where a phone fires them, and the shot shows the layout that ships.
                    frame = os.path.join(root, '__shot_frame.html')
                    with open(frame, 'w', encoding='utf-8') as fh:
                        fh.write('<!doctype html><meta charset="utf-8">'
                                 '<style>html,body{margin:0;background:#888}'
                                 f'iframe{{width:{width}px;height:{args.frame_height}px;border:0;display:block}}</style>'
                                 f'<iframe src="{path}" title="narrow preview"></iframe>')
                    target, win_w = '/__shot_frame.html', MIN_WINDOW
                cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                       '--no-first-run', '--no-default-browser-check',
                       f'--window-size={win_w},{height}', f'--screenshot={out}',
                       '--virtual-time-budget=2500', f'http://127.0.0.1:{port}{target}']
                r = subprocess.run(cmd, capture_output=True, text=True)
                if os.path.exists(out):
                    written.append(out)
                else:
                    print(f'FAILED {path} ({theme}): {r.stderr.strip()[:200]}', file=sys.stderr)
        finally:
            shutdown()
            if root != SITE:
                shutil.rmtree(root, ignore_errors=True)
    for p in written:
        print(p)
    print(f'{len(written)} shot(s) in {args.out}')


if __name__ == '__main__':
    main()
