#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.208.14.241", username="root", password="jypaPK0", timeout=30)

def exec_command(cmd, print_output=True):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    
    if print_output and out:
        print(out)
    
    return exit_code, out

print("=" * 70)
print("FIXING CACHE ISSUE")
print("=" * 70)
print()

print("[*] Updating Nginx configuration to disable caching...")

nginx_config = """server {
    listen 80;
    listen [::]:80;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    ssl_certificate /etc/ssl/certs/gymtrackerbot.ru.crt;
    ssl_certificate_key /etc/ssl/private/gymtrackerbot.ru.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Disable all caching
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always;
    add_header Pragma "no-cache" always;
    add_header Expires "0" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        
        # Disable proxy caching
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }
}
"""

sftp = client.open_sftp()
with sftp.file('/etc/nginx/sites-available/gymtrackerbot.ru', 'w') as f:
    f.write(nginx_config)
sftp.close()

print("[OK] Configuration updated")
print()

print("[*] Testing Nginx configuration...")
code, out = exec_command("nginx -t 2>&1", print_output=False)

if code == 0:
    print("[OK] Configuration valid")
    
    print("[*] Reloading Nginx...")
    exec_command("systemctl reload nginx 2>&1", print_output=False)
    print("[OK] Nginx reloaded")
    print()
    
    print("=" * 70)
    print("[SUCCESS] Cache headers added!")
    print("=" * 70)
    print()
    print("Changes made:")
    print("  • Added 'Cache-Control: no-store, no-cache' header")
    print("  • Added 'Pragma: no-cache' header")
    print("  • Added 'Expires: 0' header")
    print("  • Disabled proxy caching")
    print()
    print("This will prevent Telegram WebApp from caching old sessions.")
    print()
    print("Test by:")
    print("  1. Close Telegram app completely")
    print("  2. Reopen Telegram")
    print("  3. Open your bot")
    print("  4. Should work correctly now!")
    print()
else:
    print("[ERROR] Configuration invalid:")
    print(out)

client.close()
