#!/usr/bin/env bash
# Deploy an image to the local Docker host with a health check and automatic rollback.
# Usage: deploy.sh <image-reference>   (preferably pinned by digest)
set -euo pipefail

IMAGE_REF="${1:?usage: deploy.sh <image-reference>}"
NAME="${CONTAINER_NAME:-todo-prod}"
PORT="${HOST_PORT:-8080}"
TIMEOUT="${HEALTH_TIMEOUT:-30}"
PREV_TAG="devsecops-todo:previous"

start() {
  docker run -d --name "$NAME" \
    -p "127.0.0.1:${PORT}:5000" \
    --restart unless-stopped \
    --read-only --tmpfs /tmp \
    --cap-drop ALL --security-opt no-new-privileges:true \
    "$1" >/dev/null
}

healthy() {
  for _ in $(seq 1 "$TIMEOUT"); do
    if curl -fsS "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

had_previous=false
if docker inspect "$NAME" >/dev/null 2>&1; then
  docker tag "$(docker inspect -f '{{.Image}}' "$NAME")" "$PREV_TAG"
  had_previous=true
fi

docker pull "$IMAGE_REF"
docker rm -f "$NAME" >/dev/null 2>&1 || true
start "$IMAGE_REF"

if healthy; then
  echo "DEPLOY OK: ${IMAGE_REF} is healthy on 127.0.0.1:${PORT}"
  exit 0
fi

echo "HEALTH CHECK FAILED for ${IMAGE_REF}" >&2
docker logs "$NAME" 2>&1 | tail -n 30 || true
docker rm -f "$NAME" >/dev/null 2>&1 || true

if [ "$had_previous" = true ]; then
  echo "Rolling back to the previous version..." >&2
  start "$PREV_TAG"
  if healthy; then
    echo "ROLLBACK OK: previous version is healthy again" >&2
  else
    echo "ROLLBACK FAILED: previous version is not healthy" >&2
  fi
else
  echo "No previous version to roll back to." >&2
fi
exit 1
