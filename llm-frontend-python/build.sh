#!/usr/bin/env bash
set -euo pipefail

: "${GHCR_OWNER:?Set GHCR_OWNER to your GitHub username or organization}"
owner="$(printf '%s' "$GHCR_OWNER" | tr '[:upper:]' '[:lower:]')"
image="ghcr.io/${owner}/llmapp09-llm-frontend-python:latest"

docker build --platform linux/arm64 -t "$image" .
docker push "$image"