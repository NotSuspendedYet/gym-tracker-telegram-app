#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko
import time

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
print("Getting SSL certificate (final attempt)")
print("=" * 60)
print()

print("[*] Waiting for DNS to propagate (5 seconds)...")
time.sleep(5)

print("[*] Checking DNS...")
code, out = exec_command("dig +short gymtrackerbot.ru AAAA @8.8.8.8", print_output=False)
if out.strip():
    print(f"[WARN] IPv6 still present: {out.strip()}")
    print("       Waiting 30 more seconds...")
    time.sleep(30)

print("[*] Getting certificate with acme.sh (Let's Encrypt)...")
code, out = exec_command(
    "/root/.acme.sh/acme.sh --set-default-ca --server letsencrypt && /root/.acme.sh/acme.sh --issue -d gymtrackerbot.ru -d www.gymtrackerbot.ru -w /var/www/html --force --debug 2>&1",
    timeout=300
)

success = "cert.pem" in out or "Cert success" in out or code == 0

if success:
    print()
    print("[OK] Certificate obtained!")
    print()
    
    # Install certificate
    print("[*] Installing certificate...")
    exec_command("mkdir -p /etc/ssl/private /etc/ssl/certs", print_output=False)
    exec_command(
        "/root/.acme.sh/acme.sh --installcert -d gymtrackerbot.ru --key-file /etc/ssl/private/gymtrackerbot.ru.key --fullchain-file /etc/ssl/certs/gymtrackerbot.ru.crt 2>&1"
    )
    
    # Update Nginx
    nginx_ssl = """server {
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
    
    print("[*] Updating Nginx config...")
    sftp = client.open_sftp()
    with sftp.file('/etc/nginx/sites-available/gymtrackerbot.ru', 'w') as f:
        f.write(nginx_ssl)
    sftp.close()
    
    code, _ = exec_command("nginx -t 2>&1", print_output=False)
    if code == 0:
        exec_command("systemctl reload nginx 2>&1", print_output=False)
        
        print()
        print("=" * 60)
        print("[SUCCESS] HTTPS IS READY!")
        print("=" * 60)
        print()
        print("Your app: https://gymtrackerbot.ru")
        print()
        print("Certificate renews automatically via cron")
        print()
        print("=" * 60)
        print("CONFIGURE TELEGRAM BOT:")
        print("=" * 60)
        print()
        print("1. Open @BotFather in Telegram")
        print("2. Send: /mybots")
        print("3. Select your bot")
        print("4. Bot Settings -> Menu Button")
        print("5. Enter URL: https://gymtrackerbot.ru")
        print()
        print("=" * 60)
        print("DONE! Your GymTracker is live!")
        print("=" * 60)
    else:
        print("[ERROR] Nginx config invalid")
        exec_command("nginx -t 2>&1")
else:
    print()
    print("[ERROR] Certificate failed")
    print()
    print("Let's check what's blocking...")
    exec_command("curl -v http://gymtrackerbot.ru/.well-known/acme-challenge/test 2>&1 | head -20")

client.close()
