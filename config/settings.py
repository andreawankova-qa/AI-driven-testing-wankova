"""
Centrální konfigurace testovacího prostředí (Environment & Settings).
Načítá proměnné z .env souboru s bezpečnými výchozími hodnotami.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Načtení .env souboru z kořene projektu, pokud existuje
PROJECT_ROOT = Path(__file__).resolve().parent.parent
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()


class Settings:
    """Třída spravující globální konfiguraci a testovací prostředí."""

    BASE_URL: str = os.getenv("BASE_URL", "http://testovani.kitner.cz").rstrip("/")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() in ("true", "1", "yes")
    BROWSER_TIMEOUT: int = int(os.getenv("BROWSER_TIMEOUT", "30000"))

    # Testovací uživatel
    TEST_USER: dict = {
        "name": os.getenv("TEST_USER_NAME", "Test Tester"),
        "email": os.getenv("TEST_USER_EMAIL", "tester@kitner.cz"),
        "password": os.getenv("TEST_USER_PASSWORD", "TajneHeslo123")
    }

    # Uživatel s lektorskými právy
    LECTURER_USER: dict = {
        "email": os.getenv("LECTURER_USER_EMAIL", "lector@lector.com"),
        "password": os.getenv("LECTURER_USER_PASSWORD", "lector@lector.com")
    }


settings = Settings()
