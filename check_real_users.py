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
print("CHECKING REAL USERS DATA")
print("=" * 70)
print()

print("[1] Users with REAL Telegram IDs (not timestamp):")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT telegram_id, first_name, last_name, username, created_at FROM users WHERE telegram_id < 1000000000000 ORDER BY created_at DESC LIMIT 10;" 2>&1""")
print()

print("[2] Total 'Guest' users vs Real users:")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT CASE WHEN first_name = 'Гость' THEN 'Guest' ELSE 'Real User' END as user_type, COUNT(*) FROM users GROUP BY user_type;" 2>&1""")
print()

print("[3] Workouts from REAL users (if any):")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT w.id, w.telegram_user_id, u.first_name, w.date, (SELECT COUNT(*) FROM workout_exercises WHERE workout_id = w.id) as exercises FROM workouts w LEFT JOIN users u ON w.telegram_user_id = u.telegram_id WHERE w.telegram_user_id < 1000000000000 ORDER BY w.date DESC LIMIT 5;" 2>&1""")
print()

print("[4] When was the FIRST real user created:")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT MIN(created_at) as first_real_user, MAX(created_at) as last_real_user FROM users WHERE telegram_id < 1000000000000;" 2>&1""")
print()

client.close()
