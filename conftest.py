import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def base_url():
    """Základní URL adresa testované aplikace."""
    return "http://testovani.kitner.cz"


@pytest.fixture(scope="session")
def test_user():
    """Přihlašovací údaje pro testovacího uživatele."""
    return {
        "email": "tester@kitner.cz",
        "password": "TajneHeslo123",
        "name": "Test Tester"
    }
