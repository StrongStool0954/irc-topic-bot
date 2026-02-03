# IRC Topic Bot - Quick Start Guide

Get mobile notifications when IRC topics change in 5 minutes!

## What You Need

1. **pm01 access** (Proxmox host)
2. **IRC server details** (irc.orpheus.network)
3. **NickServ password** for your IRC account
4. **Phone** for notifications

## Super Quick Deploy (5 minutes)

### Step 1: Copy Files to pm01

```bash
# From your local machine
cd /home/bullwinkle
scp -r irc-topic-bot pm01:/tmp/
```

### Step 2: Create LXC Container

```bash
# SSH to pm01
ssh pm01

# Create container (ID 1064)
pct create 1064 local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst \
  --hostname irc-bot --cores 1 --memory 512 --swap 512 \
  --storage local-lvm --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --password --unprivileged 1 --onboot 1
```

### Step 3: Auto Setup

```bash
# Run automated setup
cd /tmp/irc-topic-bot
./setup-lxc.sh 1064
```

### Step 4: Configure

```bash
# Enter container
pct enter 1064

# Edit configuration
cd /opt/irc-topic-bot
nano .env
```

**Required settings:**
```bash
IRC_NICKNAME=JDbox
IRC_NICKSERV_PASSWORD=your_password_here
IRC_CHANNELS=#announce,#channel2

NOTIFICATION_METHOD=ntfy
NTFY_TOPIC=jdbox-irc-alerts-xyz
```

### Step 5: Start Bot

```bash
cd /opt/irc-topic-bot
docker-compose up -d
docker-compose logs -f
```

### Step 6: Set Up Phone Notifications

#### Using ntfy.sh (Easiest)

1. **Install app:**
   - Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
   - iOS: https://apps.apple.com/us/app/ntfy/id1625396347

2. **Subscribe:**
   - Open app
   - Tap "+"
   - Enter your topic: `jdbox-irc-alerts-xyz`

3. **Test:**
   ```bash
   curl -d "Test from IRC bot!" https://ntfy.sh/jdbox-irc-alerts-xyz
   ```

### Step 7: Test It!

Change a topic on IRC and watch for the notification!

```
/topic #channel Testing my new bot!
```

## Done! 🎉

Your bot is now running 24/7 on pm01 and will alert you whenever topics change!

## Quick Commands

```bash
# Enter container
pct enter 1064

# View logs
cd /opt/irc-topic-bot && docker-compose logs -f

# Restart bot
docker-compose restart

# Stop bot
docker-compose down

# Update config
nano .env
docker-compose restart
```

## Troubleshooting

**Bot not connecting?**
```bash
# Check logs
docker-compose logs

# Test IRC connection
telnet irc.orpheus.network 7000
```

**No notifications?**
```bash
# Test manually
curl -d "Test" https://ntfy.sh/your-topic-name

# Check config
cat .env | grep NTFY
```

## Files Location

All files are in: `/opt/irc-topic-bot/`

## For Full Documentation

See [DEPLOY-LXC.md](DEPLOY-LXC.md) for complete deployment guide.

---

**Your IRC bot is watching! 👀**
