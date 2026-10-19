"""
Automatizované E2E testy pro obnovu zapomenutého hesla (Authentication - Password Reset).
========================================================================================
Architektura testů:
- Framework: Pytest + Playwright
- Vzor: Page Object Model (POM)
- Markery: @pytest.mark.auth, @pytest.mark.regression
"""

import pytest
from playwright.sync_api import Page, expect
from pages.forgot_password_page import ForgotPasswordPage


@pytest.mark.auth
class TestPasswordReset:
    """Testovací sada pro ověření toku obnovy zapomenutého hesla."""

    @pytest.mark.regression
    def test_forgot_password_request_submission(self, page: Page, lecturer_user: dict):
        """TC01: Odeslání požadavku na obnovu zapomenutého hesla přímo přes Page Object (DRY princip)."""
        forgot_password_page = ForgotPasswordPage(page)
        forgot_password_page.open()

        expect(forgot_password_page.info_text).to_be_visible()
        expect(forgot_password_page.info_text).to_contain_text("Zapoměli jste své heslo?")

        forgot_password_page.request_password_reset(lecturer_user["email"])

        expect(page).to_have_url(forgot_password_page.URL)
        expect(forgot_password_page.submit_button).to_be_visible()
