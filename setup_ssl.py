#!/usr/bin/env python3
"""
Setup Nginx + Let's Encrypt SSL for GymTracker
"""

import sys
import io
import time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[ERROR] paramiko is not installed!")
    sys.exit(1)

SERVER_IP = "89.208.14.241"
SERVER_USER = "root"
SERVER_PASSWORD = "jypaPK0"
DOMAIN = "gymtrackerbot.ru"
EMAIL = "admin@gymtrackerbot.ru"  # For Let's Encrypt notifications

def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    return client

def exec_command(client, cmd, print_output=True, timeout=300):
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

def main():
    print("=" * 60)
    print("Setting up Nginx + SSL for gymtrackerbot.ru")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        # Check DNS
        print("[*] Checking DNS resolution...")
        code, out, err = exec_command(client, f"dig +short {DOMAIN} @8.8.8.8", print_output=False)
        
        resolved_ip = out.strip().split('\n')[-1] if out.strip() else ""
        
        if resolved_ip == SERVER_IP:
            print(f"[OK] DNS resolved: {DOMAIN} -> {SERVER_IP}")
        else:
            print(f"[WARN] DNS not yet propagated")
            print(f"      Current: {resolved_ip}")
            print(f"      Expected: {SERVER_IP}")
            print()
            print("      Wait 5-10 minutes and try again with:")
            print("      python setup_ssl.py")
            print()
            print("      Or continue anyway (SSL cert will fail but Nginx will work)")
            response = input("Continue? (y/n): ").lower()
            if response != 'y':
                print("Exiting. Run again when DNS is ready.")
                return False
        
        print()
        
        # Stop cloudflared tunnel (we don't need it anymore)
        print("[*] Stopping Cloudflare tunnel...")
        exec_command(client, "systemctl stop cloudflared-tunnel", print_output=False)
        exec_command(client, "systemctl disable cloudflared-tunnel", print_output=False)
        print("[OK] Tunnel stopped")
        print()
        
        # Install Nginx
        print("[*] Installing Nginx...")
        exec_command(client, "apt update -qq", print_output=False)
        code, _, _ = exec_command(client, "which nginx", print_output=False)
        
        if code != 0:
            exec_command(client, "apt install -y nginx")
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
    }}
}}
"""
        
        sftp = client.open_sftp()
        with sftp.file(f'/etc/nginx/sites-available/{DOMAIN}', 'w') as f:
            f.write(nginx_config)
        sftp.close()
        
        # Enable site
        exec_command(client, f"ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/", print_output=False)
        exec_command(client, "rm -f /etc/nginx/sites-enabled/default", print_output=False)
        
        # Test config
        code, _, _ = exec_command(client, "nginx -t", print_output=False)
        if code != 0:
            print("[ERROR] Nginx config test failed")
            return False
        
        print("[OK] Nginx configured")
        
        # Restart Nginx
        print("[*] Starting Nginx...")
        exec_command(client, "systemctl restart nginx")
        exec_command(client, "systemctl enable nginx", print_output=False)
        print("[OK] Nginx running")
        print()
        
        # Install Certbot
        print("[*] Installing Certbot...")
        code, _, _ = exec_command(client, "which certbot", print_output=False)
        
        if code != 0:
            exec_command(client, "apt install -y certbot python3-certbot-nginx")
        else:
            print("[OK] Certbot already installed")
        print()
        
        # Get SSL certificate
        print("[*] Obtaining SSL certificate...")
        print("    This may take a minute...")
        
        code, out, err = exec_command(client,
            f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email {EMAIL} --redirect",
            timeout=300
        )
        
        if code == 0:
            print("[OK] SSL certificate obtained!")
            print()
            print("=" * 60)
            print("[SUCCESS] Setup complete!")
            print("=" * 60)
            print()
            print(f"Your app is now available at:")
            print(f"  https://{DOMAIN}")
            print(f"  https://www.{DOMAIN}")
            print()
            print("SSL certificate will auto-renew every 90 days.")
            print()
            print("Next step: Configure your Telegram bot with this URL")
            return True
        else:
            print()
            print("[WARN] SSL certificate failed (DNS might not be ready)")
            print("       Your app is available at:")
            print(f"       http://{DOMAIN} (HTTP only, no SSL)")
            print()
            print("       Wait 10-30 minutes for DNS to propagate, then run:")
            print("       python setup_ssl.py retry")
            print()
            return False
        
    finally:
        client.close()

def retry_ssl():
    """Retry getting SSL certificate"""
    print("=" * 60)
    print("Retrying SSL certificate...")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        code, out, err = exec_command(client,
            f"certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email {EMAIL} --redirect",
            timeout=300
        )
        
        if code == 0:
            print()
            print("[SUCCESS] SSL certificate obtained!")
            print(f"Your app: https://{DOMAIN}")
        else:
            print()
            print("[ERROR] Still failing. Check DNS:")
            exec_command(client, f"dig +short {DOMAIN} @8.8.8.8")
    finally:
        client.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) > 0 and args[0] == "retry":
        retry_ssl()
    else:
        main()

