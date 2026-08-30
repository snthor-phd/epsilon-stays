#!/usr/bin/env bash
# Rebuild the site and push. GitHub Pages serves from main.
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py

if [[ -z "$(git status --porcelain)" ]]; then
  echo "Nothing to deploy — working tree clean."
  exit 0
fi

git add -A
git commit -m "${1:-Update stays}"
git push origin main
echo "Deployed. https://stays.adventuresinepsilon.com/"
