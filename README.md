# 🔐 CryptoMagic - Ethereum Address Hunter & Key Finder

<div align="center">

![image alt](https://github.com/jay37749/CryptoMagic-BruteForce-Ethereum-PrivateKey-Finder-Mnemonic-Cracker/blob/61db055447e5b4e76c61d974d89099b9ac0ca88a/CRYPTOCURRENCY-MAGIC-BRUTEFORCE-ETHEREUM-FINDER%20(732%20x%20279%20px).png)

**A powerful tool to generate Ethereum addresses from BIP-39 mnemonics and hunt for matches against known address lists**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#-features) • [Installation](#-installation) • [Usage](#-quick-start) • [Examples](#-usage-examples) • [Performance](#-performance-tips) • [Security](#-security-notes)

</div>

---

## 🚀 Features

- ⚡ **Multi-threaded Address Generation** - Spawn multiple workers to generate addresses in parallel
- 📊 **Real-time Metrics** - Monitor addr/s rates, CPU usage, and progress continuously
- 🎯 **Smart Reporting** - Auto-configure reporting intervals based on measured throughput or set manually
- 🔍 **Fast Address Matching** - Check generated addresses against a list of target addresses
- 💾 **Secure Match Logging** - Found matches are logged with private keys and mnemonics to disk
- 🛠️ **Flexible Configuration** - Control reporting frequency, worker count, and CPU monitoring window
- 🌍 **Cross-Platform** - Works on Windows, macOS, and Linux

---

## 📦 Installation

### Prerequisites
- Python 3.12 or higher

### Step 1: Clone the Repository

```bash
git clone https://github.com/jay37749/CryptoMagic-BruteForce-Ethereum-PrivateKey-Finder-Mnemonic-Cracker.git
cd CryptoMagic-BruteForce-Ethereum-PrivateKey-Finder-Mnemonic-Cracker
```

### Step 2: Install Dependencies

**For Linux / macOS:**
```bash
pip3 install bip_utils rich
```

**For Windows:**
```bash
pip install bip_utils rich
```

---

## 🎯 Quick Start

### Basic Usage

```bash
python3 ethmagic.py -f eth5.txt -v 1000 -n 2
```

**Command Breakdown:**
- `-f eth5.txt` → Target address file
- `-v 1000` → Report after generating 1,000 addresses
- `-n 2` → Use 2 worker processes

---

## 📚 Arguments Reference

| Argument | Short | Type | Required | Default | Description |
|----------|-------|------|----------|---------|-------------|
| `--file` | `-f` | string | ✅ Yes | - | Path to target address file (e.g., `eth5.txt`) |
| `--view` | `-v` | integer | ✅ Yes | - | Report interval (addresses per report) |
| `--thread` | `-n` | integer | ✅ Yes | - | Number of worker processes to spawn |
| `--worker-name` | - | string | ⭕ No | `worker-1` | Custom worker identifier for logging |
| `--webhook-url` | - | string | ⭕ No | - | Custom webhook URL (disables auto-startup) |
| `--port` | - | integer | ⭕ No | `3000` | Port for auto-starting webhook server |

---

## 🎓 Usage Examples

### Example 1: Basic Single-Worker Hunt
Simple address generation with reporting every 5,000 addresses:

```bash
python3 ethmagic.py -f eth5.txt -v 5000 -n 1
```

**Output Preview:**
```
[-][ GENERATED 5000 ETH ADDR ][FOUND:0][THREAD:1][rate:320.45 addr/s][CPU:45.2%][WORKER:1]
[-][ GENERATED 10000 ETH ADDR ][FOUND:0][THREAD:1][rate:325.30 addr/s][CPU:42.1%][WORKER:1]
```

---

### Example 2: Multi-Worker High-Speed Run
Optimal performance with 2 workers, generating ~750 combined addr/s:

```bash
python3 ethmagic.py -f eth5.txt -v 10000 -n 2
```

**Expected Performance:**
- Combined Rate: **~620-750 addr/s**
- CPU Usage: **80-100%** (optimal utilization)

---

### Example 3: Aggressive Address Generation
Large report interval for minimal console I/O overhead (best throughput):

```bash
python3 ethmagic.py -f eth5.txt -v 100000 -n 4
```

**Use Case:** Maximize raw throughput when you don't need frequent status updates.

---

### Example 4: Conservative Reporting
Small intervals for frequent updates (monitor progress closely):

```bash
python3 ethmagic.py -f eth5.txt -v 500 -n 2
```

**Use Case:** Real-time monitoring and quick feedback.

---

### Example 5: Auto-Starting Webhook Server with Telegram Notifications
Start the bot with automatic webhook server on a custom port with real-time Telegram updates:

```bash
python3 ethmagic.py -f eth5.txt -v 50000 -n 4 --worker-name final-demo --port 5689
```

**Features:**
- 🚀 Webhook server auto-starts on port 5689
- 📱 Sends startup notification to Telegram (with configuration details)
- 📊 Sends daily stats reports (addresses generated, rate, CPU%, time elapsed)
- 🎯 Sends match notifications immediately when found
- ✅ Graceful shutdown (sends shutdown message, kills server automatically)

**What Happens:**
```
🚀 Starting webhook server on port 5689...
✅ Webhook server started on port 5689
📱 Sending startup notification to Telegram...
[Bot starts generating addresses...]
```

---

## 📱 Telegram Integration & Webhook Notifications

### Quick Setup

1. **Set Telegram Credentials** (environment variables):
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"
```

2. **Run with Auto Webhook**:
```bash
python3 ethmagic.py -f eth5.txt -v 50000 -n 4 --port 5689
```

That's it! You'll receive:
- ✅ **Startup Message** - Bot configuration and worker details
- 📊 **Daily Stats** - Addresses generated, generation rate, CPU usage, time elapsed
- 🎯 **Match Alerts** - Immediate notification when a match is found
- 🛑 **Shutdown Message** - Graceful shutdown with final statistics

### Advanced: Custom Webhook URL

If you're running the webhook server separately or on a different machine:

```bash
# Terminal 1: Start webhook server manually
python3 webhook_server.py

# Terminal 2: Start bot with custom webhook URL
python3 ethmagic.py -f eth5.txt -v 50000 -n 4 --worker-name demo --webhook-url http://localhost:3000/webhook
```

### Multi-Platform Support

The webhook system supports Telegram (default) plus optional Discord and Slack webhooks. Configure in `webhook_server.py`:

```python
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_token')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK', None)
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK', None)
```

---

## 📊 Performance Tips

### Choosing Worker Count
- **4 CPU cores → Use 2-3 workers** for best stability and throughput
- **8+ CPU cores → Can use 4-6 workers** (test your system)
- **System headroom → Use fewer workers** if running other applications

### Throughput Optimization
| Setting | Impact | Example |
|---------|--------|---------|
| Large `-v` value | ↑ Speed (less I/O) | `-v 100000` |
| Small `-v` value | ↓ Speed (more I/O) | `-v 500` |
| Increase workers | ↑ Total rate (if CPU allows) | `-n 4` |
| Decrease workers | ↑ Per-worker stability | `-n 1` |

### Benchmark Your System

```bash
# Single-worker baseline
time python3 ethmagic.py -f eth5.txt -v 10000 -n 1

# Two-worker test
time python3 ethmagic.py -f eth5.txt -v 20000 -n 2

# Compare total time and final rate
```

---

## 📁 Input File Format

The target address file (e.g., `eth5.txt`) should contain Ethereum addresses, one per line or space-separated:

```
0x1234567890123456789012345678901234567890
0xabcdefabcdefabcdefabcdefabcdefabcdefabcd
0xfedcbafedcbafedcbafedcbafedcbafedcbafed
```

---

## 📄 Output & Logging

### Console Output
- **Live progress line:** Updated every generation (carriage return `\r`)
- **Periodic report:** Full details at intervals set by `-v`

### FoundMATCHAddr.txt
When a match is found, the following is written to `FoundMATCHAddr.txt`:
```
0xMatchedAddress
PrivateKeyHex
24WordMnemonic
MasterKeyHex
------------------------- MMDRZA.Com -------------------
```

---

## 🔐 Security & Legal Notes

⚠️ **DISCLAIMER:**
- This tool is for **educational and authorized testing purposes only**
- **Unauthorized access** to funds or systems is **illegal**
- The probability of randomly finding a valid private key is astronomically low
- Use responsibly and comply with all applicable laws

---

## 🛠️ Other Coin Scripts

This repository includes similar tools for other cryptocurrencies:

```bash
# Polkadot (DOT)
python dotmagic.py -f dot1000.txt -v 1000 -n 32

# Dogecoin (DOGE)
python dogemagic.py -f doge5.txt -v 1000 -n 32

# Tron (TRX)
python trxmagic.py -f trx_rich.txt -v 1000 -n 128

# Ripple (XRP)
python xrpmagic.py -f xrp_rich.txt -v 10000 -n 8
```

---

## 💡 How It Works

1. **Mnemonic Generation** - Creates random 24-word BIP-39 mnemonics
2. **Seed Derivation** - Uses BIP-32/BIP-44 to derive keys from seed
3. **Address Generation** - Generates Ethereum addresses from derived keys (path: `m/44'/60'/0'/0/0`)
4. **Address Matching** - Compares each generated address against the target list
5. **Match Logging** - Saves full details when a match is found

---

## 🧪 Testing & Benchmarking

### Verify Installation
```bash
python3 ethmagic.py --help
```

### Quick 10-Second Test
```bash
python3 ethmagic.py -f eth5.txt -v 1000 -n 1
# Let it run for ~10 seconds, then Ctrl+C
```

---

## 📞 Support & Contributing

- **Report Issues:** Open an issue on GitHub
- **Contribute:** Pull requests are welcome!
- **Questions:** Refer to the examples section above

---

## 💝 Support the Developer

If you find this tool useful:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X7X612R0JE)

**Donation Address (USDT):** `0x6d9454534f20907638ef3ca33f5f8d3a185e1fce`

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ by jay37749**

[⬆ Back to Top](#-cryptomagic---ethereum-address-hunter--key-finder)

</div>

---

## 🌐 Other Coin Variants

Similar tools for other cryptocurrencies are included in this repository:

```bash
# Polkadot (DOT)
python dotmagic.py -f dot1000.txt -v 1000 -n 2

# Dogecoin (DOGE)  
python dogemagic.py -f doge5.txt -v 1000 -n 2

# Tron (TRX)
python trxmagic.py -f trx_rich.txt -v 1000 -n 2

# Ripple (XRP)
python xrpmagic.py -f xrp_rich.txt -v 10000 -n 2
```

Each follows the same pattern: `-f` (file), `-v` (report interval), `-n` (workers).

---

## 🏗️ Architecture Overview

The tool uses a **multi-process architecture** for parallel address generation:

- **Master Process:** Parses arguments and spawns worker processes
- **Worker Processes:** Each worker generates random mnemonics, derives Ethereum addresses, and checks against target list
- **Synchronization:** Uses multiprocessing.Lock for thread-safe file writes and console output
- **Metrics:** Real-time CPU monitoring with rolling-window averaging
- **BIP Standards:** BIP-39 (mnemonics) → BIP-32/44 (key derivation) → Ethereum address generation

Key Libraries:
- `bip_utils` - BIP-39/32/44 implementation
- `rich` - Beautiful console formatting
- `multiprocessing` - Parallel worker management
- `psutil` (optional) - Advanced CPU monitoring

---

## ✅ Troubleshooting

### Q: "ImportError: No module named 'bip_utils'"
**A:** Install dependencies: `pip3 install bip_utils rich`

### Q: "AttributeError: module 'ctypes' has no attribute 'windll' (on Linux/Mac)"
**A:** This is expected and handled automatically. The script detects your OS and uses appropriate console title methods.

### Q: "No matches found - is the tool working?"
**A:** Yes! Matches are extremely rare. To verify:
1. Create a test file `test.txt` with your generated address
2. Run `python3 ethmagic.py -f test.txt -v 1000 -n 1` and check for a match

---

## 🧪 Development & Testing

### Run All Worker Tests
```bash
# Verify script works with different worker counts
for workers in 1 2 3 4; do
  echo "Testing with $workers workers..."
  timeout 5 python3 ethmagic.py -f eth5.txt -v 10000 -n $workers
done
```

### Benchmark on Your System
```bash
# Measure addresses/second for your CPU
python3 ethmagic.py -f eth5.txt -v 50000 -n 2 &
# Wait for ~30 seconds and note the final rate
# (Higher is better; typical: 500-1000 addr/s)
```

---

## 📖 Additional Resources

- **BIP-39 Standard:** https://github.com/trezor/python-mnemonic
- **BIP-32 Derivation:** https://github.com/trezor/python-mnemonic
- **Ethereum Addresses:** https://ethereum.org/en/developers/docs/accounts/

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 💰 Donations & Support

If you found this tool helpful and want to support development:

**USDT Address (ERC-20):** `0x6d9454534f20907638ef3ca33f5f8d3a185e1fce`

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X7X612R0JE)

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Portions of this code use:
- `bip_utils` (BSD License)
- `rich` (MIT License)

---

## ⚖️ Legal Notice

This tool is for **educational and authorized security testing only**. Unauthorized use is illegal. The author assumes no liability for misuse.

---

<div align="center">

**⭐ If you found this helpful, please star the repository! ⭐**

Made with ❤️ by [jay37749](https://github.com/jay37749)

[Back to Top](#-cryptomagic---ethereum-address-hunter--key-finder)

</div>
