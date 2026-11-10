"""
Sdílené pomocné funkce pro autentizační workflow (Shared Auth Actions).
"""

from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.courses_page import CoursesPage
from config.settings import settings
from utils.data_generator import generate_random_user


def login_user(page: Page, email: str = None, password: str = None) -> CoursesPage:
    """
    Provede přihlášení uživatele přes UI.
    Pokud nejsou údaje zadány, použije výchozího testovacího uživatele z konfigurace.
    """
    user_email = email or settings.TEST_USER["email"]
    user_password = password or settings.TEST_USER["password"]

    login_page = LoginPage(page)
    login_page.open()
    login_page.login(user_email, user_password)

    courses_page = CoursesPage(page)
    expect(courses_page.courses_header).to_be_visible()
    return courses_page


def register_and_login_user(page: Page, user: dict = None) -> dict:
    """
    Zaregistruje nového unikátního zákazníka přes UI a ověří úspěšné přihlášení.
    Vrací slovník s údaji vytvořeného uživatele (který nemá žádné zapsané kurzy).
    """
    user_data = user or generate_random_user()
    register_page = RegisterPage(page)
    register_page.open()
    register_page.register(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
        password_again=user_data["password"],
    )
    # Systém po registraci přesměruje na /home a automaticky přihlásí uživatele
    expect(register_page.navbar.logout_button).to_be_visible()
    return user_data


def logout_user(page: Page) -> CoursesPage:
    """Provede bezpečné odhlášení uživatele přes navigační lištu."""
    courses_page = CoursesPage(page)
    if courses_page.is_logged_in():
        courses_page.logout()
    expect(courses_page.navbar.logout_button).not_to_be_visible()
    expect(courses_page.navbar.login_link).to_be_visible()
    return courses_page


def login_lecturer(page: Page) -> CoursesPage:
    """Provede přihlášení uživatele s lektorskými právy přes UI."""
    return login_user(page, settings.LECTURER_USER["email"], settings.LECTURER_USER["password"])


