#!/usr/bin/env python3
"""
Setup Cloudflare Quick Tunnel for GymTracker
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

def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SERVER_IP, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    return client

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

def main():
    print("=" * 60)
    print("Setting up Cloudflare Tunnel")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        # Stop any existing cloudflared services
        print("[*] Stopping existing cloudflared services...")
        exec_command(client, "pkill cloudflared", print_output=False)
        exec_command(client, "systemctl stop cloudflared", print_output=False)
        time.sleep(2)
        
        # Create systemd service file
        print("[*] Creating systemd service...")
        
        service_content = """[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8080 --no-autoupdate
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file
        sftp = client.open_sftp()
        with sftp.file('/etc/systemd/system/cloudflared-tunnel.service', 'w') as f:
            f.write(service_content)
        sftp.close()
        
        print("[OK] Service file created")
        
        # Reload systemd
        print("[*] Reloading systemd...")
        exec_command(client, "systemctl daemon-reload")
        
        # Enable and start service
        print("[*] Starting tunnel service...")
        exec_command(client, "systemctl enable cloudflared-tunnel")
        exec_command(client, "systemctl start cloudflared-tunnel")
        
        print()
        print("[*] Waiting for tunnel to connect...")
        time.sleep(5)
        
        # Get the tunnel URL from logs
        print()
        print("[*] Fetching tunnel URL...")
        code, out, err = exec_command(client, 
            "journalctl -u cloudflared-tunnel -n 50 --no-pager | grep -o 'https://[a-zA-Z0-9-]*\\.trycloudflare\\.com' | head -1",
            print_output=False
        )
        
        tunnel_url = out.strip()
        
        if tunnel_url and tunnel_url.startswith('https://'):
            print()
            print("=" * 60)
            print("[SUCCESS] Tunnel is running!")
            print("=" * 60)
            print()
            print(f"HTTPS URL: {tunnel_url}")
            print()
            print("This URL is persistent and will work as long as the service is running.")
            print("The tunnel automatically restarts on server reboot.")
            print()
            print("Commands:")
            print("  python setup_quick_tunnel.py status  - Check status")
            print("  python setup_quick_tunnel.py restart - Restart tunnel")
            print("  python setup_quick_tunnel.py logs    - View logs")
            print()
            print("=" * 60)
            print()
            print("Next step: Configure your Telegram bot with this URL")
            
            return tunnel_url
        else:
            print()
            print("[*] Tunnel is starting... Checking logs:")
            exec_command(client, "journalctl -u cloudflared-tunnel -n 30 --no-pager")
            print()
            print("[INFO] If URL not shown above, wait 10 seconds and run:")
            print("      python setup_quick_tunnel.py status")
        
    finally:
        client.close()

def check_status():
    print("=" * 60)
    print("Tunnel Status")
    print("=" * 60)
    print()
    
    client = connect_ssh()
    
    try:
        print("[*] Service status:")
        exec_command(client, "systemctl status cloudflared-tunnel --no-pager")
        
        print()
        print("[*] Tunnel URL:")
        code, out, err = exec_command(client,
            "journalctl -u cloudflared-tunnel -n 50 --no-pager | grep -o 'https://[a-zA-Z0-9-]*\\.trycloudflare\\.com' | head -1",
            print_output=False
        )
        
        tunnel_url = out.strip()
        if tunnel_url:
            print(f"   {tunnel_url}")
        else:
            print("   URL not found in logs yet")
        
    finally:
        client.close()

def restart_tunnel():
    print("[*] Restarting tunnel...")
    client = connect_ssh()
    try:
        exec_command(client, "systemctl restart cloudflared-tunnel")
        print("[OK] Tunnel restarted")
        print("[*] Wait 5 seconds then check status")
    finally:
        client.close()

def show_logs():
    print("=" * 60)
    print("Tunnel Logs")
    print("=" * 60)
    print()
    client = connect_ssh()
    try:
        exec_command(client, "journalctl -u cloudflared-tunnel -n 50 --no-pager")
    finally:
        client.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0:
        main()
    elif args[0] == "status":
        check_status()
    elif args[0] == "restart":
        restart_tunnel()
    elif args[0] == "logs":
        show_logs()
    else:
        print("Usage: python setup_quick_tunnel.py [command]")
        print()
        print("Commands:")
        print("  (no args) - Setup tunnel")
        print("  status    - Check status and show URL")
        print("  restart   - Restart tunnel")
        print("  logs      - Show logs")

