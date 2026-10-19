"""
Globální Pytest fixtures pro automatizovanou sadu testů.
Všechny hodnoty jsou dynamicky napojeny na centrální konfiguraci config/settings.py.
"""

import pytest
from config.settings import settings


@pytest.fixture(scope="session")
def base_url() -> str:
    """Základní URL adresa testované aplikace."""
    return settings.BASE_URL


@pytest.fixture(scope="session")
def test_user() -> dict:
    """Přihlašovací údaje pro standardního testovacího uživatele."""
    return settings.TEST_USER


@pytest.fixture(scope="session")
def lecturer_user() -> dict:
    """Přihlašovací údaje pro uživatele s lektorskými právy."""
    return settings.LECTURER_USER
