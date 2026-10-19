"""
Automatizované E2E testy pro odhlášení a správu sezení (Authentication - Logout & Session).
========================================================================================
Architektura testů:
- Framework: Pytest + Playwright
- Vzor: Page Object Model (POM) + Shared Helpers (DRY)
- Markery: @pytest.mark.auth, @pytest.mark.smoke
"""

import pytest
from playwright.sync_api import Page, expect
from helpers.auth_helpers import login_user


@pytest.mark.auth
class TestLogoutAndSession:
    """Testovací sada pro životní cyklus odhlášení a stabilitu přihlašovací relace."""

    @pytest.mark.smoke
    def test_login_and_logout_lifecycle(self, page: Page, test_user: dict):
        """TC01: E2E test kompletního životního cyklu (Login -> Logout)."""
        # 1. Přihlášení přes sdílený helper (DRY princip)
        courses_page = login_user(page, test_user["email"], test_user["password"])

        # 2. Odhlášení
        courses_page.logout()

        # 3. Ověření ukončení relace
        expect(courses_page.logout_button).not_to_be_visible()
        expect(courses_page.login_link).to_be_visible()

    @pytest.mark.smoke
    def test_session_persists_after_page_reload(self, page: Page, test_user: dict):
        """TC02: Ověření perzistence přihlášení po obnovení stránky (Reload / F5)."""
        # 1. Přihlášení přes sdílený helper (DRY princip)
        courses_page = login_user(page, test_user["email"], test_user["password"])

        # 2. Obnovení stránky
        page.reload()

        # 3. Ověření, že uživatel zůstal přihlášen
        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(page).to_have_url(courses_page.URL)
