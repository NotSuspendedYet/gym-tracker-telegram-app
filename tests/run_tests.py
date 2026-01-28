#!/usr/bin/env python3
"""
Быстрый запуск API тестов GymTracker

Использование:
  python tests/run_tests.py                    # Тесты на localhost:8080
  python tests/run_tests.py https://gymtrackerbot.ru  # Тесты на продакшене
"""

import sys
import os

# Добавляем путь к тестам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_api import GymTrackerAPITester

def main():
    # Получаем URL из аргументов или используем дефолт
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = os.environ.get('API_BASE_URL', 'http://localhost:8080')
    
    print(f"\n{'='*50}")
    print(f"GymTracker API Tests")
    print(f"URL: {base_url}")
    print(f"{'='*50}\n")
    
    tester = GymTrackerAPITester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
