#!/usr/bin/env python3
"""
Speedtest HTTP Server
Runs speedtest periodically and serves the latest URL via HTTP
"""

import subprocess
import threading
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

# Configuration
SPEEDTEST_INTERVAL = int(os.getenv('SPEEDTEST_INTERVAL', '1800'))  # 30 minutes default
HTTP_PORT = int(os.getenv('SPEEDTEST_HTTP_PORT', '8888'))
SPEEDTEST_CMD = os.getenv('SPEEDTEST_CMD', 'speedtest-cli --share')

# State
latest_speedtest_url = None
last_speedtest_time = 0
speedtest_running = False


def run_speedtest():
    """Run speedtest and extract the shareable URL."""
    global latest_speedtest_url, last_speedtest_time, speedtest_running

    if speedtest_running:
        print(f"[{timestamp()}] Speedtest already running, skipping...")
        return

    try:
        speedtest_running = True
        print(f"[{timestamp()}] Running speedtest...")

        result = subprocess.run(
            SPEEDTEST_CMD.split(),
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            # Parse output for share URL (handles both http:// and https://)
            match = re.search(r'https?://www\.speedtest\.net/result/\S+', result.stdout)
            if match:
                url = match.group(0)
                latest_speedtest_url = url
                last_speedtest_time = time.time()
                print(f"[{timestamp()}] Speedtest complete: {url}")
            else:
                print(f"[{timestamp()}] Could not find share URL in output")
        else:
            print(f"[{timestamp()}] Speedtest failed: {result.stderr[:200]}")

    except subprocess.TimeoutExpired:
        print(f"[{timestamp()}] Speedtest timed out after 2 minutes")
    except Exception as e:
        print(f"[{timestamp()}] Error running speedtest: {e}")
    finally:
        speedtest_running = False


def speedtest_worker():
    """Background worker that runs speedtest periodically."""
    # Run initial speedtest
    run_speedtest()

    # Run periodically
    while True:
        time.sleep(SPEEDTEST_INTERVAL)
        run_speedtest()


def timestamp():
    """Get formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SpeedtestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for speedtest URL."""

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/trigger':
            # Trigger immediate speedtest run
            if speedtest_running:
                self.send_response(429)  # Too Many Requests
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Speedtest already running, please wait\n")
                print(f"[{timestamp()}] Trigger request denied - speedtest already running")
            else:
                # Start speedtest in background thread
                trigger_thread = threading.Thread(target=run_speedtest, daemon=True)
                trigger_thread.start()

                self.send_response(202)  # Accepted
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Speedtest triggered, check back in 30-60 seconds\n")
                print(f"[{timestamp()}] Speedtest manually triggered")
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found\n")

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/speedtest' or self.path == '/speedtest.txt':
            # Serve speedtest URL
            if latest_speedtest_url:
                age_minutes = int((time.time() - last_speedtest_time) / 60)
                response = f"{latest_speedtest_url}\n"

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('X-Speedtest-Age-Minutes', str(age_minutes))
                self.send_header('X-Speedtest-Timestamp', str(int(last_speedtest_time)))
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))

                print(f"[{timestamp()}] Served speedtest URL (age: {age_minutes} minutes)")
            else:
                self.send_response(503)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"No speedtest available yet\n")
                print(f"[{timestamp()}] No speedtest URL available")

        elif self.path == '/status':
            # Serve status information
            if latest_speedtest_url:
                age_minutes = int((time.time() - last_speedtest_time) / 60)
                status = (
                    f"Speedtest HTTP Server\n"
                    f"Latest URL: {latest_speedtest_url}\n"
                    f"Age: {age_minutes} minutes\n"
                    f"Last check: {datetime.fromtimestamp(last_speedtest_time).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Check interval: {SPEEDTEST_INTERVAL // 60} minutes\n"
                )
            else:
                status = "No speedtest run yet\n"

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(status.encode('utf-8'))

        elif self.path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK\n")

        else:
            # 404 for other paths
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not Found\n")

    def log_message(self, format, *args):
        """Suppress default HTTP logging (we do our own)."""
        pass


def main():
    """Main entry point."""
    print("=== Speedtest HTTP Server ===")
    print(f"Starting at {timestamp()}")
    print(f"HTTP port: {HTTP_PORT}")
    print(f"Check interval: {SPEEDTEST_INTERVAL // 60} minutes")
    print(f"Speedtest command: {SPEEDTEST_CMD}")
    print()

    # Start speedtest worker thread
    worker = threading.Thread(target=speedtest_worker, daemon=True)
    worker.start()

    # Start HTTP server
    server = HTTPServer(('0.0.0.0', HTTP_PORT), SpeedtestHandler)
    print(f"[{timestamp()}] HTTP server listening on port {HTTP_PORT}")
    print(f"[{timestamp()}] Endpoints:")
    print(f"  GET  /speedtest - Get latest speedtest URL")
    print(f"  GET  /status - Server status")
    print(f"  GET  /health - Health check")
    print(f"  POST /trigger - Trigger immediate speedtest")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] Server stopped by user")
        server.shutdown()


if __name__ == "__main__":
    main()
