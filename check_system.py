#!/usr/bin/env python3
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("89.208.14.241", username="root", password="jypaPK0", timeout=30)

def exec_command(cmd):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    if out:
        print(out)
    return out

print("=" * 70)
print("SYSTEM DIAGNOSTICS")
print("=" * 70)
print()

print("[1] Docker containers status:")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose ps")
print()

print("[2] App container logs (last 30 lines):")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose logs --tail=30 app")
print()

print("[3] Database container logs (last 20 lines):")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose logs --tail=20 db")
print()

print("[4] Checking database connection:")
print("-" * 70)
result = exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c '\\dt' 2>&1")
print()

print("[5] Counting records in database:")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c 'SELECT COUNT(*) as users FROM users;' 2>&1")
exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c 'SELECT COUNT(*) as workouts FROM workouts;' 2>&1")
exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c 'SELECT COUNT(*) as exercises FROM workout_exercises;' 2>&1")
exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c 'SELECT COUNT(*) as sets FROM exercise_sets;' 2>&1")
print()

print("[6] Docker volumes:")
print("-" * 70)
exec_command("docker volume ls | grep gym")
exec_command("docker volume inspect gym-tracker_postgres_data 2>&1 | grep -A 5 Mountpoint")
print()

print("[7] App responding:")
print("-" * 70)
exec_command("curl -s -o /dev/null -w 'HTTP Status: %{http_code}\\n' http://localhost:8080/")
print()

print("[8] Recent user activity (last 5 users):")
print("-" * 70)
exec_command("cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c 'SELECT telegram_id, first_name, last_name, created_at FROM users ORDER BY created_at DESC LIMIT 5;' 2>&1")
print()

print("[9] Container uptime:")
print("-" * 70)
exec_command("docker ps --format 'table {{.Names}}\\t{{.Status}}' | grep gym")
print()

print("[10] System resources:")
print("-" * 70)
exec_command("docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}' | grep gym")
print()

client.close()
