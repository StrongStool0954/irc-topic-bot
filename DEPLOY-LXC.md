# Deploy IRC Topic Bot on LXC Container (pm01.funlab.casa)

Complete guide to deploying the IRC topic monitor bot on a new LXC container on pm01.

## Quick Summary

This bot monitors IRC channel topics and sends instant mobile notifications when they change.

**Supported Notifications:**
- **ntfy.sh** (Recommended - Free, no account needed)
- Pushover ($5 one-time)
- Telegram (Free)
- Discord (Free)

## Step 1: Create LXC Container on pm01

### Option A: Via Proxmox Web UI

1. **Login to Proxmox** at pm01.funlab.casa:8006
2. **Create Container:**
   - Click "Create CT"
   - **General:**
     - Node: pm01
     - CT ID: (next available, e.g., 1064)
     - Hostname: `irc-bot`
     - Password: (set root password)
   - **Template:**
     - Storage: local
     - Template: `ubuntu-24.04-standard` (or latest)
   - **Root Disk:**
     - Storage: local-lvm
     - Disk size: 8 GB
   - **CPU:**
     - Cores: 1
   - **Memory:**
     - RAM: 512 MB
     - Swap: 512 MB
   - **Network:**
     - Bridge: vmbr0
     - IPv4: DHCP (or static)
     - IPv6: DHCP (or none)
   - **DNS:**
     - Use host settings
   - Click **Finish**

3. **Start the container**

### Option B: Via Command Line

```bash
# SSH to pm01
ssh pm01

# Create Ubuntu 24.04 container
pct create 1064 local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \
  --hostname irc-bot \
  --cores 1 \
  --memory 512 \
  --swap 512 \
  --storage local-lvm \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --password \
  --unprivileged 1

# Start container
pct start 1064
```

## Step 2: Initial Container Setup

```bash
# Attach to container
pct enter 1064

# Update system
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone America/Phoenix  # or your timezone

# Create a user for the bot (optional but recommended)
adduser ircbot
usermod -aG sudo ircbot
```

## Step 3: Install Docker (Recommended Method)

```bash
# Still in LXC container

# Install Docker
apt update
apt install -y docker.io docker-compose
systemctl enable --now docker

# Add ircbot user to docker group
usermod -aG docker ircbot

# Test Docker
docker --version
```

## Step 4: Deploy the Bot

### Copy Files to LXC Container

From your **local machine** (where you have the files):

```bash
# Copy entire bot directory to LXC container
scp -r /home/bullwinkle/irc-topic-bot root@pm01:/tmp/

# SSH to pm01
ssh pm01

# Copy to LXC container
pct push 1064 /tmp/irc-topic-bot /opt/irc-topic-bot -r

# Or if you prefer, from within the LXC container:
# Clone from a git repo or manually create files
```

### Or Create Files Manually in LXC

```bash
# In LXC container (pct enter 1064)
mkdir -p /opt/irc-topic-bot
cd /opt/irc-topic-bot

# Create files - copy content from bot.py, Dockerfile, etc.
# (see other files in this directory)
```

## Step 5: Configure the Bot

```bash
cd /opt/irc-topic-bot

# Copy example env file
cp .env.example .env

# Edit configuration
nano .env
```

**Edit `.env` file with your settings:**

```bash
# IRC Settings
IRC_SERVER=irc.orpheus.network
IRC_PORT=7000
IRC_NICKNAME=JDbox
IRC_REALNAME=Topic Monitor Bot
IRC_NICKSERV_PASSWORD=your_actual_password_here
IRC_CHANNELS=#announce,#help,#requests

# Choose notification method: ntfy (recommended), pushover, telegram, or discord
NOTIFICATION_METHOD=ntfy

# ntfy.sh settings (easiest option)
NTFY_TOPIC=jdbox-irc-orpheus-alerts  # Choose a unique name
NTFY_SERVER=https://ntfy.sh
```

### Set Up Mobile Notifications

#### Option 1: ntfy.sh (Recommended - Easiest)

1. **On your phone:**
   - Install ntfy app:
     - **Android:** https://play.google.com/store/apps/details?id=io.heckel.ntfy
     - **iOS:** https://apps.apple.com/us/app/ntfy/id1625396347

2. **Subscribe to your topic:**
   - Open ntfy app
   - Tap "+" to add subscription
   - Enter your topic name: `jdbox-irc-orpheus-alerts`
   - Done! You'll get notifications instantly

3. **Test it:**
   ```bash
   curl -d "Test notification from IRC bot" https://ntfy.sh/jdbox-irc-orpheus-alerts
   ```
   You should get a notification on your phone!

#### Option 2: Pushover ($5 one-time)

1. Sign up at https://pushover.net
2. Install Pushover app on phone
3. Create application, get app token
4. Add to `.env`:
   ```bash
   NOTIFICATION_METHOD=pushover
   PUSHOVER_APP_TOKEN=your_app_token
   PUSHOVER_USER_KEY=your_user_key
   ```

#### Option 3: Telegram (Free)

1. Create bot with @BotFather
2. Get bot token
3. Start chat with bot
4. Get chat ID from: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Add to `.env`:
   ```bash
   NOTIFICATION_METHOD=telegram
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

## Step 6: Run the Bot

### Method A: Docker (Recommended)

```bash
cd /opt/irc-topic-bot

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down

# Restart bot
docker-compose restart
```

### Method B: Systemd Service (Without Docker)

```bash
# Install Python dependencies
apt install -y python3 python3-pip
pip3 install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/irc-topic-bot.service << 'EOF'
[Unit]
Description=IRC Topic Monitor Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/irc-topic-bot
EnvironmentFile=/opt/irc-topic-bot/.env
ExecStart=/usr/bin/python3 /opt/irc-topic-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable irc-topic-bot
systemctl start irc-topic-bot

# Check status
systemctl status irc-topic-bot

# View logs
journalctl -u irc-topic-bot -f
```

## Step 7: Test the Bot

1. **Check bot is running:**
   ```bash
   docker-compose ps
   # or
   systemctl status irc-topic-bot
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   # or
   journalctl -u irc-topic-bot -f
   ```

3. **Change a topic on IRC:**
   - Join one of your monitored channels
   - Change the topic: `/topic #channel New topic here`
   - You should get a mobile notification immediately!

## Step 8: Make Container Auto-Start

```bash
# On pm01 host (not in container)
ssh pm01

# Set container to auto-start
pct set 1064 --onboot 1
```

## Monitoring and Maintenance

### View Bot Logs

```bash
# Docker method
docker-compose logs -f

# Systemd method
journalctl -u irc-topic-bot -f
```

### Restart Bot

```bash
# Docker method
docker-compose restart

# Systemd method
systemctl restart irc-topic-bot
```

### Update Bot

```bash
cd /opt/irc-topic-bot

# Pull new code (if using git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

## Troubleshooting

### Bot Won't Connect to IRC

```bash
# Check logs for connection errors
docker-compose logs

# Test SSL connection manually
openssl s_client -connect irc.orpheus.network:7000

# Check firewall
apt install -y telnet
telnet irc.orpheus.network 7000
```

### Not Receiving Notifications

```bash
# Test notification manually
# For ntfy:
curl -d "Test" https://ntfy.sh/your-topic-name

# Check notification settings in .env
cat .env | grep NOTIFICATION
```

### Container Won't Start

```bash
# On pm01
pct status 1064

# Check container config
pct config 1064

# Try starting manually
pct start 1064

# View container logs
pct enter 1064
journalctl -xe
```

## Backup and Recovery

### Backup Container

```bash
# On pm01
vzdump 1064 --compress zstd --mode stop --storage local

# Backup just the bot config
pct pull 1064 /opt/irc-topic-bot/.env /tmp/irc-bot-backup.env
```

### Restore Container

```bash
# On pm01
pct restore 1064 /var/lib/vz/dump/vzdump-lxc-1064-*.tar.zst
```

## Security Notes

1. **NickServ Password** - Stored in `.env` file, make sure permissions are restrictive:
   ```bash
   chmod 600 /opt/irc-topic-bot/.env
   ```

2. **Notification Tokens** - Keep your notification API tokens secure

3. **Updates** - Keep container updated:
   ```bash
   pct enter 1064
   apt update && apt upgrade -y
   ```

## Resource Usage

Expected resource usage:
- **CPU:** <1% average
- **RAM:** ~50-100 MB
- **Disk:** ~500 MB
- **Network:** Minimal (just IRC connection)

## Quick Commands Reference

```bash
# Start/Stop/Restart
docker-compose up -d
docker-compose down
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Access container shell
docker-compose exec irc-topic-bot sh

# Update and restart
docker-compose down && docker-compose build && docker-compose up -d
```

## Next Steps

1. Monitor for topic changes over a few days
2. Adjust notification settings if too noisy
3. Add more channels to monitor in `.env`
4. Set up log rotation if using systemd method

---

**Bot is now running 24/7 on pm01!** 🎉

You'll get instant mobile notifications whenever IRC channel topics change.
