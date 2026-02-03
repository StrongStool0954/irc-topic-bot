# Setting Up Pushover Notifications for IRC Bot

Pushover provides instant, reliable push notifications for $5 one-time purchase.

## Step 1: Sign Up for Pushover

1. **Go to:** https://pushover.net/signup
2. **Create account** (free to create)
3. **Note your User Key** - displayed on dashboard after login

## Step 2: Purchase Pushover App

**One-time $5 purchase:**
- **iOS:** https://apps.apple.com/us/app/pushover-notifications/id506088175
- **Android:** https://play.google.com/store/apps/details?id=net.superblock.pushover

Install the app and login with your Pushover account.

## Step 3: Create Application

1. **Go to:** https://pushover.net/apps/build
2. **Fill in:**
   - Name: `IRC Topic Monitor`
   - Description: `Alerts for IRC channel topic changes`
   - URL: (leave blank or put your IRC server)
   - Icon: (optional - upload an icon)
3. **Click "Create Application"**
4. **Copy your API Token/Key** - this is your app token

## Step 4: Get Your Keys

After creating the app, you'll have:
- **User Key:** Found at https://pushover.net (top of dashboard)
- **API Token:** Found in your application page

Example:
```
User Key: u4x8k2z9m3p7q1w5e8r2t6y9
API Token: azGDORePK8gMaC0QOYAMyEEuzJnyUi
```

## Step 5: Configure Bot

Edit `/opt/irc-topic-bot/.env`:

```bash
# Notification Method
NOTIFICATION_METHOD=pushover

# Pushover Configuration
PUSHOVER_APP_TOKEN=azGDORePK8gMaC0QOYAMyEEuzJnyUi
PUSHOVER_USER_KEY=u4x8k2z9m3p7q1w5e8r2t6y9
```

## Step 6: Test Notification

Before starting the bot, test Pushover manually:

```bash
curl -s \
  --form-string "token=azGDORePK8gMaC0QOYAMyEEuzJnyUi" \
  --form-string "user=u4x8k2z9m3p7q1w5e8r2t6y9" \
  --form-string "message=Test from IRC bot!" \
  https://api.pushover.net/1/messages.json
```

You should get a notification on your phone instantly!

## Step 7: Start Bot

```bash
cd /opt/irc-topic-bot
docker-compose restart
docker-compose logs -f
```

## Pushover Features

The bot uses these Pushover features:
- **Priority:** High (bypasses quiet hours)
- **Title:** Shows which channel
- **Message:** Shows old/new topic and who changed it
- **Sound:** Default notification sound

## Notification Example

When a topic changes, you'll see:

```
IRC Topic Changed: #announce

Changed by: SomeUser

Old: Welcome to #announce!

New: New release v2.0 is out!
```

## Troubleshooting

### Test API Connection

```bash
# Test with curl
curl -s \
  --form-string "token=YOUR_APP_TOKEN" \
  --form-string "user=YOUR_USER_KEY" \
  --form-string "message=Test" \
  https://api.pushover.net/1/messages.json | jq
```

Should return:
```json
{
  "status": 1,
  "request": "..."
}
```

### Common Issues

**Error: "application token is invalid"**
- Double-check your API Token from https://pushover.net/apps

**Error: "user identifier is not a valid user, group, or subscribed user key"**
- Double-check your User Key from https://pushover.net

**No notification received:**
- Check Pushover app is installed and logged in
- Check phone's notification settings
- Try sending a test via Pushover website

## Pushover vs Other Methods

| Feature | Pushover | ntfy.sh | Telegram |
|---------|----------|---------|----------|
| Cost | $5 once | Free | Free |
| Reliability | Excellent | Good | Good |
| Latency | Very low | Low | Low |
| Setup | Easy | Easiest | Medium |
| Offline support | Yes | Limited | Yes |

## Additional Pushover Settings (Optional)

You can customize the bot.py to add more Pushover features:

### Sounds
```python
"sound": "pushover"  # or "cosmic", "bike", "bugle", etc.
```

### Priority Levels
```python
"priority": 2  # Emergency (requires acknowledgment)
"priority": 1  # High (bypasses quiet hours) - current
"priority": 0  # Normal
"priority": -1  # Low (no sound/vibration)
```

### URLs
```python
"url": "https://irc.orpheus.network",
"url_title": "Join IRC"
```

## Support

- Pushover Docs: https://pushover.net/api
- API FAQ: https://pushover.net/faq
- Support: support@pushover.net
