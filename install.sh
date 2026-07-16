#!/usr/bin/env sh
# newsline · local installer — installs from THIS folder onto your PATH.
# No GitHub / network needed. Idempotent (safe to re-run).
#
#   ./install.sh                      -> ~/.local/{share,bin}
#   NEWSLINE_PREFIX=/custom ./install.sh
#
# After install:  newsline init
set -eu

SRC="$(cd "$(dirname "$0")" && pwd -P)"          # the plugin/ dir (newsline + helpers)
PREFIX="${NEWSLINE_PREFIX:-$HOME/.local}"
SHARE="$PREFIX/share/newsline"
BIN="$PREFIX/bin"

command -v python3 >/dev/null 2>&1 || { echo "✗ newsline needs python3 (not found)"; exit 1; }

mkdir -p "$SHARE" "$BIN"
for f in newsline statusline.sh refresh.sh fetch.py resolve.py feeds.json; do
  cp "$SRC/$f" "$SHARE/$f"
done
chmod +x "$SHARE/newsline" "$SHARE/statusline.sh" "$SHARE/refresh.sh"
ln -sf "$SHARE/newsline" "$BIN/newsline"

echo "✔ installed: $BIN/newsline -> $SHARE/newsline"
case ":$PATH:" in
  *":$BIN:"*) ;;
  *) echo "⚠ $BIN is not on PATH. Add to your shell rc:";
     echo "    export PATH=\"$BIN:\$PATH\"" ;;
esac
echo "next:  newsline init"
