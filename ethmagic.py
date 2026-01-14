import ctypes
import time
import argparse  # Using argparse instead of optparse
import multiprocessing
from bip_utils import Bip32Slip10Secp256k1, Bip39MnemonicGenerator, Bip39SeedGenerator, Bip39WordsNum, EthAddrEncoder
from rich import print
import os
import sys


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


def Main(worker_id, filename, logpx, thco, add, lock):
    """Worker function that generates keys and reports progress.
    worker_id: 1-based ID for this worker process
    filename, logpx, thco: parsed and typed (ints where appropriate)
    add: set of target addresses
    lock: multiprocessing.Lock instance for synchronization
    """
    # Local counters and timers
    z = 0
    fu = 0
    logp = 0
    start_perf = time.perf_counter()
    cpu_monitor = CPUUsage()

    while True:
        z += 1
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
            safe_print(lock, f"[green1][+] MATCH ADDRESS FOUND BY WORKER {worker_id} :[/green1] [white]{addr}[/white]")
            safe_print(lock, f"PrivateKey (Byte) : [green1]{PrivateKeyBytes}[/green1]\n[gold1]{mnemonic}[/gold1]\n[red1]MasterKey (Byte) : [/red1][green1]{MasterKey}[/green1]")
            # Write match to disk under lock to avoid interleaving
            try:
                if lock is not None:
                    with lock:
                        with open('FoundMATCHAddr.txt', 'a') as f:
                            f.write(f"{addr}\n{PrivateKeyBytes}\n{mnemonic}\n{MasterKey}\n------------------------- MMDRZA.Com -------------------\n")
                else:
                    with open('FoundMATCHAddr.txt', 'a') as f:
                        f.write(f"{addr}\n{PrivateKeyBytes}\n{mnemonic}\n{MasterKey}\n------------------------- MMDRZA.Com -------------------\n")
            except Exception:
                # Ignore file write errors but report them
                safe_print(lock, f"[red]Failed to write FoundMATCHAddr.txt from worker {worker_id}[/red]")
        elif z % logpx == 0:
            logp += logpx
            safe_print(lock, f"[red][[green1]+[/green1]][GENERATED[white] {logp}[/white] ETH ADDR][WITH [white]{thco} THREAD(S)[/white]][rate:[white]{rate:.2f} addr/s[/white] | {sec_per_k:.3f} s/K][CPU:[white]{cpu:.1f}%[/white]][/red]\n[red][[green1]{PrivateKeyBytes.upper()}[/green1]][/red]")
            # Show a concise mnemonic preview (first 6 words) and indicate truncation
            mnemonic_preview = " ".join(Words24.split()[0:6]) + " ... (truncated)"
            safe_print(lock, f"[red][MasterKey : [white]{MasterKey.upper()}[/white]][/red]\n[white on red3][MNEMONIC : {mnemonic_preview}][/white on red3]")
        else:
            # Live short progress line (overwrites in terminal)
            safe_print(lock, f"[red][-][ GENERATED [cyan]{z}[/cyan] ETH ADDR ][FOUND:[white]{fu}[/white]][THREAD:[cyan]{thco}[/cyan]][rate:[white]{rate:.2f} addr/s[/white]][CPU:[white]{cpu:.1f}%[/white]][WORKER:[cyan]{worker_id}[/cyan]][/red]", end="\r", flush=True)


if __name__ == '__main__':
    # Parse command-line options in the main process and launch workers
    parser = argparse.ArgumentParser(description="Ethereum Address Finder Script")

    parser.add_argument('-f', '--file', dest="filenameEth", required=True,
                        help="Ethereum Rich Address File With Type Format .TXT [Example: -f eth5.txt]")
    parser.add_argument('-v', '--view', dest="ViewPrint", required=True,
                        help="Print after generated this number of addresses and report")
    parser.add_argument('-n', '--thread', dest="ThreadCount", required=True,
                        help="Total worker processes to spawn")

    args = parser.parse_args()
    filename = args.filenameEth
    logpx = int(args.ViewPrint)
    thco = int(args.ThreadCount)

    # Read targets once in the parent and share as an immutable set
    with open(filename) as f:
        add = set(f.read().split())

    # Create a lock for synchronized console output and file writes
    lock = multiprocessing.Lock()

    jobs = []
    try:
        for i in range(thco):
            p = multiprocessing.Process(target=Main, args=(i + 1, filename, logpx, thco, add, lock), daemon=True)
            jobs.append(p)
            p.start()

        # Keep main process alive and wait for children (they run forever until interrupted)
        for p in jobs:
            p.join()
    except KeyboardInterrupt:
        # Gracefully terminate all workers
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
    except Exception as e:
        safe_print(lock, f"[red]Unexpected error in launcher: {e}[/red]")
        for p in jobs:
            try:
                p.terminate()
            except Exception:
                pass
