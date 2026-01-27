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
print("USER DATA FOR: Никита (526515096)")
print("=" * 70)
print()

print("[1] User info:")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT * FROM users WHERE telegram_id = 526515096;" 2>&1""")
print()

print("[2] User workouts:")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT id, date, created_at FROM workouts WHERE telegram_user_id = 526515096 ORDER BY date DESC;" 2>&1""")
print()

print("[3] Workout details (ID 39 - with 5 exercises):")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT we.id, e.name as exercise, (SELECT COUNT(*) FROM exercise_sets WHERE workout_exercise_id = we.id) as sets FROM workout_exercises we JOIN exercises e ON we.exercise_id = e.id WHERE we.workout_id = 39;" 2>&1""")
print()

print("[4] Sets from workout 39:")
print("-" * 70)
exec_command("""cd /root/gym-tracker && docker compose exec -T db psql -U gymtracker -d gymtracker -c "SELECT es.set_number, es.weight, es.reps, e.name FROM exercise_sets es JOIN workout_exercises we ON es.workout_exercise_id = we.id JOIN exercises e ON we.exercise_id = e.id WHERE we.workout_id = 39 ORDER BY we.id, es.set_number;" 2>&1""")
print()

client.close()
