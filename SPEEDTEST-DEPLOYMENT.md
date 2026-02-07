# Speedtest HTTP Server Deployment

This guide covers deploying the speedtest HTTP server alongside the IRC bot in the LXC container on Proxmox.

## Overview

The speedtest server:
- Runs `speedtest-cli --share` every 30 minutes
- Stores the latest speedtest URL
- Serves it via HTTP on port 8888
- Runs in a separate Docker container alongside the IRC bot

## Architecture

```
┌─────────────────────────────────────────┐
│ Proxmox pm01                            │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ LXC Container (ID: 1064)        │   │
│  │ Hostname: irc-bot               │   │
│  │                                 │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │ irc-topic-bot container  │   │   │
│  │  │ (IRC bot)                │   │   │
│  │  └──────────────────────────┘   │   │
│  │                                 │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │ speedtest-server         │   │   │
│  │  │ Port: 8888               │   │   │
│  │  │ Runs speedtest-cli       │   │   │
│  │  │ every 30 minutes         │   │   │
│  │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘

HexChat on laptop → HTTP GET → http://irc-bot:8888/speedtest
                                (or use IP if DNS not set up)
```

## Prerequisites

1. LXC container must be running on Proxmox pm01
2. Docker and Docker Compose installed in container
3. Container must have network access
4. Port 8888 must be accessible from your network

## Deployment Steps

### 1. Push Files to LXC Container

From your laptop:

```bash
cd ~/irc-topic-bot

# Use pct push to copy files to container
sudo pct push 1064 speedtest_server.py /root/irc-topic-bot/speedtest_server.py
sudo pct push 1064 Dockerfile /root/irc-topic-bot/Dockerfile
sudo pct push 1064 docker-compose.yml /root/irc-topic-bot/docker-compose.yml
```

Or use the automated script:

```bash
./setup-lxc.sh
```

### 2. SSH into Container and Deploy

```bash
# SSH into the Proxmox host first
ssh pm01

# Then enter the container
pct enter 1064

# Or SSH directly if container has SSH enabled
ssh root@irc-bot
```

### 3. Build and Start Services

```bash
cd /root/irc-topic-bot

# Stop existing containers
docker-compose down

# Rebuild with new Dockerfile
docker-compose build

# Start both services
docker-compose up -d

# Check logs
docker-compose logs -f speedtest-server
```

Expected output:
```
=== Speedtest HTTP Server ===
Starting at 2026-02-06 13:00:00
HTTP port: 8888
Check interval: 30 minutes
Speedtest command: speedtest-cli --share

[2026-02-06 13:00:00] HTTP server listening on port 8888
[2026-02-06 13:00:00] Endpoints:
  GET /speedtest - Get latest speedtest URL
  GET /status - Server status
  GET /health - Health check

[2026-02-06 13:00:00] Running speedtest...
[2026-02-06 13:00:45] Speedtest complete: http://www.speedtest.net/result/...
```

### 4. Verify It's Working

From your laptop:

```bash
# Test the endpoint (replace with actual container IP or hostname)
curl http://irc-bot:8888/speedtest

# Or use IP address if DNS not configured yet
curl http://10.10.2.XXX:8888/speedtest

# Check status
curl http://irc-bot:8888/status

# Health check
curl http://irc-bot:8888/health
```

Expected response from `/speedtest`:
```
http://www.speedtest.net/result/18812818680.png
```

Expected response from `/status`:
```
Speedtest HTTP Server
Latest URL: http://www.speedtest.net/result/18812818680.png
Age: 5 minutes
Last check: 2026-02-06 13:00:45
Check interval: 30 minutes
```

## Configuration

Environment variables (set in `docker-compose.yml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SPEEDTEST_INTERVAL` | `1800` | Seconds between speedtest runs (1800 = 30 min) |
| `SPEEDTEST_HTTP_PORT` | `8888` | HTTP server port |
| `SPEEDTEST_CMD` | `speedtest-cli --share` | Command to run speedtest |

## Troubleshooting

### Container not accessible

```bash
# Check container is running
docker ps

# Check if port is listening
netstat -tulpn | grep 8888

# Check firewall rules in LXC container
iptables -L -n
```

### Speedtest failing

```bash
# Check logs
docker-compose logs speedtest-server

# Test speedtest manually
docker exec -it speedtest-server speedtest-cli --share

# Check network connectivity
docker exec -it speedtest-server ping -c 3 speedtest.net
```

### No speedtest URL available

```bash
# Check server status
curl http://irc-bot:8888/status

# Force a speedtest by restarting container
docker-compose restart speedtest-server

# Watch logs
docker-compose logs -f speedtest-server
```

## API Endpoints

### GET /speedtest

Returns the latest speedtest URL as plain text.

**Response Headers:**
- `X-Speedtest-Age-Minutes`: Age of the speedtest in minutes
- `X-Speedtest-Timestamp`: Unix timestamp when speedtest was run

**Response Codes:**
- `200 OK`: Speedtest URL available
- `503 Service Unavailable`: No speedtest run yet

### GET /status

Returns detailed status information as plain text.

### GET /health

Simple health check endpoint. Always returns `200 OK` with `OK\n`.

## Integration with HexChat

Update the HexChat plugin to fetch from this endpoint:

```python
# In hexchat_speedtest_queue.py
def run_speedtest():
    """Fetch latest speedtest URL from HTTP server."""
    import urllib.request

    speedtest_url = 'http://irc-bot:8888/speedtest'  # Or use IP

    try:
        with urllib.request.urlopen(speedtest_url, timeout=5) as response:
            if response.status == 200:
                url = response.read().decode('utf-8').strip()
                age = response.headers.get('X-Speedtest-Age-Minutes', 'unknown')
                print(f'[SPEEDTEST] Loaded: {url} (age: {age} minutes)')
                return url
            else:
                print(f'[SPEEDTEST ERROR] HTTP {response.status}')
                return None
    except Exception as e:
        print(f'[SPEEDTEST ERROR] {e}')
        return None
```

## Maintenance

### Update Code

```bash
cd ~/irc-topic-bot

# Pull latest changes
git pull

# Push to container
./setup-lxc.sh

# SSH into container and rebuild
ssh root@irc-bot
cd /root/irc-topic-bot
docker-compose down
docker-compose build
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Just speedtest server
docker-compose logs -f speedtest-server

# Last 100 lines
docker-compose logs --tail=100 speedtest-server
```

### Restart Services

```bash
# Restart just speedtest server
docker-compose restart speedtest-server

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

## DNS Configuration

If you want to use `http://irc-bot:8888/speedtest` instead of IP addresses:

### Option 1: Add to /etc/hosts

On your laptop:

```bash
sudo nano /etc/hosts

# Add line (replace with actual container IP):
10.10.2.XXX    irc-bot
```

### Option 2: Add to Firewalla DNS

Follow the Tower of Omens DNS setup guide to add a DNS record for the irc-bot container.

## Next Steps

1. Deploy the speedtest server to the LXC container
2. Test the HTTP endpoint from your laptop
3. Update the HexChat plugin to use the HTTP endpoint
4. Test `/joinred` and `/joinops` commands

## Related Files

- `speedtest_server.py` - HTTP server implementation
- `docker-compose.yml` - Docker services configuration
- `Dockerfile` - Container build instructions
- `~/irc-topic-bot/` - Main repository directory
