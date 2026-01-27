#!/usr/bin/env python3
"""
Setup Nginx first, SSL later when DNS is ready
"""

import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

SERVER_IP = "89.208.14.241"
SERVER_USER = "root"
SERVER_PASSWORD = "jypaPK0"
DOMAIN = "gymtrackerbot.ru"

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
print("Setting up Nginx (HTTP)")
print("=" * 60)
print()

# Stop cloudflared
print("[*] Stopping Cloudflare tunnel...")
exec_command("systemctl stop cloudflared-tunnel 2>&1 || true", print_output=False)
exec_command("systemctl disable cloudflared-tunnel 2>&1 || true", print_output=False)
print("[OK] Tunnel stopped")
print()

# Install Nginx
print("[*] Installing Nginx...")
exec_command("apt update -qq 2>&1", print_output=False)
code, _, _ = exec_command("which nginx", print_output=False)

if code != 0:
    exec_command("DEBIAN_FRONTEND=noninteractive apt install -y nginx 2>&1")
else:
    print("[OK] Nginx already installed")
print()

# Configure Nginx
print("[*] Configuring Nginx...")

nginx_config = f"""server {{
    listen 80;
    listen [::]:80;
    server_name {DOMAIN} www.{DOMAIN};
    
    location / {{
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Increase timeouts
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }}
}}
"""

sftp = client.open_sftp()
with sftp.file(f'/etc/nginx/sites-available/{DOMAIN}', 'w') as f:
    f.write(nginx_config)
sftp.close()

# Enable site
exec_command(f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/ 2>&1", print_output=False)
exec_command("rm -f /etc/nginx/sites-enabled/default 2>&1", print_output=False)

# Test config
code, out, err = exec_command("nginx -t 2>&1", print_output=False)
if code != 0:
    print("[ERROR] Nginx config test failed:")
    print(out)
    print(err)
    sys.exit(1)

print("[OK] Nginx configured")

# Restart Nginx
print("[*] Starting Nginx...")
exec_command("systemctl restart nginx 2>&1")
exec_command("systemctl enable nginx 2>&1", print_output=False)
print("[OK] Nginx running")
print()

# Check status
print("[*] Nginx status:")
exec_command("systemctl status nginx --no-pager -l | head -10")
print()

# Check DNS
print("[*] Checking DNS (might take 10-30 minutes to propagate)...")
code, out, err = exec_command(f"dig +short {DOMAIN} @8.8.8.8", print_output=False)
resolved_ip = out.strip().split('\n')[-1] if out.strip() else "not resolved"
print(f"   {DOMAIN} -> {resolved_ip}")
print(f"   Expected: {SERVER_IP}")

if resolved_ip == SERVER_IP:
    print("   [OK] DNS ready!")
else:
    print("   [WAIT] DNS not ready yet")

print()
print("=" * 60)
print("[SUCCESS] Nginx is running!")
print("=" * 60)
print()
print(f"App accessible at: http://{DOMAIN} (HTTP)")
print()
print("When DNS propagates (10-30 min), get SSL certificate:")
print("  python get_ssl.py")
print()

client.close()

