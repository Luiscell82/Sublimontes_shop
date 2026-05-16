#!/bin/bash
set -euo pipefail

# Only run in remote (cloud) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install agent-browser globally if not already installed
if ! command -v agent-browser &>/dev/null; then
  npm install -g agent-browser
fi

# Set up Chromium for agent-browser using the pre-installed Playwright binary
CHROME_CACHE_DIR="$HOME/.agent-browser/browsers/chrome-linux"
PLAYWRIGHT_CHROME="/opt/pw-browsers/chromium-1194/chrome-linux"

if [ ! -f "$CHROME_CACHE_DIR/chrome" ]; then
  mkdir -p "$CHROME_CACHE_DIR"
  cp -r "$PLAYWRIGHT_CHROME/." "$CHROME_CACHE_DIR/"
fi
