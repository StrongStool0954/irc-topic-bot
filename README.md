# IRC Topic Monitor Bot

Get instant mobile notifications when IRC channel topics change!

## Features

- 🔔 Real-time mobile notifications
- 🔒 SSL/TLS IRC connections
- 📱 Multiple notification backends (ntfy, Pushover, Telegram, Discord)
- 🐳 Docker support
- 🔄 Auto-reconnect
- 📝 Detailed logging

## Quick Start

### 1. Clone or Copy Files

```bash
# Files needed:
# - bot.py (main bot script)
# - requirements.txt (Python dependencies)
# - Dockerfile (for Docker deployment)
# - docker-compose.yml (Docker Compose config)
# - .env.example (configuration template)
```

### 2. Configure

```bash
cp .env.example .env
nano .env
```

Edit these settings:
```bash
IRC_SERVER=irc.orpheus.network
IRC_PORT=7000
IRC_NICKNAME=YourNick
IRC_NICKSERV_PASSWORD=your_password
IRC_CHANNELS=#channel1,#channel2

NOTIFICATION_METHOD=ntfy
NTFY_TOPIC=your-unique-topic-name
```

### 3. Set Up Mobile Notifications

#### ntfy.sh (Recommended - Free & Easy)

1. Install ntfy app on your phone
2. Subscribe to your chosen topic
3. Done!

Test it:
```bash
curl -d "Test" https://ntfy.sh/your-topic-name
```

### 4. Run the Bot

**Docker (Recommended):**
```bash
docker-compose up -d
docker-compose logs -f
```

**Python directly:**
```bash
pip install -r requirements.txt
python bot.py
```

## Deployment Options

- **LXC Container on Proxmox** - See [DEPLOY-LXC.md](DEPLOY-LXC.md)
- **Docker** - Use included `docker-compose.yml`
- **Systemd Service** - See deployment guide
- **Local** - Run manually with Python

## Notification Methods

| Method | Cost | Setup Difficulty | Real-time |
|--------|------|------------------|-----------|
| ntfy.sh | Free | Easy | ✅ Yes |
| Pushover | $5 once | Easy | ✅ Yes |
| Telegram | Free | Medium | ✅ Yes |
| Discord | Free | Easy | ✅ Yes |

## Configuration

All configuration via environment variables in `.env` file:

### IRC Settings
- `IRC_SERVER` - IRC server hostname
- `IRC_PORT` - IRC server port (usually 6667 or 7000 for SSL)
- `IRC_NICKNAME` - Bot nickname
- `IRC_REALNAME` - Bot real name
- `IRC_PASSWORD` - Server password (optional)
- `IRC_NICKSERV_PASSWORD` - NickServ password (optional)
- `IRC_CHANNELS` - Comma-separated list of channels

### Notification Settings
- `NOTIFICATION_METHOD` - One of: `ntfy`, `pushover`, `telegram`, `discord`

**ntfy.sh:**
- `NTFY_TOPIC` - Your unique topic name
- `NTFY_SERVER` - Server URL (default: https://ntfy.sh)

**Pushover:**
- `PUSHOVER_APP_TOKEN` - Application token
- `PUSHOVER_USER_KEY` - User key

**Telegram:**
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Your chat ID

**Discord:**
- `DISCORD_WEBHOOK_URL` - Webhook URL

## Example Notification

When a topic changes, you'll receive:

```
IRC Topic Changed: #announce

Changed by: SomeUser

Old: Welcome to #announce!

New: New release available - check it out!
```

## Monitoring

### View Logs

**Docker:**
```bash
docker-compose logs -f
```

**Systemd:**
```bash
journalctl -u irc-topic-bot -f
```

### Check Status

**Docker:**
```bash
docker-compose ps
```

**Systemd:**
```bash
systemctl status irc-topic-bot
```

## Troubleshooting

### Bot won't connect

1. Check IRC server and port in `.env`
2. Verify SSL certificate is valid: `openssl s_client -connect server:port`
3. Check firewall rules

### No notifications

1. Test notification manually (see commands in .env.example)
2. Verify notification credentials in `.env`
3. Check bot logs for errors

### Bot disconnects

Bot will auto-reconnect. Check logs for connection issues.

## Development

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run bot
python bot.py
```

### Build Docker Image

```bash
docker build -t irc-topic-bot .
```

## Security

- Store `.env` file securely (contains passwords/tokens)
- Use SSL connections to IRC (port 7000 vs 6667)
- Keep notification tokens private
- Run bot as non-root user in Docker

## Requirements

- Python 3.8+
- `irc` library (Python IRC framework)
- `requests` library (for notifications)

Or just use Docker - everything included!

## License

MIT

## Support

For issues or questions, check:
- IRC connection: Verify server/port/credentials
- Notifications: Test manually first
- Logs: Check for error messages

## Links

- ntfy.sh: https://ntfy.sh
- Pushover: https://pushover.net
- IRC Python Library: https://github.com/jaraco/irc
