#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko
import urllib.request

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

print("=" * 60)
print("Checking port 80 accessibility")
print("=" * 60)
print()

print("[*] Checking from server itself...")
result = exec_command("curl -s -o /dev/null -w 'HTTP: %{http_code}' http://localhost/ 2>&1")
print(f"   Local: {result}")
print()

print("[*] Checking firewall rules...")
exec_command("ufw status 2>&1 || iptables -L -n | head -20")
print()

print("[*] Checking what's listening on port 80...")
exec_command("netstat -tulpn | grep :80")
print()

print("[*] DNS records...")
exec_command("dig +short gymtrackerbot.ru @8.8.8.8")
exec_command("dig +short www.gymtrackerbot.ru @8.8.8.8")
print()

print("[*] Checking from external (via Python)...")
try:
    response = urllib.request.urlopen("http://gymtrackerbot.ru", timeout=10)
    print(f"   External: HTTP {response.status} OK!")
except Exception as e:
    print(f"   External: FAILED - {e}")
print()

print("[*] Nginx access log (last 5)...")
exec_command("tail -5 /var/log/nginx/access.log 2>&1 || echo 'No logs yet'")
print()

print("[*] Nginx error log (last 5)...")
exec_command("tail -5 /var/log/nginx/error.log 2>&1 || echo 'No errors'")

client.close()
