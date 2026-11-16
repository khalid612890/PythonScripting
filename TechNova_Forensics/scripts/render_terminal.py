#!/usr/bin/env python3
"""Renders saved, unedited tool output files as terminal-style PNG images (Playwright) for the report."""
import sys, html, subprocess, os
from playwright.sync_api import sync_playwright
jobs = [l.split('|', 4) for l in sys.argv[1:]]  # "outfile.png|title|file|maxlines|grep"
with sync_playwright() as p:
    import glob; b = p.chromium.launch(executable_path=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome') or ['/opt/pw-browsers/chromium'])[0]); pg = b.new_page(viewport={'width': 1400, 'height': 400}, device_scale_factor=2)
    for out, title, f, n, g in jobs:
        lines = open(f, errors='replace').read().splitlines()
        lines = [l for l in lines if not l.startswith('Running as user')]
        if g: lines = [lines[0]] + [l for l in lines[1:] if __import__('re').search(g, l)]
        txt = '\n'.join(l[:190] for l in lines[:int(n)])
        pg.set_content(f"<body style='margin:0;background:#1e1e1e'><div style='background:#333;color:#ddd;font:13px sans-serif;padding:6px 10px'>analyst@forensic-vm: {html.escape(title)}</div><pre style='margin:0;padding:10px;color:#e6e6e6;font:12.5px/1.35 DejaVu Sans Mono,monospace;white-space:pre'>{html.escape(txt)}</pre></body>")
        pg.set_viewport_size({'width': 1400, 'height': max(120, pg.evaluate('document.body.scrollHeight'))})
        pg.screenshot(path=out, full_page=True)
    b.close()
