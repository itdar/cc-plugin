#!/usr/bin/env python3
"""newsline · fetch + parse (stdlib only).

Reads a locale-appropriate keyless feed on the USER'S machine, extracts the top
N headlines, and prints one ready-to-render status line PER headline (newline
separated). Each line is an OSC 8 terminal hyperlink whose target is the redirect
wrapper, so the click destination can be swapped to an affiliate URL later,
server-side, with no plugin change.

Handles both RSS (<channel><item>) and Atom (<feed><entry>).

Usage: fetch.py <lang> <feeds.json> <endpoint> [count]
Exits non-zero on failure so refresh.sh keeps the previous cache.
"""
import os
import re
import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

TIMEOUT = 5
MAX_TITLE = int(os.environ.get("NEWSLINE_MAXLEN") or 100)  # headline truncation
ATOM = "{http://www.w3.org/2005/Atom}"
_ws = re.compile(r"\s+")


def clean(title):
    return _ws.sub(" ", title).strip()


def parse_items(data):
    """Return [(title, link), ...] from an RSS or Atom document."""
    out = []
    root = ET.fromstring(data)

    # RSS
    for it in root.findall(".//channel/item"):
        t = clean(it.findtext("title") or "")
        l = (it.findtext("link") or "").strip()
        if t and l:
            out.append((t, l))
    if out:
        return out

    # Atom
    for e in root.findall(f".//{ATOM}entry"):
        t = clean(e.findtext(f"{ATOM}title") or "")
        link = ""
        for ln in e.findall(f"{ATOM}link"):
            if ln.get("rel", "alternate") in ("alternate", ""):
                link = ln.get("href", "").strip()
                break
        if t and link:
            out.append((t, link))
    return out


def top_headlines(urls, count):
    """First feed that yields items wins; return up to `count` unique ones."""
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "newsline/0.1"})
            data = urllib.request.urlopen(req, timeout=TIMEOUT).read()
            items = parse_items(data)
        except Exception:
            continue
        seen, picked = set(), []
        for title, link in items:
            key = title.lower()
            if key in seen:
                continue
            seen.add(key)
            picked.append((title, link))
            if len(picked) >= count:
                break
        if picked:
            return picked
    return []


def osc8(url, text):
    esc = "\x1b"  # ESC]8;;URL ESC\  TEXT  ESC]8;;ESC\
    return f"{esc}]8;;{url}{esc}\\{text}{esc}]8;;{esc}\\"


def render(title, link, endpoint, lang):
    wrapped = endpoint + "?" + urllib.parse.urlencode({"u": link, "c": lang})
    if len(title) > MAX_TITLE:
        title = title[: MAX_TITLE - 1] + "…"
    return osc8(wrapped, f"\U0001F4F0 {title}")


def main():
    if len(sys.argv) < 4:
        return 2
    lang, feeds_path, endpoint = sys.argv[1], sys.argv[2], sys.argv[3]
    count = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    with open(feeds_path, encoding="utf-8") as f:
        feeds = json.load(f)
    urls = feeds.get(lang) or feeds.get("default") or []
    if not urls:
        return 1

    picked = top_headlines(urls, count)
    if not picked:
        return 1

    for title, link in picked:
        sys.stdout.write(render(title, link, endpoint, lang) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
