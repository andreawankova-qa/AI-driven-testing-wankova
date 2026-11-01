"""
Automatizované E2E testy pro Modul 5: Profil a domovská nástěnka (User Profile & Dashboard).
========================================================================================
Pokrývá testovací případy:
- TC-39-PRF: Zobrazení personalizovaného uvítání na domovské nástěnce
- TC-40-PRF: Úspěšná aktualizace údajů profilu (jméno, IČO, telefon)
- TC-41-PRF: Validace formátu IČO a telefonu v profilu
- TC-42-PRF: Pokus o změnu e-mailu na již obsazenou adresu
"""

import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from helpers.auth_helpers import login_user
from utils.data_generator import generate_valid_ico, generate_invalid_ico


@pytest.mark.profile
class TestUserProfileAndDashboard:
    """Testovací sada pro domovskou nástěnku a profil uživatele."""

    @pytest.fixture(autouse=True)
    def setup_logged_in_user(self, page: Page, test_user: dict):
        """Přihlásí testovacího uživatele před každým testem."""
        login_user(page, test_user["email"], test_user["password"])

    @pytest.mark.smoke
    def test_tc39_prf_personalized_welcome_dashboard(self, page: Page, test_user: dict):
        """TC-39-PRF: Zobrazení personalizovaného uvítání na domovské nástěnce."""
        home_page = HomePage(page)
        home_page.open()

        expect(home_page.welcome_section).to_be_visible()
        expect(home_page.welcome_section).to_contain_text(test_user["name"])

    @pytest.mark.smoke
    def test_tc40_prf_display_and_update_profile(self, page: Page, test_user: dict):
        """TC-40-PRF: Předvyplnění údajů, úspěšná aktualizace profilu a přesměrování na /home."""
        profile_page = ProfilePage(page)
        home_page = HomePage(page)
        profile_page.open()

        expect(profile_page.heading).to_be_visible()
        expect(profile_page.name_input).to_have_value(test_user["name"])
        expect(profile_page.email_input).to_have_value(test_user["email"])

        valid_ico = generate_valid_ico()
        valid_phone = "+420 777 999 888"

        profile_page.update_profile(ico=valid_ico, phone=valid_phone)

        # US-17: Po uložení je uživatel přesměrován na domovskou stránku
        expect(page).to_have_url(home_page.URL, timeout=10000)
        expect(home_page.welcome_section).to_be_visible()
        page.wait_for_load_state("networkidle")

        # Ověření perzistence uložených dat po návratu do profilu
        profile_page.open()
        page.wait_for_load_state("networkidle")
        expect(profile_page.ico_input).to_have_value(valid_ico)
        expect(profile_page.phone_input).to_have_value(valid_phone)

    @pytest.mark.regression
    def test_tc41_prf_ico_and_phone_validation_in_profile(self, page: Page):
        """TC-41-PRF: Validace formátu IČO a telefonu v profilu."""
        profile_page = ProfilePage(page)
        profile_page.open()

        invalid_ico = generate_invalid_ico()
        profile_page.update_profile(ico=invalid_ico, phone="123")

        # Formulář zůstává zobrazen
        expect(profile_page.form).to_be_visible()

    @pytest.mark.regression
    def test_tc42_prf_duplicate_email_change_rejected(self, page: Page, test_user: dict, lecturer_user: dict):
        """TC-42-PRF: Pokus o změnu e-mailu na již obsazenou adresu je odmítnut."""
        profile_page = ProfilePage(page)
        profile_page.open()

        # Pokus o nastavení e-mailu existujícího lektora
        profile_page.email_input.fill(lecturer_user["email"])
        profile_page.save_button.click()

        # Znovunačtení profilu ověří, že e-mail nebyl přepsán na cizí adresu
        profile_page.open()
        expect(profile_page.email_input).to_have_value(test_user["email"])

