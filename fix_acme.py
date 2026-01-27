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
    err = stderr.read().decode('utf-8', errors='replace')
    
    if print_output:
        if out.strip():
            print(out.strip())
    
    return exit_code, out, err

print("[*] Creating webroot directory...")
exec_command("mkdir -p /var/www/html/.well-known/acme-challenge", print_output=False)
exec_command("chown -R www-data:www-data /var/www/html", print_output=False)
exec_command("chmod -R 755 /var/www/html", print_output=False)
print("[OK] Directory created")
print()

print("[*] Updating Nginx config...")

nginx_config = """server {
    listen 80;
    listen [::]:80;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    # ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }
    
    # Proxy to app
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

sftp = client.open_sftp()
with sftp.file('/etc/nginx/sites-available/gymtrackerbot.ru', 'w') as f:
    f.write(nginx_config)
sftp.close()

print("[OK] Config updated")

print("[*] Testing Nginx config...")
code, out, err = exec_command("nginx -t 2>&1", print_output=False)
if code == 0:
    print("[OK] Config valid")
else:
    print("[ERROR] Config invalid:")
    print(out)
    print(err)
    client.close()
    sys.exit(1)

print("[*] Reloading Nginx...")
exec_command("systemctl reload nginx 2>&1", print_output=False)
print("[OK] Nginx reloaded")
print()

print("[*] Getting SSL certificate (attempt 2)...")
code, out, err = exec_command(
    "certbot --nginx -d gymtrackerbot.ru -d www.gymtrackerbot.ru --non-interactive --agree-tos --email admin@gymtrackerbot.ru --redirect 2>&1",
    timeout=300
)

if code == 0:
    print()
    print("=" * 60)
    print("[SUCCESS] SSL certificate obtained!")
    print("=" * 60)
    print()
    print("Your app: https://gymtrackerbot.ru")
    print()
else:
    print()
    print("[ERROR] Still failed. Trying with standalone mode...")
    print()
    
    # Stop nginx temporarily
    exec_command("systemctl stop nginx", print_output=False)
    
    # Try standalone
    code, out, err = exec_command(
        "certbot certonly --standalone -d gymtrackerbot.ru -d www.gymtrackerbot.ru --non-interactive --agree-tos --email admin@gymtrackerbot.ru 2>&1",
        timeout=300
    )
    
    if code == 0:
        print("[OK] Certificate obtained via standalone!")
        
        # Update nginx for SSL
        nginx_ssl = """server {
    listen 80;
    listen [::]:80;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name gymtrackerbot.ru www.gymtrackerbot.ru;
    
    ssl_certificate /etc/letsencrypt/live/gymtrackerbot.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gymtrackerbot.ru/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
"""
        sftp = client.open_sftp()
        with sftp.file('/etc/nginx/sites-available/gymtrackerbot.ru', 'w') as f:
            f.write(nginx_ssl)
        sftp.close()
        
        exec_command("nginx -t 2>&1", print_output=False)
        exec_command("systemctl start nginx", print_output=False)
        
        print()
        print("=" * 60)
        print("[SUCCESS] SSL is ready!")
        print("=" * 60)
        print()
        print("Your app: https://gymtrackerbot.ru")
        print()
    else:
        # Start nginx back
        exec_command("systemctl start nginx", print_output=False)
        print("[ERROR] Failed both methods")
        print(out)

client.close()
