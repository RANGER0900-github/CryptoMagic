#!/usr/bin/env python3
"""
📱 Telegram Integration Verification Script
Verifies that all Telegram features are properly implemented in ethmagic.py
"""

import subprocess
import sys
import os

def check_syntax():
    """Check Python syntax"""
    print("🔍 Checking Python syntax...")
    result = subprocess.run(
        ["python3", "-m", "py_compile", "ethmagic.py"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Syntax check passed")
        return True
    else:
        print(f"❌ Syntax error: {result.stderr}")
        return False

def check_imports():
    """Check required imports"""
    print("\n🔍 Checking required imports...")
    imports = ['requests', 'pytz', 'hashlib', 'threading']
    missing = []
    
    for imp in imports:
        try:
            __import__(imp)
            print(f"✅ {imp} available")
        except ImportError:
            print(f"❌ {imp} NOT installed")
            missing.append(imp)
    
    return len(missing) == 0

def check_functions():
    """Check if all Telegram functions exist"""
    print("\n🔍 Checking Telegram functions...")
    with open('ethmagic.py', 'r') as f:
        content = f.read()
    
    functions = [
        'send_telegram_message',
        'send_telegram_file',
        'send_startup_message',
        'send_daily_stats',
        'file_monitor_thread'
    ]
    
    all_found = True
    for func in functions:
        if f"def {func}" in content:
            print(f"✅ {func}() found")
        else:
            print(f"❌ {func}() NOT found")
            all_found = False
    
    return all_found

def check_cli_args():
    """Check if --worker-name CLI argument exists"""
    print("\n🔍 Checking CLI arguments...")
    with open('ethmagic.py', 'r') as f:
        content = f.read()
    
    if "--worker-name" in content or "worker_name" in content:
        print("✅ --worker-name argument found")
        return True
    else:
        print("❌ --worker-name argument NOT found")
        return False

def check_telegram_constants():
    """Check if Telegram credentials are configured"""
    print("\n🔍 Checking Telegram configuration...")
    with open('ethmagic.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('TELEGRAM_BOT_TOKEN', 'Bot token'),
        ('TELEGRAM_CHAT_ID', 'Chat ID'),
        ('IST = pytz.timezone', 'IST timezone')
    ]
    
    all_found = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc} configured")
        else:
            print(f"❌ {desc} NOT configured")
            all_found = False
    
    return all_found

def check_integration_points():
    """Check if functions are called in main flow"""
    print("\n🔍 Checking integration points...")
    with open('ethmagic.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('send_startup_message(', 'Startup message call'),
        ('file_monitor_thread', 'File monitor thread start'),
        ('send_daily_stats(', 'Final stats send'),
        ('threading.Thread', 'Threading for file monitoring')
    ]
    
    all_found = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc} integrated")
        else:
            print(f"❌ {desc} NOT integrated")
            all_found = False
    
    return all_found

def check_help_output():
    """Check if --help shows new argument"""
    print("\n🔍 Checking help output...")
    result = subprocess.run(
        ["python3", "ethmagic.py", "--help"],
        capture_output=True,
        text=True
    )
    
    if "--worker-name" in result.stdout:
        print("✅ --worker-name appears in help")
        return True
    else:
        print("❌ --worker-name NOT in help output")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("📱 TELEGRAM INTEGRATION VERIFICATION")
    print("=" * 60)
    
    checks = [
        ("Syntax", check_syntax),
        ("Imports", check_imports),
        ("Functions", check_functions),
        ("CLI Arguments", check_cli_args),
        ("Telegram Config", check_telegram_constants),
        ("Integration Points", check_integration_points),
        ("Help Output", check_help_output),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"Result: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Telegram integration is ready!")
        print("\n📱 Quick test command:")
        print("   python3 ethmagic.py -f eth5.txt -v 100000 -n 2 --worker-name test")
        print("\n🔍 You should see:")
        print("   1. Startup message in Telegram (within 2 seconds)")
        print("   2. Live progress in console")
        print("   3. Press Ctrl+C to send final stats to Telegram")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
