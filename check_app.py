#!/usr/bin/env python3
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

SERVER_IP = "89.208.14.241"
SERVER_USER = "root"
SERVER_PASSWORD = "jypaPK0"

def exec_command(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    return out.strip()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

print("=" * 60)
print("Checking Application and Tunnel")
print("=" * 60)
print()

print("[*] Docker containers status:")
print(exec_command(client, "cd /root/gym-tracker && docker compose ps"))
print()

print("[*] Testing app on localhost:8080:")
result = exec_command(client, "curl -s -o /dev/null -w 'HTTP: %{http_code}' http://localhost:8080/ 2>&1 || echo 'FAILED'")
print(f"   {result}")
print()

print("[*] Cloudflare tunnel status:")
print(exec_command(client, "systemctl status cloudflared-tunnel --no-pager -l | head -20"))
print()

print("[*] Recent tunnel logs:")
print(exec_command(client, "journalctl -u cloudflared-tunnel -n 15 --no-pager"))

client.close()

