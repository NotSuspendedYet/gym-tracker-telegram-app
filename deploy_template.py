#!/usr/bin/env python3
"""
GymTracker Deploy Script Template
Copy this file to deploy.py and configure your settings.

Requirements: pip install paramiko
"""

import os
import sys
import time
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[ERROR] paramiko is not installed!")
    print("        Install it with: pip install paramiko")
    sys.exit(1)

# Configuration - SET THESE VALUES
SERVER_IP = os.environ.get("DEPLOY_SERVER_IP", "YOUR_SERVER_IP")
SERVER_USER = os.environ.get("DEPLOY_SERVER_USER", "root")
SERVER_PASSWORD = os.environ.get("DEPLOY_SERVER_PASSWORD", "YOUR_PASSWORD")
PROJECT_PATH = os.environ.get("DEPLOY_PROJECT_PATH", "/root/gym-tracker")

class SSHDeployer:
    def __init__(self):
        self.client = None
        self.sftp = None
        
    def connect(self):
        print("[*] Connecting to server...")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.client.connect(
                SERVER_IP,
                username=SERVER_USER,
                password=SERVER_PASSWORD,
                timeout=30
            )
            self.sftp = self.client.open_sftp()
            print("[OK] Connected successfully")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
    
    def exec_command(self, cmd, timeout=300, print_output=True):
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode('utf-8', errors='replace')
            err = stderr.read().decode('utf-8', errors='replace')
            
            if print_output and out.strip():
                print(out.strip())
            if print_output and err.strip() and exit_code != 0:
                print(f"Error: {err.strip()}")
            
            return exit_code, out, err
        except Exception as e:
            print(f"Command error: {e}")
            return -1, "", str(e)
    
    def mkdir_p(self, remote_path):
        try:
            self.sftp.stat(remote_path)
        except FileNotFoundError:
            parent = os.path.dirname(remote_path)
            if parent:
                self.mkdir_p(parent)
            try:
                self.sftp.mkdir(remote_path)
            except:
                pass
    
    def upload_file(self, local_path, remote_path):
        try:
            self.mkdir_p(os.path.dirname(remote_path))
            self.sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"Failed to upload {local_path}: {e}")
            return False
    
    def upload_directory(self, local_dir, remote_dir):
        local_path = Path(local_dir)
        
        for item in local_path.rglob('*'):
            if item.is_file():
                if any(part.startswith('.') for part in item.parts):
                    continue
                if 'build' in item.parts or '__pycache__' in item.parts:
                    continue
                if item.suffix in ['.class', '.pyc']:
                    continue
                
                relative = item.relative_to(local_path)
                remote_path = f"{remote_dir}/{relative}".replace('\\', '/')
                
                self.mkdir_p(os.path.dirname(remote_path))
                try:
                    self.sftp.put(str(item), remote_path)
                except Exception as e:
                    print(f"  Warning: Could not upload {relative}: {e}")
        
        return True

def deploy():
    print("=" * 60)
    print("GymTracker Deploy Script")
    print("=" * 60)
    print(f"Server: {SERVER_IP}")
    print(f"Remote path: {PROJECT_PATH}")
    print()
    
    if SERVER_IP == "YOUR_SERVER_IP" or SERVER_PASSWORD == "YOUR_PASSWORD":
        print("[ERROR] Please configure SERVER_IP and SERVER_PASSWORD!")
        print("        Edit this file or set environment variables:")
        print("        DEPLOY_SERVER_IP, DEPLOY_SERVER_USER, DEPLOY_SERVER_PASSWORD")
        return False
    
    deployer = SSHDeployer()
    
    try:
        if not deployer.connect():
            return False
        print()
        
        print("[*] Preparing project directory...")
        deployer.exec_command(f"mkdir -p {PROJECT_PATH}", print_output=False)
        print("[OK] Directory ready")
        print()
        
        print("[*] Uploading project files...")
        local_project = Path(__file__).parent.resolve()
        
        files_to_upload = [
            "docker-compose.yml",
            "Dockerfile", 
            "build.gradle.kts",
            "settings.gradle.kts",
        ]
        
        for filename in files_to_upload:
            local_file = local_project / filename
            if local_file.exists():
                print(f"    {filename}")
                remote_file = f"{PROJECT_PATH}/{filename}"
                if not deployer.upload_file(str(local_file), remote_file):
                    print(f"[ERROR] Failed to upload {filename}")
                    return False
        
        dirs_to_upload = ["src", "gradle"]
        for dir_name in dirs_to_upload:
            local_dir = local_project / dir_name
            if local_dir.exists():
                print(f"    {dir_name}/...")
                deployer.exec_command(f"rm -rf {PROJECT_PATH}/{dir_name}", print_output=False)
                deployer.upload_directory(str(local_dir), f"{PROJECT_PATH}/{dir_name}")
        
        print("[OK] Files uploaded successfully")
        print()
        
        print("[*] Stopping existing containers...")
        deployer.exec_command(f"cd {PROJECT_PATH} && docker compose down 2>&1 || true", print_output=False)
        print("[OK] Containers stopped (data preserved in volumes)")
        print()
        
        print("[*] Building and starting containers...")
        print("    This may take several minutes...")
        print()
        
        code, out, err = deployer.exec_command(
            f"cd {PROJECT_PATH} && docker compose up -d --build 2>&1",
            timeout=600
        )
        
        if code != 0:
            print("[ERROR] Deploy failed!")
            if err:
                print(f"Error: {err}")
            return False
        
        print()
        print("[OK] Containers started")
        print()
        
        print("[*] Waiting for application to start...")
        time.sleep(15)
        
        print("[*] Container status:")
        deployer.exec_command(f"cd {PROJECT_PATH} && docker compose ps")
        print()
        
        print("[*] Checking application health...")
        code, out, err = deployer.exec_command(
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/ 2>&1",
            print_output=False
        )
        
        if "200" in out or "302" in out:
            print("[OK] Application is running and responding!")
        else:
            print("[WARN] Application might need more time to start.")
            print("       Checking container logs...")
            deployer.exec_command(f"cd {PROJECT_PATH} && docker compose logs --tail=20 app 2>&1")
        
        print()
        print("=" * 60)
        print("[SUCCESS] Deploy completed!")
        print(f"Application URL: http://{SERVER_IP}:8080")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Deploy error: {e}")
        return False
    finally:
        deployer.disconnect()

def show_logs():
    deployer = SSHDeployer()
    try:
        if not deployer.connect():
            return
        print()
        print("[*] Container logs (last 100 lines):")
        print("-" * 60)
        deployer.exec_command(f"cd {PROJECT_PATH} && docker compose logs --tail=100 2>&1")
    finally:
        deployer.disconnect()

def check_status():
    deployer = SSHDeployer()
    try:
        if not deployer.connect():
            return
        print()
        print("[*] Container status:")
        deployer.exec_command(f"cd {PROJECT_PATH} && docker compose ps 2>&1")
    finally:
        deployer.disconnect()

def stop_containers():
    deployer = SSHDeployer()
    try:
        if not deployer.connect():
            return
        print()
        print("[*] Stopping containers...")
        deployer.exec_command(f"cd {PROJECT_PATH} && docker compose down 2>&1")
        print("[OK] Containers stopped (data preserved in volumes)")
    finally:
        deployer.disconnect()

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0 or args[0] == "deploy":
        success = deploy()
        sys.exit(0 if success else 1)
    elif args[0] == "logs":
        show_logs()
    elif args[0] == "status":
        check_status()
    elif args[0] == "stop":
        stop_containers()
    else:
        print("Usage: python deploy.py [command]")
        print()
        print("Commands:")
        print("  deploy   - Deploy the application (default)")
        print("  logs     - Show container logs")
        print("  status   - Check container status")
        print("  stop     - Stop containers (preserves data)")

