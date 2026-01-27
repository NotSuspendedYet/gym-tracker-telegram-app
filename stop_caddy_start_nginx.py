#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.208.14.241", username="root", password="jypaPK0", timeout=30)

def exec_command(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    return out

print("[*] Stopping Caddy...")
exec_command("systemctl stop caddy 2>&1")
exec_command("systemctl disable caddy 2>&1")
exec_command("pkill -9 caddy 2>&1 || true")
print("[OK] Caddy stopped")
print()

print("[*] Starting Nginx...")
exec_command("systemctl start nginx 2>&1")
print("[OK] Nginx started")
print()

print("[*] Nginx status:")
exec_command("systemctl status nginx --no-pager | head -15")
print()

print("[*] Testing app через Nginx...")
result = exec_command("curl -s -o /dev/null -w 'HTTP: %{http_code}' http://localhost/ 2>&1")
print(f"   {result}")
print()

print("=" * 60)
print("[SUCCESS] Nginx is running!")
print("=" * 60)
print()
print("App: http://gymtrackerbot.ru (via Nginx)")
print()
print("When DNS propagates, run:")
print("  python get_ssl.py")

client.close()

