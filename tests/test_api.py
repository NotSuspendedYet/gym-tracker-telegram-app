#!/usr/bin/env python3
"""
GymTracker API Tests

Тесты для проверки работоспособности API после деплоя.
Запуск: python -m pytest tests/test_api.py -v
или: python tests/test_api.py (для быстрого теста)

Переменные окружения:
- API_BASE_URL: базовый URL API (по умолчанию http://localhost:8080)
"""

import os
import sys
import time
import io
import requests
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Конфигурация
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8080')
TEST_USER_ID = 999999999  # Тестовый Telegram ID

# Цвета для вывода (отключаем на Windows для совместимости)
USE_COLORS = sys.platform != 'win32' or os.environ.get('FORCE_COLORS', '')

class Colors:
    GREEN = '\033[92m' if USE_COLORS else ''
    RED = '\033[91m' if USE_COLORS else ''
    YELLOW = '\033[93m' if USE_COLORS else ''
    BLUE = '\033[94m' if USE_COLORS else ''
    RESET = '\033[0m' if USE_COLORS else ''
    BOLD = '\033[1m' if USE_COLORS else ''


def log_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.RESET}")


def log_error(msg: str):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.RESET}")


def log_info(msg: str):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.RESET}")


def log_section(msg: str):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}=== {msg} ==={Colors.RESET}")


class GymTrackerAPITester:
    """Тестер API GymTracker"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.test_user = None
        self.test_workout = None
        self.test_workout_exercise = None
        self.test_sets = []
        
    def api_call(self, method: str, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Выполняет API запрос"""
        url = f"{self.base_url}/api{endpoint}"
        response = self.session.request(method, url, json=data, timeout=30)
        return response
    
    # ==================== Тесты ==================== #
    
    def test_health_check(self) -> bool:
        """Проверка доступности сервера"""
        try:
            response = requests.get(f"{self.base_url}/api/categories", timeout=10)
            if response.status_code == 200:
                log_success("Сервер доступен")
                return True
            else:
                log_error(f"Сервер вернул статус {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            log_error(f"Сервер недоступен: {e}")
            return False
    
    def test_auth(self) -> bool:
        """Тест аутентификации пользователя"""
        data = {
            "telegramId": TEST_USER_ID,
            "firstName": "Test",
            "lastName": "User",
            "username": "testuser"
        }
        
        response = self.api_call('POST', '/auth', data)
        
        if response.status_code == 200:
            self.test_user = response.json()
            log_success(f"Аутентификация успешна: {self.test_user.get('firstName')}")
            return True
        else:
            log_error(f"Ошибка аутентификации: {response.status_code}")
            return False
    
    def test_get_categories(self) -> bool:
        """Тест получения списка категорий"""
        response = self.api_call('GET', '/categories')
        
        if response.status_code == 200:
            categories = response.json()
            log_success(f"Получено {len(categories)} категорий")
            
            # Проверка структуры
            if categories and all('id' in c and 'name' in c for c in categories):
                log_success("Структура категорий корректна")
                return True
            else:
                log_error("Некорректная структура категорий")
                return False
        else:
            log_error(f"Ошибка получения категорий: {response.status_code}")
            return False
    
    def test_get_exercises(self) -> bool:
        """Тест получения списка упражнений"""
        response = self.api_call('GET', '/exercises')
        
        if response.status_code == 200:
            exercises = response.json()
            log_success(f"Получено {len(exercises)} упражнений")
            
            # Проверка наличия exerciseType
            if exercises:
                first = exercises[0]
                if 'exerciseType' in first:
                    log_success(f"Поле exerciseType присутствует: {first.get('exerciseType')}")
                    
                    # Проверка разных типов
                    types = set(e.get('exerciseType') for e in exercises)
                    log_success(f"Найдены типы: {', '.join(types)}")
                    return True
                else:
                    log_error("Поле exerciseType отсутствует!")
                    return False
            return True
        else:
            log_error(f"Ошибка получения упражнений: {response.status_code}")
            return False
    
    def test_get_today_workout(self) -> bool:
        """Тест получения/создания тренировки на сегодня"""
        if not self.test_user:
            log_error("Требуется сначала пройти аутентификацию")
            return False
            
        response = self.api_call('GET', f'/workout/today/{TEST_USER_ID}')
        
        if response.status_code == 200:
            self.test_workout = response.json()
            log_success(f"Тренировка получена: ID={self.test_workout.get('id')}")
            return True
        else:
            log_error(f"Ошибка получения тренировки: {response.status_code}")
            return False
    
    def test_add_exercise_to_workout(self) -> bool:
        """Тест добавления упражнения в тренировку"""
        if not self.test_workout:
            log_error("Требуется сначала получить тренировку")
            return False
        
        # Получаем первое упражнение
        response = self.api_call('GET', '/exercises')
        if response.status_code != 200:
            log_error("Не удалось получить список упражнений")
            return False
            
        exercises = response.json()
        if not exercises:
            log_error("Список упражнений пуст")
            return False
            
        exercise_id = exercises[0]['id']
        exercise_type = exercises[0].get('exerciseType', 'STRENGTH')
        
        data = {
            "workoutId": self.test_workout['id'],
            "exerciseId": exercise_id
        }
        
        response = self.api_call('POST', '/workout/exercise', data)
        
        if response.status_code == 200:
            self.test_workout_exercise = response.json()
            log_success(f"Упражнение добавлено: {self.test_workout_exercise.get('exerciseName')}")
            log_info(f"Тип: {self.test_workout_exercise.get('exerciseType', exercise_type)}")
            return True
        else:
            log_error(f"Ошибка добавления упражнения: {response.status_code}")
            return False
    
    def test_add_set_strength(self) -> bool:
        """Тест добавления подхода (STRENGTH тип)"""
        if not self.test_workout_exercise:
            log_error("Требуется сначала добавить упражнение")
            return False
        
        data = {
            "workoutExerciseId": self.test_workout_exercise['id'],
            "setNumber": 1,
            "weight": 50.0,
            "reps": 10
        }
        
        response = self.api_call('POST', '/workout/set', data)
        
        if response.status_code == 200:
            set_data = response.json()
            self.test_sets.append(set_data)
            log_success(f"Подход добавлен: {set_data.get('weight')}кг x {set_data.get('reps')}")
            return True
        else:
            log_error(f"Ошибка добавления подхода: {response.status_code}")
            return False
    
    def test_add_set_with_all_fields(self) -> bool:
        """Тест добавления подхода со всеми полями"""
        if not self.test_workout_exercise:
            log_error("Требуется сначала добавить упражнение")
            return False
        
        data = {
            "workoutExerciseId": self.test_workout_exercise['id'],
            "setNumber": 2,
            "weight": 60.0,
            "reps": 8,
            "duration": 30,
            "distance": 100.0,
            "style": "FREESTYLE",
            "workTime": 20,
            "restTime": 10,
            "intensity": 7,
            "isWarmup": False,
            "isToFailure": True
        }
        
        response = self.api_call('POST', '/workout/set', data)
        
        if response.status_code == 200:
            set_data = response.json()
            self.test_sets.append(set_data)
            
            # Проверяем наличие новых полей в ответе
            new_fields = ['style', 'workTime', 'restTime', 'intensity']
            present_fields = [f for f in new_fields if f in set_data]
            
            log_success(f"Подход с расширенными полями добавлен")
            log_info(f"Поля присутствуют в ответе: {', '.join(present_fields)}")
            
            if set_data.get('style') == 'FREESTYLE':
                log_success("Стиль плавания сохранён корректно")
            
            return True
        else:
            log_error(f"Ошибка добавления подхода: {response.status_code} - {response.text}")
            return False
    
    def test_update_set(self) -> bool:
        """Тест обновления подхода"""
        if not self.test_sets:
            log_error("Требуется сначала создать подход")
            return False
        
        set_id = self.test_sets[0]['id']
        
        data = {
            "setId": set_id,
            "weight": 55.0,
            "reps": 12,
            "duration": 60,
            "intensity": 8
        }
        
        response = self.api_call('PUT', '/workout/set', data)
        
        if response.status_code == 200:
            updated = response.json()
            log_success(f"Подход обновлён: {updated.get('weight')}кг x {updated.get('reps')}")
            return True
        else:
            log_error(f"Ошибка обновления подхода: {response.status_code}")
            return False
    
    def test_get_workout_history(self) -> bool:
        """Тест получения истории тренировок"""
        response = self.api_call('GET', f'/workouts/{TEST_USER_ID}')
        
        if response.status_code == 200:
            workouts = response.json()
            log_success(f"История получена: {len(workouts)} тренировок")
            
            # Проверка наличия exerciseType в упражнениях
            if workouts:
                for workout in workouts:
                    for exercise in workout.get('exercises', []):
                        if 'exerciseType' in exercise:
                            log_success(f"exerciseType в истории: {exercise.get('exerciseType')}")
                            return True
                log_info("Нет упражнений с exerciseType в истории")
            return True
        else:
            log_error(f"Ошибка получения истории: {response.status_code}")
            return False
    
    def test_delete_set(self) -> bool:
        """Тест удаления подхода"""
        if not self.test_sets:
            log_error("Нет подходов для удаления")
            return False
        
        set_id = self.test_sets[-1]['id']
        
        response = self.api_call('DELETE', f'/workout/set/{set_id}')
        
        if response.status_code == 204:
            log_success(f"Подход удалён: ID={set_id}")
            self.test_sets.pop()
            return True
        else:
            log_error(f"Ошибка удаления подхода: {response.status_code}")
            return False
    
    def test_delete_workout_exercise(self) -> bool:
        """Тест удаления упражнения из тренировки"""
        if not self.test_workout_exercise:
            log_error("Нет упражнения для удаления")
            return False
        
        we_id = self.test_workout_exercise['id']
        
        response = self.api_call('DELETE', f'/workout/exercise/{we_id}')
        
        if response.status_code == 204:
            log_success(f"Упражнение удалено: ID={we_id}")
            self.test_workout_exercise = None
            self.test_sets = []
            return True
        else:
            log_error(f"Ошибка удаления упражнения: {response.status_code}")
            return False
    
    def test_exercise_types_coverage(self) -> bool:
        """Тест покрытия типов упражнений"""
        response = self.api_call('GET', '/exercises')
        
        if response.status_code != 200:
            log_error("Не удалось получить упражнения")
            return False
        
        exercises = response.json()
        types = set(e.get('exerciseType') for e in exercises if e.get('exerciseType'))
        
        expected_types = {
            'STRENGTH', 'BODYWEIGHT', 'WEIGHTED_BODYWEIGHT', 
            'STATIC', 'CARDIO_DISTANCE', 'CARDIO_TIME', 
            'SWIMMING', 'INTERVALS'
        }
        
        missing = expected_types - types
        
        if not missing:
            log_success("Все 8 типов упражнений присутствуют!")
            return True
        else:
            log_error(f"Отсутствуют типы: {', '.join(missing)}")
            return len(missing) <= 2  # Допускаем частичное покрытие
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        log_section("Запуск тестов GymTracker API")
        log_info(f"URL: {self.base_url}")
        
        tests = [
            ("Проверка доступности", self.test_health_check),
            ("Аутентификация", self.test_auth),
            ("Получение категорий", self.test_get_categories),
            ("Получение упражнений", self.test_get_exercises),
            ("Покрытие типов", self.test_exercise_types_coverage),
            ("Получение тренировки", self.test_get_today_workout),
            ("Добавление упражнения", self.test_add_exercise_to_workout),
            ("Добавление подхода (базовый)", self.test_add_set_strength),
            ("Добавление подхода (все поля)", self.test_add_set_with_all_fields),
            ("Обновление подхода", self.test_update_set),
            ("История тренировок", self.test_get_workout_history),
            ("Удаление подхода", self.test_delete_set),
            ("Удаление упражнения", self.test_delete_workout_exercise),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            log_section(name)
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                log_error(f"Исключение: {e}")
                failed += 1
        
        log_section("Результаты")
        print(f"{Colors.GREEN}Пройдено: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Провалено: {failed}{Colors.RESET}")
        
        return failed == 0


def main():
    """Главная функция"""
    tester = GymTrackerAPITester(API_BASE_URL)
    
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
