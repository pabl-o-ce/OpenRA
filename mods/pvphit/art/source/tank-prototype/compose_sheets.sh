#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
for layer in body turret; do
  frames=("$layer"/*.png)
  if [[ ${#frames[@]} -ne 32 ]]; then
    printf 'Expected 32 frames for %s; found %s\n' "$layer" "${#frames[@]}" >&2
    exit 1
  fi
  magick montage "${frames[@]}" -background none -tile 8x4 -geometry 128x128+0+0 "$layer-sheet.png"
done
magick montage assembled/*.png -background '#111b24' -tile 4x2 -geometry 128x128+16+16 directions-preview.png
