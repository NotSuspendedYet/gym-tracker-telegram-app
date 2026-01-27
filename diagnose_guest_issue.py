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

print("=" * 70)
print("DIAGNOSING 'GUEST' ISSUE")
print("=" * 70)
print()

print("[1] Checking Nginx cache settings:")
print("-" * 70)
exec_command("grep -i 'proxy_cache\\|cache' /etc/nginx/sites-available/gymtrackerbot.ru || echo 'No caching directives found'")
print()

print("[2] Recent app logs (auth/user creation):")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose logs --tail=50 app 2>&1 | grep -E 'Auth|User|Гость|Guest|POST /api/auth' | tail -20")
print()

print("[3] Check if app serves different content based on User-Agent:")
print("-" * 70)
print("Testing from server with different User-Agents...")
result1 = exec_command("curl -s http://localhost:8080/ -H 'User-Agent: Mozilla' | grep -o 'const tg.*WebApp' | head -1")
print(f"Browser UA: {result1 if result1 else 'OK'}")
result2 = exec_command("curl -s http://localhost:8080/ -H 'User-Agent: Telegram' | grep -o 'const tg.*WebApp' | head -1")
print(f"Telegram UA: {result2 if result2 else 'OK'}")
print()

print("[4] Checking if there's any session/cookie issue:")
print("-" * 70)
exec_command("grep -i 'session\\|cookie' /etc/nginx/sites-available/gymtrackerbot.ru || echo 'No session/cookie config'")
print()

print("[5] App logs - last 10 authentication attempts:")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose logs app 2>&1 | grep 'POST /api/auth' | tail -10")
print()

print("[6] Checking Nginx access log for recent requests:")
print("-" * 70)
exec_command("tail -20 /var/log/nginx/access.log | grep -E 'GET / |POST /api/auth'")
print()

client.close()
