#!/usr/bin/env python3
"""
Setup Cloudflare Tunnel for GymTracker
"""

import sys
import io

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

def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    return client

def exec_command(client, cmd, print_output=True):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
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
    print("Cloudflare Tunnel Setup")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        # Check if cloudflared is installed
        print("[*] Checking if cloudflared is installed...")
        code, out, err = exec_command(client, "which cloudflared", print_output=False)
        
        if code == 0:
            print("[OK] cloudflared is already installed")
            exec_command(client, "cloudflared version")
        else:
            print("[*] Installing cloudflared...")
            # Download and install
            exec_command(client, """
                cd /tmp && \
                wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && \
                chmod +x cloudflared-linux-amd64 && \
                mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
            """)
            print("[OK] cloudflared installed")
        
        print()
        print("=" * 60)
        print("Next steps:")
        print("=" * 60)
        print()
        print("1. Go to: https://one.dash.cloudflare.com/")
        print("   - Sign up / Log in (free)")
        print()
        print("2. Go to: Zero Trust > Networks > Tunnels")
        print("   - Click 'Create a tunnel'")
        print("   - Choose 'Cloudflared'")
        print("   - Give it a name: 'gym-tracker'")
        print("   - Copy the token (starts with 'eyJ...')")
        print()
        print("3. Configure:")
        print("   - Public hostname: (your-subdomain)")
        print("   - Domain: (leave default or add custom)")
        print("   - Service: http://localhost:8080")
        print()
        print("4. Run this script again with your token:")
        print("   python setup_cloudflare_tunnel.py <YOUR_TOKEN>")
        print()
        print("=" * 60)
        
    finally:
        client.close()

def install_tunnel(token):
    print("=" * 60)
    print("Installing Cloudflare Tunnel")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        # Install the tunnel service
        print("[*] Installing tunnel service...")
        exec_command(client, f"cloudflared service install {token}")
        
        print("[*] Starting tunnel...")
        exec_command(client, "systemctl start cloudflared")
        exec_command(client, "systemctl enable cloudflared")
        
        print()
        print("[*] Checking tunnel status...")
        exec_command(client, "systemctl status cloudflared --no-pager")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Tunnel installed and running!")
        print("=" * 60)
        print()
        print("Your app should now be accessible via HTTPS URL")
        print("Check Cloudflare dashboard for the URL")
        
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
        install_tunnel(token)
    else:
        main()

