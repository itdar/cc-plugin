# newsline · plugin (local)

A Claude Code status-line utility that shows one **regional-language news headline**
at the bottom of your session. Everything runs **locally on your machine**:
locale detection, feed fetch, parsing, caching, rendering. No account, no login,
no code/prompt access.

## How it works

```
statusline.sh   fast path — prints cached headline instantly (never blocks)
   └─ (stale?) → refresh.sh   background — fetch RSS, parse, write cache
                    └─ fetch.py   stdlib-only fetch/parse → OSC 8 link
feeds.json      locale → keyless public RSS (Google News), no API key
```

- Detects language from macOS `AppleLocale` / `$LANG` **locally** (no IP geolocation).
- **Server-first (optional):** if `NEWSLINE_API` is set, `resolve.py` asks your
  curation API which feeds to use, sending only coarse context (lang, country,
  localtime, dow, tz) — no personal data. On any failure/offline/timeout it falls
  back to the bundled `feeds.json`. Unset `NEWSLINE_API` → pure local, unchanged.
- Pulls a **keyless** feed for that locale directly from the source. `feeds.json`
  lists several per locale (national outlet first, Google News fallback); the
  first that yields items wins, so a dead/blocked feed is skipped. RSS **and**
  Atom are supported.
- Caches the top `NEWSLINE_COUNT` (default 5) headlines and **rotates** through
  them, showing a new one every `NEWSLINE_ROTATE` (default 8) seconds — a ticker
  with zero stored state.
- Renders each headline as a clickable [OSC 8] terminal hyperlink.
- Caches for `NEWSLINE_TTL` (default 900s) and refreshes in the background, so the
  status line is always instant and survives feed outages (stale-tolerant).

### Environment knobs

| Var | Default | Meaning |
|-----|---------|---------|
| `NEWSLINE_LANG` | _(auto)_ | force locale, e.g. `ko`/`ja`/`en`. Auto-detect order: this > macOS `AppleLocale` (system region) > `LC_ALL`/`LC_MESSAGES`/`LANG` > `en` |
| `NEWSLINE_MAXLEN` | `100` | max headline chars before truncation with `…` |
| `NEWSLINE_ENDPOINT` | `https://go.example.com/r` | redirect wrapper for click links |
| `NEWSLINE_COUNT` | `5` | headlines cached for rotation |
| `NEWSLINE_ROTATE` | `8` | seconds each headline stays up |
| `NEWSLINE_TTL` | `900` | cache age (s) before a background refresh |
| `NEWSLINE_CACHE` | `~/.cache/newsline` | cache directory |
| `NEWSLINE_FEEDS` | `./feeds.json` | bundled feed map (fallback source) |
| `NEWSLINE_API` | _(none)_ | curation API base; server-first feed selection, local fallback on any failure |
| `NEWSLINE_API_TIMEOUT` | `2` | seconds to wait for the curation API before falling back |

## Install

1. `chmod +x statusline.sh refresh.sh`
2. Merge `settings.snippet.json` into `~/.claude/settings.json` (fix the absolute path).
3. New Claude Code session → headline appears at the bottom.

Requires `python3` (uses stdlib `urllib` — no `curl`, no dependencies).

## Test it standalone

```sh
# force a fetch, then see the rendered line
NEWSLINE_ENDPOINT=http://localhost:8787/r ./refresh.sh && cat ~/.cache/newsline/line; echo
# simulate what Claude Code runs each refresh
./statusline.sh; echo
```

## The click link (and monetization)

Headlines link through a redirect wrapper (`NEWSLINE_ENDPOINT`, default
`https://go.example.com/r`), **not** straight to the article. On day one that
wrapper just forwards you to the real article. This indirection is what lets the
project later route clicks through affiliate links **without changing anything you
have installed** — see `../server/`.

## Disclosure (ship this, from day one)

> newsline shows public news headlines. Clicks pass through our redirect
> (`go.example.com`) so we can measure engagement and, in the future, use
> affiliate links to fund the project. We never read your code, prompts, files,
> or Claude conversations. Locale is detected locally from your system settings.
> Feeds are fetched directly from public sources.

Being upfront on day one avoids the bait-and-switch trust problem that sinks
adware-style tools with developer audiences.

[OSC 8]: https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
