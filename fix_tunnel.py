#!/usr/bin/env python3
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko
import time

SERVER_IP = "89.208.14.241"
SERVER_USER = "root"
SERVER_PASSWORD = "jypaPK0"

def exec_command(client, cmd, print_output=True, timeout=60):
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
print("Fixing Cloudflare Tunnel - switching to HTTP/2")
print("=" * 60)
print()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)

# Update service to use http2 protocol
print("[*] Updating service configuration...")

service_content = """[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8080 --protocol http2 --no-autoupdate
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

sftp = client.open_sftp()
with sftp.file('/etc/systemd/system/cloudflared-tunnel.service', 'w') as f:
    f.write(service_content)
sftp.close()

print("[OK] Configuration updated")

print("[*] Reloading systemd...")
exec_command(client, "systemctl daemon-reload", print_output=False)

print("[*] Restarting tunnel...")
exec_command(client, "systemctl restart cloudflared-tunnel", print_output=False)

print("[*] Waiting for tunnel to connect...")
time.sleep(8)

print()
print("[*] Tunnel status:")
exec_command(client, "systemctl status cloudflared-tunnel --no-pager -l | head -15")

print()
print("[*] Fetching tunnel URL...")
code, out, err = exec_command(client,
    "journalctl -u cloudflared-tunnel -n 50 --no-pager | grep -o 'https://[a-zA-Z0-9-]*\\.trycloudflare\\.com' | tail -1",
    print_output=False
)

tunnel_url = out.strip()

if tunnel_url and tunnel_url.startswith('https://'):
    print()
    print("=" * 60)
    print("[SUCCESS] Tunnel is working!")
    print("=" * 60)
    print()
    print(f"HTTPS URL: {tunnel_url}")
    print()
    print("Try accessing this URL in your browser now!")
    print()
else:
    print()
    print("[*] Checking recent logs for URL...")
    exec_command(client, "journalctl -u cloudflared-tunnel -n 30 --no-pager")

client.close()

