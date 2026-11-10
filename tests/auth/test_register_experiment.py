"""
Experimentální automatizované testy pro registraci (TC-01-AUTH).
================================================================
Testovací scénář převzat ze souboru docs/test_cases_experiment.md.
Řídí se standardy AGENTS.md a skillem testcase-to-automation.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.home_page import HomePage
from utils.data_generator import generate_random_user


@pytest.mark.auth
class TestRegistrationExperiment:
    """Experimentální testovací sada pro ověření registrace uživatelů."""

    @pytest.mark.smoke
    def test_tc01_auth_successful_registration(self, page: Page):
        """TC-01-AUTH: Úspěšná registrace zákaznického účtu (Happy Path)."""
        # Arrange – Příprava testovacího prostředí, Page Objectů a dynamických dat
        register_page = RegisterPage(page)
        home_page = HomePage(page)
        new_user = generate_random_user(name_prefix="Jan Novák")

        register_page.open()

        # Krok 1: Kontrola viditelnosti polí formuláře
        expect(register_page.name_input).to_be_visible()
        expect(register_page.email_input).to_be_visible()
        expect(register_page.password_input).to_be_visible()
        expect(register_page.password_again_input).to_be_visible()

        # Act – Vyplnění údajů a odeslání registračního formuláře (Kroky 2-6)
        register_page.register(
            name=new_user["name"],
            email=new_user["email"],
            password=new_user["password"],
            password_again=new_user["password"],
        )

        # Assert – 3úrovňová validační pyramida (Routing, Session, Data State)
        # 1. Úroveň: Routing – Přesměrování na domovskou stránku /home
        expect(page).to_have_url(home_page.URL)

        # 2. Úroveň: Session State – Uživatel je přihlášen (zobrazeno tlačítko odhlášení)
        expect(home_page.navbar.logout_button).to_be_visible()

        # 3. Úroveň: Data State & UI Feedback – Uvítací zpráva s personalizovaným jménem
        expect(home_page.welcome_section).to_be_visible()
        expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {new_user['name']}!")
