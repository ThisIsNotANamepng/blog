#!/bin/sh
# Runs on the VPS from cron. Pulls the newest image from Docker Hub and, if it
# differs from what's running, replaces the container. Nothing on GitHub needs
# access to the VPS.
#
# Install:
#   sudo mkdir -p /opt/personal-website
#   sudo cp update.sh /opt/personal-website/ && sudo chmod +x /opt/personal-website/update.sh
#   crontab -e    (as a user that can run docker, or root)
#   */10 * * * * flock -n /tmp/personal-website-update.lock /opt/personal-website/update.sh >> "$HOME/personal-website-update.log" 2>&1
set -eu

IMAGE="ilikecontainers/personal-website:latest"
NAME="personal-website"

# The app listens on 5000 inside the container and reads /stats.txt at startup.
# Bound to localhost only: Caddy is the public entry point, and ports Docker
# publishes on 0.0.0.0 skip ufw entirely.
run_container() {
    docker run -d \
        --name "$NAME" \
        --restart unless-stopped \
        -p 127.0.0.1:5000:5000 \
        -v /stats.txt:/stats.txt:ro \
        "$IMAGE"
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*"
}

if ! docker pull -q "$IMAGE" >/dev/null; then
    log "pull failed, leaving the current container running"
    exit 1
fi

latest=$(docker image inspect -f '{{.Id}}' "$IMAGE")
# Empty if the container is missing or stopped, so those get fixed too
running=$(docker inspect -f '{{if .State.Running}}{{.Image}}{{end}}' "$NAME" 2>/dev/null || true)

if [ "$latest" = "$running" ]; then
    exit 0
fi

log "deploying $latest"
docker rm -f "$NAME" >/dev/null 2>&1 || true
run_container >/dev/null
# Drop the now-untagged previous image so the disk doesn't fill up
docker image prune -f >/dev/null
log "deployed"
