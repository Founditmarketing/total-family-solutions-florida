#!/usr/bin/env python3
"""Regenerate sitemap.xml from the pages in this repo.

Run from the repo root after adding or removing a page:

    python3 generate-sitemap.py

URL format matches how the site is actually served in production
(see vercel.json: cleanUrls + trailingSlash false):
    locations/miami/index.html  ->  https://www.totalfamilysolutionsfl.com/locations/miami

Anything not listed in PAGES is deliberately excluded -- the HTTrack
redirect stubs (index2fc1.html and friends), the empty xmlrpc files, and
the wp-json / feed dumps carried over from the WordPress export.
"""

import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

BASE = "https://www.totalfamilysolutionsfl.com"

# (path, priority, changefreq) -- ordered as they should appear in the sitemap.
PAGES = [
    ("index.html", "1.0", "monthly"),
    ("locations/index.html", "0.9", "monthly"),
    ("locations/ocala/index.html", "0.8", "monthly"),
    ("locations/orlando/index.html", "0.8", "monthly"),
    ("locations/gainesville/index.html", "0.8", "monthly"),
    ("locations/wildwood-the-villages/index.html", "0.8", "monthly"),
    ("locations/dunnellon/index.html", "0.8", "monthly"),
    ("locations/tampa/index.html", "0.8", "monthly"),
    ("locations/wesley-chapel/index.html", "0.8", "monthly"),
    ("locations/jacksonville/index.html", "0.8", "monthly"),
    ("locations/port-st-lucie/index.html", "0.8", "monthly"),
    ("locations/fort-myers/index.html", "0.8", "monthly"),
    ("locations/miami/index.html", "0.8", "monthly"),
    ("outpatient-telehealth-care/index.html", "0.8", "monthly"),
    ("medication-mgmt-psychiatric-care/index.html", "0.8", "monthly"),
    ("request-appointment/index.html", "0.9", "monthly"),
    ("get-in-touch/index.html", "0.7", "monthly"),
    ("insurance/index.html", "0.7", "monthly"),
    ("groups/index.html", "0.6", "monthly"),
    ("about-us/index.html", "0.6", "monthly"),
    ("employment/index.html", "0.4", "yearly"),
]


def url_for(path):
    """Map a repo file path to its production URL."""
    clean = path[: -len("index.html")].rstrip("/")
    return f"{BASE}/" if not clean else f"{BASE}/{clean}"


def lastmod_for(path):
    """Date of the last commit that touched this file (YYYY-MM-DD)."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", path],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return out or None


def main():
    root = Path(__file__).parent
    missing = [p for p, _, _ in PAGES if not (root / p).is_file()]
    if missing:
        raise SystemExit("Listed in PAGES but not on disk:\n  " + "\n  ".join(missing))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority, changefreq in PAGES:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url_for(path))}</loc>")
        lastmod = lastmod_for(path)
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    (root / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote sitemap.xml with {len(PAGES)} URLs")


if __name__ == "__main__":
    main()
