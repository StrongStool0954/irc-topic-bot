#!/usr/bin/env python3
"""
IRC Topic Monitor Bot
Monitors IRC channel topics and sends mobile notifications when they change
"""

import irc.bot
import irc.connection
import ssl
import os
import sys
import requests
import json
from datetime import datetime
from typing import Optional


class TopicMonitorBot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        self.config = config
        self.topics = {}  # Store current topics per channel

        # Set up SSL connection factory
        ssl_context = ssl.create_default_context()

        def ssl_wrapper(sock):
            return ssl_context.wrap_socket(sock, server_hostname=config['server'])

        ssl_factory = irc.connection.Factory(wrapper=ssl_wrapper)

        # Connect to IRC server
        server = [(
            config['server'],
            config['port'],
            config.get('password')
        )]

        super().__init__(
            server,
            config['nickname'],
            config['realname'],
            connect_factory=ssl_factory
        )

    def on_welcome(self, connection, event):
        """Called when bot connects to server"""
        print(f"[{self._timestamp()}] Connected to {self.config['server']}")

        # Identify with NickServ if password provided
        if self.config.get('nickserv_password'):
            connection.privmsg(
                'NickServ',
                f"IDENTIFY {self.config['nickserv_password']}"
            )
            print(f"[{self._timestamp()}] Identified with NickServ")

        # Join channels
        for channel in self.config['channels']:
            connection.join(channel)
            print(f"[{self._timestamp()}] Joined {channel}")

    def on_topic(self, connection, event):
        """Called when topic is received (on join or when changed)"""
        channel = event.target
        topic = event.arguments[0] if event.arguments else ""

        # Check if this is a topic change
        if channel in self.topics and self.topics[channel] != topic:
            old_topic = self.topics[channel]
            print(f"[{self._timestamp()}] Topic changed in {channel}")
            print(f"  Old: {old_topic}")
            print(f"  New: {topic}")

            # Send notification
            self._send_notification(channel, old_topic, topic, event.source.nick)

        # Store current topic
        self.topics[channel] = topic

    def on_currenttopic(self, connection, event):
        """Called when receiving current topic (numeric 332)"""
        # event.arguments[0] is channel, event.arguments[1] is topic
        if len(event.arguments) >= 2:
            channel = event.arguments[0]
            topic = event.arguments[1]

            if channel not in self.topics:
                self.topics[channel] = topic
                print(f"[{self._timestamp()}] Initial topic for {channel}: {topic}")

    def on_topicinfo(self, connection, event):
        """Called when receiving topic metadata (numeric 333)"""
        # This gives us who set the topic and when
        pass

    def on_pubmsg(self, connection, event):
        """Called when a public message is received"""
        # We can add commands here if needed
        pass

    def on_disconnect(self, connection, event):
        """Called when disconnected from server"""
        print(f"[{self._timestamp()}] Disconnected from server")
        sys.exit(0)

    def _timestamp(self):
        """Get formatted timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _send_notification(self, channel, old_topic, new_topic, changed_by):
        """Send notification via configured method"""
        title = f"IRC Topic Changed: {channel}"
        message = f"Changed by: {changed_by}\n\nOld: {old_topic}\n\nNew: {new_topic}"

        method = self.config.get('notification_method', 'ntfy')

        try:
            if method == 'ntfy':
                self._send_ntfy(title, message)
            elif method == 'pushover':
                self._send_pushover(title, message)
            elif method == 'telegram':
                self._send_telegram(title, message)
            elif method == 'discord':
                self._send_discord(title, message)
            else:
                print(f"[{self._timestamp()}] Unknown notification method: {method}")
        except Exception as e:
            print(f"[{self._timestamp()}] Failed to send notification: {e}")

    def _send_ntfy(self, title, message):
        """Send notification via ntfy.sh"""
        topic = self.config.get('ntfy_topic', 'irc-topic-monitor')
        server = self.config.get('ntfy_server', 'https://ntfy.sh')

        requests.post(
            f"{server}/{topic}",
            data=message.encode('utf-8'),
            headers={
                "Title": title,
                "Priority": "high",
                "Tags": "speech_balloon"
            }
        )
        print(f"[{self._timestamp()}] Sent ntfy notification")

    def _send_pushover(self, title, message):
        """Send notification via Pushover"""
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": self.config['pushover_app_token'],
                "user": self.config['pushover_user_key'],
                "title": title,
                "message": message,
                "priority": 1
            }
        )
        print(f"[{self._timestamp()}] Sent Pushover notification")

    def _send_telegram(self, title, message):
        """Send notification via Telegram"""
        bot_token = self.config['telegram_bot_token']
        chat_id = self.config['telegram_chat_id']

        full_message = f"<b>{title}</b>\n\n{message}"

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": full_message,
                "parse_mode": "HTML"
            }
        )
        print(f"[{self._timestamp()}] Sent Telegram notification")

    def _send_discord(self, title, message):
        """Send notification via Discord webhook"""
        requests.post(
            self.config['discord_webhook_url'],
            json={
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 3447003,  # Blue
                    "timestamp": datetime.utcnow().isoformat()
                }]
            }
        )
        print(f"[{self._timestamp()}] Sent Discord notification")


def load_config():
    """Load configuration from environment variables or config file"""
    config = {
        # IRC Settings
        'server': os.getenv('IRC_SERVER', 'irc.orpheus.network'),
        'port': int(os.getenv('IRC_PORT', '7000')),
        'nickname': os.getenv('IRC_NICKNAME', 'TopicBot'),
        'realname': os.getenv('IRC_REALNAME', 'Topic Monitor Bot'),
        'password': os.getenv('IRC_PASSWORD'),
        'nickserv_password': os.getenv('IRC_NICKSERV_PASSWORD'),
        'channels': os.getenv('IRC_CHANNELS', '#test').split(','),

        # Notification Settings
        'notification_method': os.getenv('NOTIFICATION_METHOD', 'ntfy'),

        # ntfy.sh settings
        'ntfy_topic': os.getenv('NTFY_TOPIC', 'irc-topic-monitor'),
        'ntfy_server': os.getenv('NTFY_SERVER', 'https://ntfy.sh'),

        # Pushover settings
        'pushover_app_token': os.getenv('PUSHOVER_APP_TOKEN'),
        'pushover_user_key': os.getenv('PUSHOVER_USER_KEY'),

        # Telegram settings
        'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
        'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),

        # Discord settings
        'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
    }

    return config


def main():
    """Main entry point"""
    print("=== IRC Topic Monitor Bot ===")
    print(f"Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    config = load_config()

    print(f"Server: {config['server']}:{config['port']}")
    print(f"Nickname: {config['nickname']}")
    print(f"Channels: {', '.join(config['channels'])}")
    print(f"Notification method: {config['notification_method']}")
    print()

    bot = TopicMonitorBot(config)

    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
