#!/usr/bin/env bash
set -euxo pipefail

# Step 1: Build the SVG file from the drawio file
docker run --rm -v "$(pwd)":/pwd rlespinasse/drawio-desktop-headless -x --embed-svg-images -t -f svg -o /pwd/architecture-orig.svg /pwd/architecture.drawio

# Step 2: Inject the darkmode CSS into the SVG file
awk 'BEGIN{getline l < "darkmode-style-injection.txt"}/<defs\/>/{gsub("<defs/>",l)}1' architecture-orig.svg > architecture.svg
