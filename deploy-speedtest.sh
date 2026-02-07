#!/bin/bash
# Deploy speedtest server to existing irc-bot container
# Run this from pm01

set -e

LXC_ID="${1:-1064}"

echo "=== Deploying Speedtest Server ==="
echo "Container ID: ${LXC_ID}"
echo ""

# Check if running on pm01
if ! command -v pct &> /dev/null; then
    echo "Error: This script must be run on pm01 (Proxmox host)"
    echo ""
    echo "Copy this script to pm01 and run it there:"
    echo "  scp deploy-speedtest.sh pm01:/tmp/"
    echo "  ssh pm01"
    echo "  cd /path/to/irc-topic-bot"
    echo "  bash /tmp/deploy-speedtest.sh"
    exit 1
fi

# Push new files
echo "Pushing speedtest_server.py..."
pct push ${LXC_ID} speedtest_server.py /opt/irc-topic-bot/speedtest_server.py

echo "Pushing updated Dockerfile..."
pct push ${LXC_ID} Dockerfile /opt/irc-topic-bot/Dockerfile

echo "Pushing updated docker-compose.yml..."
pct push ${LXC_ID} docker-compose.yml /opt/irc-topic-bot/docker-compose.yml

# Rebuild and restart
echo ""
echo "Rebuilding containers..."
pct exec ${LXC_ID} -- bash -c "cd /opt/irc-topic-bot && docker-compose down"
pct exec ${LXC_ID} -- bash -c "cd /opt/irc-topic-bot && docker-compose build"
pct exec ${LXC_ID} -- bash -c "cd /opt/irc-topic-bot && docker-compose up -d"

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Check logs with:"
echo "  pct exec ${LXC_ID} -- docker-compose -f /opt/irc-topic-bot/docker-compose.yml logs -f speedtest-server"
echo ""
echo "Test endpoint:"
echo "  curl http://10.200.200.213:8888/speedtest"
echo ""
