#!/usr/bin/env bash
# Assembles dist/: the exact set of files that should be public.
# An explicit allowlist, so repo tooling can never leak onto the site by accident.
# There is no build step for development: serve the repo root directly.
#
#   python3 -m http.server 8000     # then open http://localhost:8000
#
# index.html and assets/world.svg are GENERATED and COMMITTED, by
# tools/build-page.py and tools/build-map.py. Deploys ship exactly what the
# repository holds; this script never regenerates them.
#
# There is no functions/ directory: the waitlist posts to api.findsyou.work,
# a separate worker (FindsYou-Work/waitlist-backend). Deploy from the repo root:
#     ./tools/build-dist.sh && npx wrangler pages deploy dist --project-name=findsyou
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf dist
mkdir -p dist

for f in index.html 404.html robots.txt sitemap.xml llms.txt site.webmanifest _headers _redirects; do
  cp "$f" dist/
done
for d in assets .well-known; do
  cp -R "$d" "dist/$d"
done
find dist -name '.DS_Store' -delete

# world.svg is inlined into index.html at page-build time; it is not requested
# by the browser, so it does not need to ship.
rm -f dist/assets/world.svg

# GitHub-only artwork: the README banner and the org avatar are not part of the
# site, and there is no reason to serve 150KB of them.
rm -f dist/assets/readme-banner.png dist/assets/org-avatar.png

# Cache busting. Asset filenames are not content-hashed in the repo, so a deploy
# alone cannot invalidate a cached CSS/JS file. Stamp each reference with a short
# content hash here; _headers can then cache /assets/*.css and *.js immutably
# because the URL changes when the file does.
hash_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -c1-8
  else shasum -a 256 "$1" | cut -c1-8; fi
}

for f in findsyou.css findsyou.js; do
  h=$(hash_of "dist/assets/$f")
  # `sed -i` is not portable: GNU takes no argument, BSD demands one.
  find dist -name '*.html' | while IFS= read -r page; do
    sed "s|/assets/$f\"|/assets/$f?v=$h\"|g" "$page" > "$page.stamped" && mv "$page.stamped" "$page"
  done
  # A sed that matches nothing exits 0. Fail instead of shipping an immutable
  # asset under a URL that never changes.
  grep -q "/assets/$f?v=$h\"" dist/index.html || { echo "cache stamp for $f did not apply" >&2; exit 1; }
done

echo "dist/ assembled:"
find dist -type f | sed 's|^dist/|  |' | sort
echo "  ($(find dist -type f | wc -l | tr -d ' ') files)"
