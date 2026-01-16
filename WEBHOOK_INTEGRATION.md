# 🪝 Webhook Integration Guide - Multi-Platform Support

## Overview

**CryptoMagic now supports webhooks** for platform-agnostic notifications! This allows your bot to integrate with **any service** (Telegram, Discord, Slack, custom APIs, etc.) without being locked into a single platform.

## Architecture

```
┌─────────────────────┐
│  CryptoMagic Bot    │
│  (Ethereum Hunter)  │
└──────────┬──────────┘
           │
           ├─→ Webhook (Your Server/API)
           │   └─→ Telegram, Discord, Slack, etc.
           │
           └─→ Direct Bot API (Fallback)
               └─→ Telegram API
```

### Why Webhooks?

✅ **Multi-platform support** - Same bot can send to Telegram, Discord, Slack simultaneously  
✅ **No platform lock-in** - Change your notification service without changing bot code  
✅ **Flexible hosting** - Webhook can run anywhere (your server, cloud function, docker, etc.)  
✅ **Message processing** - Webhook can transform, queue, log messages before sending  
✅ **5-6 software integration** - Easily integrate with multiple applications  
✅ **Fallback support** - If webhook fails, bot falls back to direct Telegram API  

## How It Works

### Webhook Request Format

When an event occurs, CryptoMagic sends a POST request to your webhook:

```json
{
  "event_type": "startup|daily_stats|match_found|message",
  "timestamp": "2024-01-15T10:30:00+05:30",
  "data": {
    "message_type": "startup|text|file_content|daily_stats|match_alert",
    "worker_name": "robo1",
    "target_file": "eth5.txt",
    "worker_count": 4,
    "formatted_message": "HTML formatted text...",
    // Additional fields depending on event type
  }
}
```

### Event Types

#### 1. **Startup Event**
```json
{
  "event_type": "startup",
  "data": {
    "message_type": "startup",
    "worker_name": "robo1",
    "target_file": "eth5.txt",
    "worker_count": 4,
    "formatted_message": "<b>🤖 Bot Started...</b>"
  }
}
```

#### 2. **Daily Stats Event**
```json
{
  "event_type": "daily_stats",
  "data": {
    "message_type": "daily_stats",
    "worker_name": "robo1",
    "total_generated": 1234567,
    "average_rate": 750.5,
    "elapsed_seconds": 1645,
    "total_matches": 2,
    "average_cpu": 45.2,
    "worker_count": 4,
    "formatted_message": "<b>📊 Daily Stats Report...</b>"
  }
}
```

#### 3. **Match Found Event**
```json
{
  "event_type": "match_found",
  "data": {
    "message_type": "file_content|match_alert",
    "filename": "FoundMATCHAddr.txt",
    "content": "0x1234...\n0x5678...\n",
    "timestamp": "2024-01-15T10:45:00+05:30"
  }
}
```

#### 4. **Message Event**
```json
{
  "event_type": "message",
  "data": {
    "message_type": "text",
    "content": "<b>🎉 MATCH FOUND!</b>",
    "parse_mode": "HTML"
  }
}
```

## Setup Options

### Option 1: Use with Telegram (Default + Webhook)

```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --worker-name farm1 \
  --webhook-url http://your-server.com/webhook
```

**Result**: Messages sent to BOTH webhook AND Telegram  
**Benefit**: Redundancy + flexibility

### Option 2: Webhook Only

Set up webhook to forward to Telegram:

```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --worker-name farm1 \
  --webhook-url http://your-webhook-server.com/notify
```

### Option 3: Environment Variable

```bash
export WEBHOOK_URL=http://your-server.com/webhook
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 --worker-name farm1
```

## Example Webhook Servers

### 1. Simple Python Webhook (Flask)

```python
from flask import Flask, request
import requests

app = Flask(__name__)

# Your Telegram bot credentials
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive CryptoMagic notifications and forward to Telegram."""
    data = request.json
    
    if data['event_type'] == 'match_found':
        # Send file content to Telegram
        content = data['data']['content']
        message = f"🎉 MATCH FOUND!\n\n{content}"
    else:
        # Send formatted message
        message = data['data'].get('formatted_message', '')
    
    # Forward to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })
    
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```

**Run it:**
```bash
pip install flask requests
python webhook_server.py
# Then use: --webhook-url http://localhost:3000/webhook
```

### 2. Discord Webhook

```python
from flask import Flask, request
import requests

app = Flask(__name__)
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if data['event_type'] == 'match_found':
        content = data['data']['content']
        message = f"🎉 MATCH FOUND!\n```\n{content}\n```"
    else:
        message = data['data'].get('formatted_message', '').replace('<b>', '**').replace('</b>', '**')
    
    requests.post(DISCORD_WEBHOOK, json={"content": message})
    return {"status": "ok"}, 200

app.run(host='0.0.0.0', port=3000)
```

### 3. Slack Webhook

```python
from flask import Flask, request
import requests

app = Flask(__name__)
SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if data['event_type'] == 'match_found':
        text = data['data']['content']
    else:
        text = data['data'].get('formatted_message', '')
    
    requests.post(SLACK_WEBHOOK, json={"text": text})
    return {"status": "ok"}, 200

app.run(host='0.0.0.0', port=3000)
```

### 4. Multi-Platform (Telegram + Discord + Slack)

```python
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "..."
TELEGRAM_CHAT_ID = "..."
DISCORD_WEBHOOK = "..."
SLACK_WEBHOOK = "..."

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"})

def send_to_discord(message):
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def send_to_slack(message):
    requests.post(SLACK_WEBHOOK, json={"text": message})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data['data'].get('formatted_message', '')
    
    # Send to ALL platforms simultaneously
    send_to_telegram(message)
    send_to_discord(message)
    send_to_slack(message)
    
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```

## Deployment Options

### Local Machine
```bash
python webhook_server.py
# Use: --webhook-url http://localhost:3000/webhook
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY webhook_server.py .
RUN pip install flask requests
CMD ["python", "webhook_server.py"]
```

```bash
docker build -t webhook-server .
docker run -p 3000:3000 webhook_server
```

### Cloud (AWS Lambda, Google Cloud Functions, etc.)

Create a simple serverless function that receives webhooks and forwards them.

### Ngrok (For testing)
```bash
pip install ngrok
ngrok http 3000
# Use the ngrok URL as webhook-url
```

## Advanced Usage

### Multiple Webhook URLs (Via Webhook)

Your webhook receiver can send to multiple destinations:

```python
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data['data'].get('formatted_message', '')
    
    # Send to multiple services
    send_to_telegram(message)
    send_to_discord(message)
    send_to_slack(message)
    send_to_custom_api(message)  # Your own service
    
    return {"status": "ok"}, 200
```

### Message Transformation

Transform messages for different platforms:

```python
def transform_for_discord(html_message):
    """Convert HTML to Discord markdown."""
    return html_message.replace('<b>', '**').replace('</b>', '**')

def transform_for_slack(html_message):
    """Convert HTML to Slack format."""
    return html_message.replace('<b>', '*').replace('</b>', '*')
```

### Message Queuing

Queue messages for later processing:

```python
from queue import Queue
import threading

message_queue = Queue()

def webhook():
    data = request.json
    message_queue.put(data)
    return {"status": "queued"}, 202

def process_messages():
    while True:
        data = message_queue.get()
        send_to_all_platforms(data)
        message_queue.task_done()

threading.Thread(target=process_messages, daemon=True).start()
```

### Message Logging

Log all notifications:

```python
import json
from datetime import datetime

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Log to file
    with open('notifications.log', 'a') as f:
        f.write(f"{datetime.now()} - {json.dumps(data)}\n")
    
    # Forward to services
    send_to_all_platforms(data)
    
    return {"status": "ok"}, 200
```

## CLI Reference

```bash
python3 ethmagic.py [OPTIONS]

Options:
  -f, --file FILE              Target addresses file (required)
  -v, --verbose COUNT          Progress update interval [default: 100000]
  -n, --threads WORKERS        Number of worker processes [default: 2]
  -r, --report-interval SECS   Throttle live output every N seconds [default: 1]
  --worker-name NAME           Worker identifier [default: CryptoBot]
  --webhook-url URL            Webhook URL for notifications (optional)
                               Supports environment variable: WEBHOOK_URL
```

## Examples

### Single Worker with Webhook
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --worker-name bot1 \
  --webhook-url http://localhost:3000/webhook
```

### Multiple Workers (Each with Webhook)
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 --worker-name east --webhook-url http://server1.com/webhook &
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 --worker-name west --webhook-url http://server2.com/webhook &
```

### 24/7 with Webhook
```bash
nohup python3 ethmagic.py -f eth5.txt -v 100000 -n 16 \
  --worker-name farm \
  --webhook-url http://webhook-server.com/notify > bot.log 2>&1 &
```

### Use Environment Variable
```bash
export WEBHOOK_URL=http://webhook-server.com/notify
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 --worker-name bot1
```

## Fallback Behavior

**If webhook is not configured or fails:**
- Bot automatically falls back to direct Telegram Bot API
- No messages are lost
- Direct API is used as backup

**If both webhook and Telegram API fail:**
- Errors logged to console
- Bot continues running (doesn't crash)
- Notifications may be missed but address generation continues

## Best Practices

1. **Use fallback** - Always keep Telegram credentials configured for backup
2. **Test webhook** - Test your webhook endpoint before deploying
3. **Monitor webhook** - Log webhook requests and responses
4. **Handle errors** - Your webhook should gracefully handle malformed requests
5. **Use HTTPS** - Use HTTPS URLs in production for security
6. **Add authentication** - Add secret tokens to your webhook URL for security
7. **Rate limiting** - Implement rate limiting if needed
8. **Timeout handling** - Set reasonable timeouts (bot uses 10 seconds)

## Webhook Security

### Add Secret Token

**Webhook Server:**
```python
SECRET_TOKEN = "your-secret-token-here"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate token in URL
    if request.args.get('token') != SECRET_TOKEN:
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    send_to_all_platforms(data)
    return {"status": "ok"}, 200
```

**Bot Usage:**
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --webhook-url http://server.com/webhook?token=your-secret-token-here
```

## Troubleshooting

### Webhook Not Receiving Requests

1. **Check URL**: Verify webhook URL is correct and reachable
2. **Check firewall**: Ensure port is open and accessible
3. **Check logs**: Enable request logging on webhook server
4. **Test with curl**:
```bash
curl -X POST http://your-webhook/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Webhook Timeout

- Bot waits 10 seconds for webhook response
- If webhook takes longer, request fails
- Optimize webhook performance or use async processing

### Fallback Not Working

- If webhook fails, bot falls back to Telegram API
- Ensure Telegram credentials are configured
- Check Telegram API errors in console

---

## Summary

**Webhooks enable:**
✅ Multi-platform support (Telegram, Discord, Slack, etc.)  
✅ No platform lock-in  
✅ Flexible deployment options  
✅ Integration with 5-6 different software platforms  
✅ Message processing and transformation  
✅ Automatic fallback to direct Telegram API  

**Your bot is now platform-agnostic and ready for enterprise integration!**
