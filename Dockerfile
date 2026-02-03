FROM python:3.11-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot script
COPY bot.py .
RUN chmod +x bot.py

# Run as non-root user
RUN adduser -D -u 1000 ircbot
USER ircbot

CMD ["python", "-u", "bot.py"]
