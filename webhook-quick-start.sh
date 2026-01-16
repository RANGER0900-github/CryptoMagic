#!/bin/bash
# 🪝 Webhook Setup - Quick Start Guide

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              🪝 WEBHOOK INTEGRATION - QUICK START GUIDE 🪝               ║
║                                                                            ║
║        Multi-Platform Support for 5-6 Software Integration                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHAT IS WEBHOOK INTEGRATION?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Instead of bot sending directly to Telegram, it sends to YOUR webhook:

    CryptoMagic Bot → Your Webhook Server → Telegram + Discord + Slack + Custom APIs

✅ Benefits:
  • No platform lock-in (switch from Telegram to Discord anytime)
  • Integrate with 5-6 different software platforms
  • Webhook can be on ANY server/cloud provider
  • Message processing, logging, queuing at webhook layer
  • Flexible and scalable architecture

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ QUICK START (5 minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Install Flask (webhook server framework)
────────────────────────────────────────────────
  $ pip install flask requests

Step 2: Start webhook server
────────────────────────────
  $ python3 webhook_server.py
  
  You should see:
    🪝 CryptoMagic Webhook Server
    📡 Configured Platforms:
      ✅ Telegram
      ⭕ Discord (optional)
      ⭕ Slack (optional)
    🚀 Starting server on http://0.0.0.0:3000

Step 3: In another terminal, run CryptoMagic with webhook
─────────────────────────────────────────────────────────
  $ python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \
      --worker-name my-bot \
      --webhook-url http://localhost:3000/webhook
  
  When bot starts, you'll see:
    📱 Sending startup notification to Telegram...
    
  And in webhook server terminal:
    🔔 Received webhook: startup
    ✅ Sent to: Telegram

Done! Your bot is now using webhooks! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Bot generates addresses
2. Event occurs (startup, match, daily stats)
3. Bot sends HTTP POST to webhook with JSON:
   
   {
     "event_type": "match_found",
     "data": {
       "filename": "FoundMATCHAddr.txt",
       "content": "0x1234...\n0x5678...",
       "timestamp": "2024-01-15T10:45:00+05:30"
     }
   }

4. Webhook server receives POST request
5. Webhook parses JSON and sends to Telegram (or other platforms)
6. If webhook fails, bot falls back to direct Telegram API

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 WEBHOOK URL OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Local Machine
   ──────────────
   $ python3 webhook_server.py
   $ python3 ethmagic.py ... --webhook-url http://localhost:3000/webhook

2. Remote Server
   ──────────────
   $ ssh user@your-server.com
   $ python3 webhook_server.py
   
   On local machine:
   $ python3 ethmagic.py ... --webhook-url http://your-server.com:3000/webhook

3. Cloud Provider (AWS, GCP, Azure, etc.)
   ───────────────────────────────────────
   Deploy webhook_server.py to cloud function or container
   Use cloud URL: --webhook-url https://your-cloud-service.com/webhook

4. Docker Container
   ─────────────────
   $ docker build -t webhook-server -f Dockerfile .
   $ docker run -p 3000:3000 webhook_server
   $ python3 ethmagic.py ... --webhook-url http://localhost:3000/webhook

5. Environment Variable
   ─────────────────────
   $ export WEBHOOK_URL=http://your-server.com:3000/webhook
   $ python3 ethmagic.py -f eth5.txt -v 100000 -n 3 --worker-name bot1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 CONFIGURE ADDITIONAL PLATFORMS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

By default, webhook sends to Telegram. Add Discord or Slack:

Discord
───────
1. Create Discord server and webhook:
   - Server Settings → Integrations → Webhooks → New Webhook
   - Copy webhook URL

2. Start webhook server with Discord:
   $ DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR/URL" \
     python3 webhook_server.py

3. Your bot now sends to BOTH Telegram AND Discord automatically!

Slack
─────
1. Create Slack webhook:
   - Your Workspace → Apps → Incoming Webhooks → New Webhook
   - Copy webhook URL

2. Start webhook server with Slack:
   $ SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/URL" \
     python3 webhook_server.py

3. Your bot now sends to Telegram AND Slack!

Both
────
$ DISCORD_WEBHOOK="..." SLACK_WEBHOOK="..." python3 webhook_server.py

All three (Telegram + Discord + Slack) active simultaneously! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 SECURITY (Optional but Recommended)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Protect your webhook with a secret token:

1. Start webhook with secret:
   $ WEBHOOK_SECRET="super-secret-token-123" python3 webhook_server.py

2. Use secret in bot URL:
   $ python3 ethmagic.py ... --webhook-url http://localhost:3000/webhook?token=super-secret-token-123

Only requests with correct token will be accepted!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 MULTIPLE BOT INSTANCES (5-6 Software Integration)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run multiple CryptoMagic instances, all sending to same webhook:

Terminal 1:
──────────
$ python3 ethmagic.py -f eth5.txt -v 100000 -n 4 \
    --worker-name app-scanner-1 \
    --webhook-url http://webhook-server.com/webhook

Terminal 2:
──────────
$ python3 ethmagic.py -f eth5.txt -v 100000 -n 4 \
    --worker-name app-scanner-2 \
    --webhook-url http://webhook-server.com/webhook

Terminal 3:
──────────
$ python3 ethmagic.py -f eth5.txt -v 100000 -n 4 \
    --worker-name app-scanner-3 \
    --webhook-url http://webhook-server.com/webhook

Single webhook server handles ALL three bots:
─────────────────────────────────────────────
$ python3 webhook_server.py

Webhook server receives:
  🔔 Received webhook: startup (app-scanner-1)
  🔔 Received webhook: startup (app-scanner-2)
  🔔 Received webhook: startup (app-scanner-3)

All send to Telegram, Discord, Slack simultaneously!

This is perfect for 5-6 software integration - they can all:
  - Send to same webhook
  - Webhook handles routing to different platforms
  - Different apps receive different formatted messages

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 FILES CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

webhook_server.py                 Ready-to-use webhook server (Flask)
WEBHOOK_INTEGRATION.md            Complete webhook documentation
webhook-quick-start.sh            This guide
ethmagic.py                        Updated with --webhook-url argument

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 TEST YOUR SETUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Check webhook server is running:
   $ curl http://localhost:3000/health
   
   Expected response:
   {
     "status": "ok",
     "telegram": true,
     "discord": false,
     "slack": false
   }

2. View webhook configuration:
   $ curl http://localhost:3000/config

3. Send test message via curl:
   $ curl -X POST http://localhost:3000/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "event_type": "startup",
       "data": {
         "worker_name": "test-bot",
         "formatted_message": "<b>Test message</b>"
       }
     }'

4. Check webhook logs:
   $ tail webhook_notifications.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ FALLBACK BEHAVIOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If webhook fails:
  ✅ Bot automatically falls back to direct Telegram API
  ✅ Messages are still sent (no data loss)
  ✅ Bot continues running normally
  ✅ Error logged to console

If both webhook and Telegram API fail:
  ❌ Notifications may be lost
  ✅ Bot continues running
  ✅ Error logged to console
  ✅ Address generation continues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Read full documentation:
   $ cat WEBHOOK_INTEGRATION.md

2. Deploy webhook to production:
   - Use Docker, cloud functions, or dedicated server
   - Configure Telegram, Discord, Slack credentials
   - Test with multiple bot instances

3. Integrate with your 5-6 software platforms:
   - Modify webhook_server.py to add custom APIs
   - Add message transformation for each platform
   - Implement message queuing/logging

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ YOU'RE READY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your CryptoMagic bot is now:
  ✅ Platform-agnostic (not locked to Telegram)
  ✅ Ready for multi-platform integration
  ✅ Scalable to 5-6 software platforms
  ✅ Using secure webhook architecture
  ✅ Production-ready

Questions? See WEBHOOK_INTEGRATION.md for complete guide!

═══════════════════════════════════════════════════════════════════════════════
EOF
