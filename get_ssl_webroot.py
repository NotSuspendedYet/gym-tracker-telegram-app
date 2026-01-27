#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.208.14.241", username="root", password="jypaPK0", timeout=30)

def exec_command(cmd, print_output=True, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace')
    
    if print_output and out.strip():
        print(out.strip())
    
    return exit_code, out

print("=" * 60)
print("Getting SSL via webroot method")
print("=" * 60)
print()

print("[*] Getting certificate...")
code, out = exec_command(
    "certbot certonly --webroot -w /var/www/html -d gymtrackerbot.ru -d www.gymtrackerbot.ru --non-interactive --agree-tos --email admin@gymtrackerbot.ru --preferred-challenges http 2>&1",
    timeout=300
)

if code == 0:
    print()
    print("[OK] Certificate obtained!")
    print()
    
    # Update Nginx for SSL
    nginx_ssl = """server {
    listen 80;
    listen [::]:80;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    ssl_certificate /etc/letsencrypt/live/gymtrackerbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gymtrackerbot.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
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
    }
}
"""
    
    print("[*] Updating Nginx config for SSL...")
    sftp = client.open_sftp()
    with sftp.file('/etc/nginx/sites-available/gymtrackerbot.ru', 'w') as f:
        f.write(nginx_ssl)
    sftp.close()
    
    code, _ = exec_command("nginx -t 2>&1", print_output=False)
    if code != 0:
        print("[ERROR] Nginx config invalid!")
        client.close()
        sys.exit(1)
    
    print("[*] Reloading Nginx...")
    exec_command("systemctl reload nginx 2>&1", print_output=False)
    
    print()
    print("=" * 60)
    print("[SUCCESS] SSL is ready!")
    print("=" * 60)
    print()
    print("Your app: https://gymtrackerbot.ru")
    print()
    print("SSL certificate auto-renews every 90 days")
    print()
    print("Next: Configure your Telegram bot!")
    print("  1. Open @BotFather")
    print("  2. /mybots -> your bot")
    print("  3. Bot Settings -> Menu Button")
    print("  4. Enter: https://gymtrackerbot.ru")
    print()
else:
    print()
    print("[ERROR] Failed to get certificate")
    print()
    # Check if it's IPv6 issue
    print("[*] Checking IPv6...")
    exec_command("ip -6 addr show 2>&1 | grep -v 'lo\\|::1'")

client.close()
