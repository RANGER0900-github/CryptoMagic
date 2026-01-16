# 🪝 WEBHOOK REFACTORING COMPLETE

## ✅ What Was Done

I've completely refactored the Telegram integration to use **webhooks instead of direct bot API calls**. This gives you the flexibility to integrate with 5-6 different software platforms without platform lock-in.

## 🎯 Architecture

**Old Approach:**
```
CryptoMagic → Direct Telegram API (locked to Telegram only)
```

**New Approach (Webhooks):**
```
CryptoMagic → Your Webhook Server → Telegram + Discord + Slack + Custom APIs
```

## 📦 What Changed

### 1. **Core Webhook System**
- New `send_webhook_notification()` function
- Sends HTTP POST to your webhook with event data
- Graceful fallback to direct Telegram API if webhook fails

### 2. **Refactored Message Functions**
All message functions now:
- Try webhook first (universal platform)
- Fall back to direct Telegram API (backup)
- Support both methods simultaneously

Updated functions:
- `send_telegram_message()` - text messages
- `send_telegram_file()` - file content (sends content via webhook, file via bot API)
- `send_startup_message()` - includes webhook data
- `send_daily_stats()` - includes webhook data
- `file_monitor_thread()` - monitors for changes and sends via webhook

### 3. **New CLI Argument**
```bash
--webhook-url URL
```

Usage:
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --worker-name mybot \
  --webhook-url http://localhost:3000/webhook
```

Can also use environment variable:
```bash
export WEBHOOK_URL=http://your-server.com/webhook
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 --worker-name mybot
```

### 4. **Ready-to-Use Webhook Server**
File: `webhook_server.py`

Features:
- Flask-based HTTP server
- Receives webhook notifications from bot
- Forwards to Telegram (default)
- Optional Discord support
- Optional Slack support
- Message logging
- Health check endpoint
- Configuration endpoint

Installation:
```bash
pip install flask requests
python3 webhook_server.py
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask requests pytz
```

### 2. Start Webhook Server
```bash
python3 webhook_server.py
```

Output:
```
🪝 CryptoMagic Webhook Server
📡 Configured Platforms:
  ✅ Telegram
  ⭕ Discord (optional)
  ⭕ Slack (optional)
🚀 Starting server on http://0.0.0.0:3000
```

### 3. Run CryptoMagic with Webhook
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
  --worker-name my-bot \
  --webhook-url http://localhost:3000/webhook
```

## 📊 Webhook Events

Bot sends JSON payloads with event data:

### Startup Event
```json
{
  "event_type": "startup",
  "timestamp": "2024-01-15T10:30:00+05:30",
  "data": {
    "worker_name": "my-bot",
    "target_file": "eth5.txt",
    "worker_count": 3,
    "formatted_message": "<b>🤖 Bot Started...</b>"
  }
}
```

### Daily Stats Event
```json
{
  "event_type": "daily_stats",
  "data": {
    "worker_name": "my-bot",
    "total_generated": 1234567,
    "average_rate": 750.5,
    "elapsed_seconds": 1645,
    "total_matches": 2,
    "average_cpu": 45.2,
    "worker_count": 3,
    "formatted_message": "<b>📊 Daily Stats...</b>"
  }
}
```

### Match Found Event
```json
{
  "event_type": "match_found",
  "data": {
    "filename": "FoundMATCHAddr.txt",
    "content": "0x1234...\n0x5678...",
    "timestamp": "2024-01-15T10:45:00+05:30"
  }
}
```

## 🔌 Webhook Server Configuration

### Telegram Only (Default)
```bash
python3 webhook_server.py
```

### Discord Support
```bash
DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR/URL" \
python3 webhook_server.py
```

### Slack Support
```bash
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/URL" \
python3 webhook_server.py
```

### All Platforms
```bash
DISCORD_WEBHOOK="..." SLACK_WEBHOOK="..." python3 webhook_server.py
```

### With Security Token
```bash
WEBHOOK_SECRET="your-secret-token" python3 webhook_server.py
```

Then use in bot:
```bash
--webhook-url http://localhost:3000/webhook?token=your-secret-token
```

## 📁 Files Created/Modified

### Modified
- `ethmagic.py`
  - Added webhook functions (~50 lines)
  - Updated message functions for webhook support
  - Added `--webhook-url` CLI argument
  - Fallback to direct Telegram API

### Created
- `webhook_server.py` - Ready-to-use Flask webhook server (170 lines)
- `WEBHOOK_INTEGRATION.md` - Complete webhook documentation
- `webhook-quick-start.sh` - Quick start guide

## 🎯 Why Webhooks?

✅ **No Platform Lock-in**
- Switch from Telegram to Discord anytime
- Use multiple platforms simultaneously
- Not dependent on any single service

✅ **5-6 Software Integration**
- Single webhook server handles multiple platforms
- Multiple bot instances send to same webhook
- Webhook routes messages to different destinations

✅ **Flexible Hosting**
- Webhook can run on any server/cloud provider
- Docker, AWS Lambda, Google Cloud Functions, etc.
- Your own VPS, home server, etc.

✅ **Message Processing**
- Transform messages for different platforms
- Queue messages for processing
- Log all notifications
- Add custom logic

✅ **Fallback Support**
- If webhook fails, bot uses direct Telegram API
- No data loss
- Automatic failover

## 🔄 Fallback Behavior

**If webhook not configured:**
- Bot sends directly to Telegram API
- Works exactly as before

**If webhook fails:**
- Bot logs error
- Automatically falls back to direct Telegram API
- Message still sent
- No interruption to address generation

**If both fail:**
- Error logged to console
- Bot continues running
- Address generation continues
- Notifications may be lost

## 💡 Advanced Usage

### Multiple Bot Instances with Same Webhook
```bash
# Terminal 1
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 \
  --worker-name farm-east \
  --webhook-url http://webhook.com/webhook

# Terminal 2
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 \
  --worker-name farm-west \
  --webhook-url http://webhook.com/webhook

# Both send to same webhook server
# Webhook routes to Telegram, Discord, Slack
```

### Custom Message Transformation
Edit `webhook_server.py` to transform messages:
```python
def transform_for_discord(html_message):
    return html_message.replace('<b>', '**').replace('</b>', '**')
```

### Message Queuing
Add to webhook_server.py:
```python
from queue import Queue
message_queue = Queue()

@app.route('/webhook', methods=['POST'])
def webhook():
    message_queue.put(data)
    return {"status": "queued"}, 202
```

### Message Logging
Webhook server automatically logs to `webhook_notifications.log`

## 📝 Example Webhook Server Configurations

### Simple Telegram-Only
```bash
python3 webhook_server.py
```

### Production with Security
```bash
WEBHOOK_SECRET="random-generated-token" \
TELEGRAM_BOT_TOKEN="your-token" \
TELEGRAM_CHAT_ID="your-id" \
python3 webhook_server.py &

# Use with token in URL
--webhook-url http://your-server.com:3000/webhook?token=random-generated-token
```

### Docker Deployment
```dockerfile
FROM python:3.10
RUN pip install flask requests
COPY webhook_server.py .
CMD ["python3", "webhook_server.py"]
```

```bash
docker build -t webhook-server .
docker run -e TELEGRAM_BOT_TOKEN="..." -p 3000:3000 webhook-server
```

## ✅ Testing

### Check Webhook Health
```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "ok",
  "telegram": true,
  "discord": false,
  "slack": false
}
```

### View Configuration
```bash
curl http://localhost:3000/config
```

### Test Send Message
```bash
curl -X POST http://localhost:3000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "startup",
    "data": {
      "worker_name": "test",
      "formatted_message": "<b>Test</b>"
    }
  }'
```

## 🔐 Security Recommendations

1. **Use HTTPS** in production
2. **Add authentication token** to webhook URL
3. **Validate source** of webhook requests
4. **Log all requests** for auditing
5. **Rate limit** webhook endpoint
6. **Use environment variables** for credentials
7. **Don't expose webhook URL** in logs

## 📚 Documentation Files

1. **WEBHOOK_INTEGRATION.md**
   - Complete webhook documentation
   - Detailed examples
   - Architecture diagrams
   - Troubleshooting guide

2. **webhook-quick-start.sh**
   - Quick start instructions
   - Common commands
   - Configuration examples

3. **webhook_server.py**
   - Ready-to-use Flask server
   - Well commented
   - Easy to customize

## 🚀 Next Steps

1. **Install dependencies:**
   ```bash
   pip install flask requests pytz
   ```

2. **Start webhook server:**
   ```bash
   python3 webhook_server.py
   ```

3. **Run bot with webhook:**
   ```bash
   python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
     --worker-name mybot \
     --webhook-url http://localhost:3000/webhook
   ```

4. **Optional: Add Discord/Slack:**
   ```bash
   DISCORD_WEBHOOK="..." python3 webhook_server.py
   ```

## 🎯 Summary

Your CryptoMagic bot is now:
- ✅ **Platform-agnostic** (not locked to Telegram)
- ✅ **Ready for multi-platform integration** (Telegram, Discord, Slack, custom)
- ✅ **Scalable to 5-6 software platforms**
- ✅ **Enterprise-grade webhook architecture**
- ✅ **Production-ready with fallback**

Perfect for integrating with multiple software platforms without any restrictions!

---

**Questions?** See `WEBHOOK_INTEGRATION.md` for complete guide!
