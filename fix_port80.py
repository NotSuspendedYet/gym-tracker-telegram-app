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
    return stdout.read().decode('utf-8', errors='replace').strip()

print("[*] Checking what's on port 80...")
print(exec_command("lsof -i :80 || netstat -tulpn | grep :80"))
print()

print("[*] Stopping Apache/other services...")
exec_command("systemctl stop apache2 2>&1 || true")
exec_command("systemctl disable apache2 2>&1 || true")
exec_command("systemctl stop httpd 2>&1 || true")
exec_command("pkill -9 -f 'python.*http.server' 2>&1 || true")
print("[OK] Done")
print()

print("[*] Starting Nginx...")
print(exec_command("systemctl restart nginx 2>&1"))
print()

print("[*] Nginx status:")
print(exec_command("systemctl status nginx --no-pager -l | head -10"))

client.close()

