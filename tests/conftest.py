"""
Pytest configuration for GymTracker API tests
"""
import os
import pytest

def pytest_configure(config):
    """Конфигурация pytest"""
    # Устанавливаем базовый URL если не задан
    if not os.environ.get('API_BASE_URL'):
        os.environ['API_BASE_URL'] = 'http://localhost:8080'


@pytest.fixture
def api_base_url():
    """Fixture для базового URL API"""
    return os.environ.get('API_BASE_URL', 'http://localhost:8080')


@pytest.fixture
def test_user_id():
    """Fixture для тестового Telegram ID"""
    return 999999999
