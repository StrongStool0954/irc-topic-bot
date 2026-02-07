FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies for speedtest
RUN apk add --no-cache curl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt speedtest-cli

# Copy scripts
COPY bot.py .
COPY speedtest_server.py .
RUN chmod +x bot.py speedtest_server.py

# Run as non-root user
RUN adduser -D -u 1000 ircbot
USER ircbot

CMD ["python", "-u", "bot.py"]
