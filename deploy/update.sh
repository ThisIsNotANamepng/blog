#!/bin/sh
# Runs on the VPS from cron. Pulls the newest image from Docker Hub and, if it
# differs from what's running, replaces the container. Nothing on GitHub needs
# access to the VPS.
#
# Install (rootful podman, so it all runs from root's crontab):
#   sudo mkdir -p /opt/personal-website
#   sudo cp update.sh /opt/personal-website/ && sudo chmod +x /opt/personal-website/update.sh
#   sudo systemctl enable --now podman-restart.service   # start the site after a reboot
#   sudo crontab -e
#   */10 * * * * flock -n /tmp/personal-website-update.lock /opt/personal-website/update.sh >> /root/personal-website-update.log 2>&1
set -eu

# Fully qualified: podman won't guess a registry for a short name without a TTY
IMAGE="docker.io/ilikecontainers/personal-website:latest"
NAME="personal-website"

# The app listens on 5000 inside the container and reads /stats.txt at startup.
# Bound to localhost only: Caddy is the public entry point, and published
# container ports go around ufw.
run_container() {
    podman run -d \
        --name "$NAME" \
        --restart always \
        -p 127.0.0.1:5000:5000 \
        -v /stats.txt:/stats.txt:ro \
        "$IMAGE"
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*"
}

if ! podman pull -q "$IMAGE" >/dev/null; then
    log "pull failed, leaving the current container running"
    exit 1
fi

latest=$(podman image inspect -f '{{.Id}}' "$IMAGE")
# Empty if the container is missing or stopped, so those get fixed too
running=$(podman inspect -f '{{if .State.Running}}{{.Image}}{{end}}' "$NAME" 2>/dev/null || true)

if [ "$latest" = "$running" ]; then
    exit 0
fi

log "deploying $latest"
podman rm -f "$NAME" >/dev/null 2>&1 || true
run_container >/dev/null
# Drop the now-untagged previous image so the disk doesn't fill up
podman image prune -f >/dev/null
log "deployed"
