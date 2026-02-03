#!/bin/bash
# Quick setup script for IRC Topic Bot on LXC container
# Run this on pm01 after creating the LXC container

set -e

LXC_ID="${1:-1064}"
LXC_NAME="irc-bot"

echo "=== IRC Topic Bot - LXC Setup Script ==="
echo "Container ID: ${LXC_ID}"
echo "Container Name: ${LXC_NAME}"
echo ""

# Check if running on pm01
if ! command -v pct &> /dev/null; then
    echo "Error: This script must be run on pm01 (Proxmox host)"
    exit 1
fi

# Check if container exists
if ! pct status ${LXC_ID} &> /dev/null; then
    echo "Error: Container ${LXC_ID} does not exist"
    echo ""
    echo "Create it first with:"
    echo "  pct create ${LXC_ID} local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \\"
    echo "    --hostname ${LXC_NAME} --cores 1 --memory 512 --swap 512 \\"
    echo "    --storage local-lvm --rootfs local-lvm:8 \\"
    echo "    --net0 name=eth0,bridge=vmbr0,ip=dhcp --password --unprivileged 1"
    exit 1
fi

# Start container if not running
echo "Starting container..."
pct start ${LXC_ID} 2>/dev/null || true
sleep 5

# Update system
echo "Updating system packages..."
pct exec ${LXC_ID} -- bash -c "apt update && apt upgrade -y"

# Install Docker
echo "Installing Docker..."
pct exec ${LXC_ID} -- bash -c "apt install -y docker.io docker-compose"
pct exec ${LXC_ID} -- systemctl enable docker
pct exec ${LXC_ID} -- systemctl start docker

# Create directory
echo "Creating bot directory..."
pct exec ${LXC_ID} -- mkdir -p /opt/irc-topic-bot

# Copy files to container (assumes files are in current directory)
echo "Copying bot files..."
for file in bot.py requirements.txt Dockerfile docker-compose.yml .env.example README.md; do
    if [ -f "$file" ]; then
        pct push ${LXC_ID} "$file" "/opt/irc-topic-bot/$file"
    fi
done

# Set execute permissions
pct exec ${LXC_ID} -- chmod +x /opt/irc-topic-bot/bot.py

# Copy .env.example to .env
pct exec ${LXC_ID} -- cp /opt/irc-topic-bot/.env.example /opt/irc-topic-bot/.env

# Set container to auto-start
echo "Setting container to auto-start on boot..."
pct set ${LXC_ID} --onboot 1

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Enter container: pct enter ${LXC_ID}"
echo "2. Configure bot: nano /opt/irc-topic-bot/.env"
echo "3. Start bot: cd /opt/irc-topic-bot && docker-compose up -d"
echo "4. View logs: docker-compose logs -f"
echo ""
echo "Container IP: $(pct exec ${LXC_ID} -- hostname -I | awk '{print $1}')"
echo ""
