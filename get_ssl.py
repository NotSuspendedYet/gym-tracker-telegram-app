#!/usr/bin/env python3
"""
Get SSL certificate for gymtrackerbot.ru
"""

import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

SERVER_IP = "89.208.14.241"
SERVER_USER = "root"
SERVER_PASSWORD = "jypaPK0"
DOMAIN = "gymtrackerbot.ru"
EMAIL = "admin@gymtrackerbot.ru"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

def exec_command(cmd, print_output=True, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    
    if print_output:
        if out.strip():
            print(out.strip())
        if err.strip() and exit_code != 0:
            print(f"Error: {err.strip()}")
    
    return exit_code, out, err

print("=" * 60)
print("Getting SSL certificate for gymtrackerbot.ru")
print("=" * 60)
print()

# Check DNS
print("[*] Checking DNS...")
code, out, err = exec_command(f"dig +short {DOMAIN} @8.8.8.8", print_output=False)
resolved_ip = out.strip().split('\n')[-1] if out.strip() else ""

print(f"   {DOMAIN} -> {resolved_ip}")
print(f"   Expected: {SERVER_IP}")

if resolved_ip != SERVER_IP:
    print()
    print("[ERROR] DNS not ready yet!")
    print(f"        {DOMAIN} resolves to: {resolved_ip}")
    print(f"        Expected: {SERVER_IP}")
    print()
    print("Wait 10-30 minutes and try again.")
    print()
    print("Check DNS status in reg.ru panel")
    client.close()
    sys.exit(1)

print("[OK] DNS ready!")
print()

# Install Certbot
print("[*] Installing Certbot...")
code, _, _ = exec_command("which certbot", print_output=False)

if code != 0:
    exec_command("DEBIAN_FRONTEND=noninteractive apt install -y certbot python3-certbot-nginx 2>&1")
else:
    print("[OK] Certbot already installed")
print()

# Get SSL certificate
print("[*] Obtaining SSL certificate...")
print("    This may take a minute...")
print()

code, out, err = exec_command(
    f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email {EMAIL} --redirect 2>&1",
    timeout=300
)

if code == 0:
    print()
    print("=" * 60)
    print("[SUCCESS] SSL certificate obtained!")
    print("=" * 60)
    print()
    print(f"Your app is now available at:")
    print(f"  https://{DOMAIN}")
    print(f"  https://www.{DOMAIN}")
    print()
    print("SSL certificate will auto-renew every 90 days.")
    print()
    print("=" * 60)
    print("Next step: Configure your Telegram bot!")
    print("=" * 60)
    print()
    print("1. Open @BotFather in Telegram")
    print("2. /mybots -> select your bot")
    print("3. Bot Settings -> Menu Button")
    print(f"4. Enter: https://{DOMAIN}")
    print()
else:
    print()
    print("[ERROR] Failed to get SSL certificate!")
    print()
    print("Possible reasons:")
    print("- DNS still propagating")
    print("- Port 80 not accessible")
    print("- Domain name configuration issue")
    print()
    print("Check logs above for details")

client.close()

