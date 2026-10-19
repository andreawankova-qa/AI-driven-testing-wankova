"""
Automatizované E2E testy pro modul Registrace (Authentication - Registration).
=============================================================================
Architektura testů:
- Framework: Pytest + Playwright
- Vzor: Page Object Model (POM) – zapouzdření všech elementů do stránek
- Helpers: Sdílené akce z helpers/auth_helpers.py (DRY)
- Utility: utils.data_generator pro dynamická testovací data
- Markery: @pytest.mark.auth, @pytest.mark.smoke, @pytest.mark.regression
"""

import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from pages.home_page import HomePage
from helpers.auth_helpers import logout_user
from utils.data_generator import generate_random_user, generate_random_email


@pytest.mark.auth
class TestRegistration:
    """Testovací sada pro ověření registrace uživatelů a validace polí."""

    @pytest.mark.smoke
    def test_successful_registration_and_password_masking(self, page: Page):
        """TC01: Úspěšná registrace nového uživatele a kontrola maskování hesel."""
        register_page = RegisterPage(page)
        home_page = HomePage(page)
        new_user = generate_random_user()

        register_page.open()

        # Bezpečnostní kontrola typu password
        expect(register_page.password_input).to_have_attribute("type", "password")
        expect(register_page.password_again_input).to_have_attribute("type", "password")

        # Registrace
        register_page.register(
            name=new_user["name"],
            email=new_user["email"],
            password=new_user["password"],
            password_again=new_user["password"]
        )

        # Ověření uvítání na /home přes HomePage model
        expect(page).to_have_url(home_page.URL, timeout=10000)
        expect(home_page.welcome_section).to_be_visible()
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {new_user['name']}!")

        # Ověření přihlášeného stavu přes sdílenou navbar komponentu
        expect(home_page.navbar.logout_button).to_be_visible()

    @pytest.mark.regression
    def test_registration_required_fields_validation(self, page: Page):
        """TC02: Validace povinných polí při odeslání prázdného formuláře."""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.click_register()

        expect(page).to_have_url(register_page.URL)
        expect(register_page.name_error).to_be_visible()
        expect(register_page.name_error).to_have_text("The name field is required.")

        expect(register_page.email_error).to_be_visible()
        expect(register_page.email_error).to_have_text("The email field is required.")

        expect(register_page.password_error).to_be_visible()
        expect(register_page.password_error).to_have_text("The password field is required.")

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "password_again_value, scenario_id",
        [
            ("ZcelaJineHeslo999", "different-password"),
            ("", "empty-password-again"),
        ],
        ids=["different-password", "empty-password-again"]
    )
    def test_registration_password_mismatch_and_empty_confirmation(
        self, page: Page, password_again_value: str, scenario_id: str
    ):
        """TC03: Negativní test registrace – neshoda hesel a prázdné potvrzení."""
        register_page = RegisterPage(page)
        test_email = generate_random_email(prefix=f"mismatch_{scenario_id}")

        register_page.open()
        register_page.register(
            name="Test Potvrzeni Hesla",
            email=test_email,
            password="HesloPrvni123",
            password_again=password_again_value
        )

        expect(page).to_have_url(register_page.URL)
        expect(register_page.password_error).to_be_visible()
        expect(register_page.password_error).to_have_text("The password field confirmation does not match.")

    @pytest.mark.regression
    def test_registration_short_password(self, page: Page):
        """TC04: Negativní test registrace – heslo kratší než 8 znaků."""
        register_page = RegisterPage(page)
        test_email = generate_random_email(prefix="short")

        register_page.open()
        register_page.register(
            name="Kratke Heslo",
            email=test_email,
            password="12345",
            password_again="12345"
        )

        expect(page).to_have_url(register_page.URL)
        expect(register_page.password_error).to_be_visible()
        expect(register_page.password_error).to_have_text("The password field must be at least 8 characters.")

    @pytest.mark.regression
    def test_registration_duplicate_email(self, page: Page, lecturer_user: dict):
        """TC05: Negativní test registrace – pokus o registraci s již obsazeným e-mailem."""
        register_page = RegisterPage(page)
        register_page.open()

        register_page.register(
            name="Duplicitni Lektor",
            email=lecturer_user["email"],
            password="PlatneHeslo123",
            password_again="PlatneHeslo123"
        )

        expect(page).to_have_url(register_page.URL)
        expect(register_page.email_error).to_be_visible()
        expect(register_page.email_error).to_have_text("The email has already been taken.")

    @pytest.mark.smoke
    def test_registration_and_subsequent_login_with_enter_key(self, page: Page):
        """TC06: Registrace nového uživatele, odhlášení a následné přihlášení klávesou Enter."""
        register_page = RegisterPage(page)
        home_page = HomePage(page)
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        new_user = generate_random_user(name_prefix="Novy Student")

        # 1. Registrace
        register_page.open()
        register_page.register(new_user["name"], new_user["email"], new_user["password"], new_user["password"])
        expect(page).to_have_url(home_page.URL, timeout=10000)

        # 2. Odhlášení přes sdílený helper (DRY)
        logout_user(page)

        # 3. Přihlášení přes Enter
        login_page.open()
        login_page.fill_email(new_user["email"])
        login_page.fill_password(new_user["password"])
        login_page.password_input.press("Enter")

        # 4. Ověření
        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible()
