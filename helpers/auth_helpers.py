"""
Sdílené pomocné funkce pro autentizační workflow (Shared Auth Actions).
"""

from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from config.settings import settings


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

