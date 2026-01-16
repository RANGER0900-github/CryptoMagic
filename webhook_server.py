#!/usr/bin/env python3
"""
🪝 Simple Webhook Server for CryptoMagic
Receives notifications and forwards to Telegram (or other platforms)
Run: python3 webhook_server.py
Then use: python3 ethmagic.py ... --webhook-url http://localhost:3000/webhook
"""

from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration (set these via environment variables or directly)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '6668621875:AAHaIDS59aIPpWYf3JkWZuAkOaRatknClG0')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '1702319284')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', None)
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK', None)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', None)

# Message log file
LOG_FILE = 'webhook_notifications.log'

def log_notification(event_type, data):
    """Log all notifications to file."""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"[{datetime.now().isoformat()}] Event: {event_type}\n")
            f.write(json.dumps(data, indent=2))
            f.write(f"\n{'='*80}\n")
    except Exception as e:
        print(f"Error logging notification: {e}")

def send_to_telegram(message, parse_mode="HTML"):
    """Send message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode
        }, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Telegram: Message sent")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram exception: {e}")
        return False

def send_to_discord(message):
    """Send message to Discord."""
    if not DISCORD_WEBHOOK:
        return False
    
    try:
        # Convert HTML to Discord markdown
        discord_message = message.replace('<b>', '**').replace('</b>', '**').replace('<code>', '`').replace('</code>', '`').replace('<i>', '_').replace('</i>', '_')
        
        response = requests.post(DISCORD_WEBHOOK, json={
            "content": discord_message
        }, timeout=10)
        
        if response.status_code in [200, 204]:
            print(f"✅ Discord: Message sent")
            return True
        else:
            print(f"❌ Discord error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Discord exception: {e}")
        return False

def send_to_slack(message):
    """Send message to Slack."""
    if not SLACK_WEBHOOK:
        return False
    
    try:
        # Convert HTML to Slack markdown
        slack_message = message.replace('<b>', '*').replace('</b>', '*').replace('<code>', '`').replace('</code>', '`').replace('<i>', '_').replace('</i>', '_')
        
        response = requests.post(SLACK_WEBHOOK, json={
            "text": slack_message
        }, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Slack: Message sent")
            return True
        else:
            print(f"❌ Slack error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Slack exception: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main webhook endpoint for CryptoMagic notifications."""
    
    # Validate secret token if configured
    if WEBHOOK_SECRET:
        token = request.args.get('token')
        if token != WEBHOOK_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        event_type = data.get('event_type')
        event_data = data.get('data', {})
        
        print(f"\n🔔 Received webhook: {event_type}")
        
        # Log the notification
        log_notification(event_type, data)
        
        # Handle different event types
        if event_type == 'startup':
            message = event_data.get('formatted_message', '')
            print(f"   Worker: {event_data.get('worker_name')}")
            print(f"   Target: {event_data.get('target_file')}")
            
        elif event_type == 'daily_stats':
            message = event_data.get('formatted_message', '')
            print(f"   Generated: {event_data.get('total_generated'):,} addresses")
            print(f"   Rate: {event_data.get('average_rate'):.1f} addr/s")
            print(f"   Matches: {event_data.get('total_matches')}")
            
        elif event_type == 'match_found':
            message = "🎉 MATCH FOUND!\n\n"
            content = event_data.get('content', '')
            # Limit content display
            if len(content) > 500:
                message += f"{content[:500]}...\n(File truncated, see full content in log)"
            else:
                message += content
            print(f"   Matches detected: {len(content.splitlines())} addresses")
            
        elif event_type == 'message':
            message = event_data.get('content', '')
            print(f"   Message: {message[:50]}...")
        
        else:
            return jsonify({"error": f"Unknown event type: {event_type}"}), 400
        
        # Send to configured platforms
        platforms_sent = []
        
        # Always try Telegram (main platform)
        if send_to_telegram(message):
            platforms_sent.append("Telegram")
        
        # Try Discord if configured
        if DISCORD_WEBHOOK and send_to_discord(message):
            platforms_sent.append("Discord")
        
        # Try Slack if configured
        if SLACK_WEBHOOK and send_to_slack(message):
            platforms_sent.append("Slack")
        
        if platforms_sent:
            print(f"✅ Sent to: {', '.join(platforms_sent)}")
            return jsonify({
                "status": "ok",
                "event_type": event_type,
                "platforms_sent": platforms_sent
            }), 200
        else:
            return jsonify({"status": "failed", "error": "No platforms configured"}), 500
            
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    status = {
        "status": "ok",
        "telegram": bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID),
        "discord": bool(DISCORD_WEBHOOK),
        "slack": bool(SLACK_WEBHOOK)
    }
    return jsonify(status), 200

@app.route('/config', methods=['GET'])
def config():
    """Show current configuration (sanitized)."""
    return jsonify({
        "telegram_configured": bool(TELEGRAM_BOT_TOKEN),
        "discord_configured": bool(DISCORD_WEBHOOK),
        "slack_configured": bool(SLACK_WEBHOOK),
        "webhook_secret_configured": bool(WEBHOOK_SECRET),
        "log_file": LOG_FILE,
        "endpoints": {
            "webhook": "/webhook (POST)",
            "health": "/health (GET)",
            "config": "/config (GET)"
        }
    }), 200

if __name__ == '__main__':
    # Read port from environment variable (set by ethmagic.py) or use default
    port = int(os.environ.get('FLASK_PORT', 3000))
    
    print("=" * 80)
    print("🪝 CryptoMagic Webhook Server")
    print("=" * 80)
    
    print("\n📡 Configured Platforms:")
    print(f"  {'✅' if TELEGRAM_BOT_TOKEN else '❌'} Telegram")
    print(f"  {'✅' if DISCORD_WEBHOOK else '⭕'} Discord (optional)")
    print(f"  {'✅' if SLACK_WEBHOOK else '⭕'} Slack (optional)")
    
    print(f"\n🔐 Security: {'✅ Secret token required' if WEBHOOK_SECRET else '⭕ No secret token'}")
    
    print(f"\n📝 Logging to: {LOG_FILE}")
    
    print(f"\n🚀 Starting server on http://0.0.0.0:{port}")
    print("\n📌 Use in CryptoMagic:")
    print("   python3 ethmagic.py -f eth5.txt -v 100000 -n 3 \\")
    print(f"     --webhook-url http://localhost:{port}/webhook")
    
    print(f"\n📊 Health check: curl http://localhost:{port}/health")
    print(f"📊 View config: curl http://localhost:{port}/config")
    
    print("\n" + "=" * 80 + "\n")
    
    # Start server
    app.run(host='0.0.0.0', port=port, debug=False)
