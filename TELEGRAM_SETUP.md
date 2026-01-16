# 📱 Telegram Integration Setup Guide

## Overview
CryptoMagic now includes **24/7 Telegram monitoring and reporting** for unattended operation. The bot will:
- 📢 Send startup notification with worker name and configuration
- 📊 Send daily stats at end of day (or on shutdown)
- 🎉 Instantly alert when addresses are found (send FoundMATCHAddr.txt file)
- ⏱️ Run continuously in background without user interaction

## Prerequisites

### 1. Install Dependencies
```bash
pip install pytz requests
```

### 2. Telegram Bot Setup (Already Configured)
The bot credentials are pre-configured:
- **Bot Token**: `6668621875:AAHaIDS59aIPpWYf3JkWZuAkOaRatknClG0`
- **Chat ID**: `1702319284`
- **Timezone**: Asia/Kolkata (IST)

## Usage Examples

### Basic Usage with Default Worker Name
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3
```
- Worker name defaults to: `CryptoBot`
- Telegram messages will show: "Worker Name: CryptoBot"

### Custom Worker Name
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 3 --worker-name robo1
```
- Worker name will be: `robo1`
- Useful for running multiple instances simultaneously

### Multiple Workers with Different Names
Terminal 1:
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 --worker-name worker-farm-1
```

Terminal 2:
```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 --worker-name worker-farm-2
```

Each will send separate startup and daily stats messages!

## Telegram Messages

### 📢 Startup Message
Sent immediately after bot starts:
```
🤖 Bot Started
Date: 01 January 2024
Time: 10:30 AM (IST)

⚙️ Configuration:
Worker Name: robo1
Target File: eth5.txt
Workers: 4

✅ Ready to hunt addresses!
```

### 📊 Daily Stats Report
Sent when bot shuts down (Ctrl+C) or at end of day:
```
📊 Daily Stats Report
Date: 01 January 2024

👤 Worker: robo1
📁 Target: eth5.txt

📈 Statistics:
Generated: 1,234,567 addresses
Avg Rate: 750.5 addr/s
Time: 27m 15s
Found: 🎉 2 matches
Avg CPU: 45.2%
Workers: 4

See you tomorrow! 🚀
```

### 🎉 Instant Match Alert
Sent immediately when an address match is detected:
```
🎉 MATCH FOUND!
01 January 2024 10:45 AM IST
[File: FoundMATCHAddr.txt is attached]
```

## Features

### 🟢 Real-time Match Detection
- Monitors `FoundMATCHAddr.txt` every 5 seconds
- Uses MD5 hash-based change detection (no performance impact)
- Sends Telegram message + file attachment instantly
- Works even if you're away from computer

### 👤 Worker Identification
- Use `--worker-name` to identify different worker instances
- Useful for tracking multiple bots running on different machines
- Each worker sends its own startup and daily stats

### 🌐 IST Timezone
- All timestamps automatically converted to IST (Asia/Kolkata)
- No configuration needed, automatic timezone handling

### 📍 24/7 Operation
- Background file monitoring thread (daemon process)
- Runs independently of main generation loop
- Automatically stops when main process terminates

## Advanced Usage

### Running 24/7 on Server
```bash
# Run in background with nohup
nohup python3 ethmagic.py -f eth5.txt -v 100000 -n 8 --worker-name mainbot &

# Check logs
tail -f nohup.out
```

### Running with Screen/Tmux
```bash
# Using screen
screen -S cryptobot
python3 ethmagic.py -f eth5.txt -v 100000 -n 8 --worker-name mainbot

# Detach: Ctrl+A then D
# Reattach: screen -r cryptobot
```

### Multiple Independent Workers
```bash
# Terminal 1 - Fast aggressive bot
python3 ethmagic.py -f eth5.txt -v 500000 -n 8 --worker-name aggressive-bot &

# Terminal 2 - Steady scanning bot  
python3 ethmagic.py -f eth5.txt -v 100000 -n 4 --worker-name steady-bot &

# Both send separate Telegram updates!
```

## Performance Notes

- ✅ **File Monitoring**: Minimal overhead (check every 5 seconds, uses MD5 hash)
- ✅ **Telegram API Calls**: Non-blocking (thread-based)
- ✅ **Memory**: Negligible (only tracks file hash)
- ✅ **Network**: Only sends when needed (startup, shutdown, matches)

## Troubleshooting

### No Telegram Messages Received
1. Check internet connection
2. Verify bot token and chat ID are correct (they're pre-configured)
3. Check Telegram app privacy settings
4. Review error output in console

### Messages Show Wrong Timezone
- IST timezone is automatically applied
- If your server has different timezone, it will convert to IST

### File Monitoring Not Working
- Ensure `FoundMATCHAddr.txt` is in same directory as ethmagic.py
- File monitoring is daemon thread (non-blocking)
- Check console for any error messages

## Command Reference

```bash
python3 ethmagic.py [OPTIONS]

Options:
  -f, --file FILE              Target addresses file (required)
  -v, --verbose COUNT          Progress update interval [default: 100000]
  -n, --threads WORKERS        Number of worker processes [default: 2]
  -r, --report-interval SECS   Throttle live output every N seconds [default: 1]
  --worker-name NAME           Worker identifier for Telegram [default: CryptoBot]
```

## Example Scenarios

### Scenario 1: Hunt for Known Whales
```bash
python3 ethmagic.py -f eth5.txt -v 1000000 -n 6 --worker-name whale-hunter
```
- Large progress interval (1M addresses)
- More workers for speed
- Receives startup and daily stats on Telegram

### Scenario 2: Distributed Hunting
```bash
# Machine 1 (High CPU)
python3 ethmagic.py -f eth5.txt -v 500000 -n 16 --worker-name farm-east &

# Machine 2 (Medium CPU)
python3 ethmagic.py -f eth5.txt -v 500000 -n 8 --worker-name farm-west &

# Machine 3 (Low CPU)
python3 ethmagic.py -f eth5.txt -v 500000 -n 4 --worker-name farm-south &
```
- Separate Telegram notifications for each
- Can monitor all from single Telegram chat

### Scenario 3: 24/7 Monitoring
```bash
# Start in background
nohup python3 ethmagic.py -f eth5.txt -v 100000 -n 8 --worker-name nightshift &

# Receive alerts on phone even while sleeping
# Get daily stats each morning
# Instant notification if match found
```

## Privacy & Security

⚠️ **Important**: Bot token and Chat ID are stored in the code. If sharing:
1. Regenerate bot token before sharing code
2. Use environment variables (optional enhancement)
3. Restrict Telegram bot permissions

## Questions?

For issues or feature requests:
1. Check console output for error messages
2. Verify internet connectivity
3. Ensure dependencies are installed: `pip install pytz requests`

---

**Happy hunting! 🚀**
