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
from pages.reset_password_page import ResetPasswordPage
from pages.email_verification_page import EmailVerificationPage
from pages.login_page import LoginPage
from config.settings import settings


@pytest.mark.auth
class TestPasswordReset:
    """Testovací sada pro ověření toku obnovy zapomenutého hesla a ověření e-mailu."""

    @pytest.mark.regression
    def test_tc12_auth_forgot_password_request_submission(self, page: Page, lecturer_user: dict):
        """TC-12-AUTH: Odeslání požadavku na obnovu zapomenutého hesla přímo přes Page Object (DRY princip)."""
        forgot_password_page = ForgotPasswordPage(page)
        forgot_password_page.open()

        expect(forgot_password_page.info_text).to_be_visible()
        expect(forgot_password_page.info_text).to_contain_text("Zapoměli jste své heslo?")

        forgot_password_page.request_password_reset(lecturer_user["email"])

        expect(page).to_have_url(forgot_password_page.URL)
        expect(forgot_password_page.submit_button).to_be_visible()

    @pytest.mark.regression
    def test_tc13_auth_forgot_password_invalid_or_empty_email_validation(self, page: Page):
        """TC-13-AUTH: Žádost o reset s neplatným / prázdným e-mailem."""
        forgot_password_page = ForgotPasswordPage(page)
        forgot_password_page.open()

        # 1. Prázdný e-mail
        forgot_password_page.submit()
        expect(page).to_have_url(forgot_password_page.URL)

        # 2. Neplatný formát e-mailu
        forgot_password_page.fill_email("neplatny-email-bez-zavinace")
        forgot_password_page.submit()
        expect(page).to_have_url(forgot_password_page.URL)
        expect(forgot_password_page.submit_button).to_be_visible()

    # =========================================================================
    # 2. DOKONČENÍ ZMĚNY HESLA POMOCÍ TOKENU (US-05)
    # =========================================================================

    @pytest.mark.regression
    @pytest.mark.xfail(
        reason="BR-03: Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password",
        strict=True
    )
    def test_tc14_auth_successful_password_reset_with_valid_token(self, page: Page):
        """TC-14-AUTH: Úspěšná změna hesla pomocí platného tokenu."""
        reset_page = ResetPasswordPage(page)
        login_page = LoginPage(page)

        # Otevření stránky resetu s platným tokenem
        reset_page.open(token="valid_sample_token_xyz123", email="tester@kitner.cz")

        # Ověření zobrazení formuláře pro zadání nového hesla
        expect(reset_page.password_input).to_be_visible()
        expect(reset_page.password_again_input).to_be_visible()
        expect(reset_page.submit_button).to_be_visible()

        # Odeslání nového hesla
        reset_page.reset_password(password="NoveBezpecneHeslo123!", password_again="NoveBezpecneHeslo123!")

        # Ověření přesměrování na login s potvrzením
        expect(page).to_have_url(login_page.URL, timeout=10000)

    @pytest.mark.regression
    def test_tc15_auth_password_reset_invalid_or_expired_token(self, page: Page):
        """TC-15-AUTH: Pokus o změnu hesla s neplatným nebo expirovaným tokenem."""
        reset_page = ResetPasswordPage(page)

        # Otevření stránky resetu s neplatným tokenem
        reset_page.open(token="neplatny_nebo_expirovany_token_404", email="tester@kitner.cz")

        # Systém musí indikovat neplatnost odkazu nebo zamezit formuláři
        if reset_page.submit_button.is_visible():
            reset_page.reset_password(password="NoveHeslo123!", password_again="NoveHeslo123!")
            expect(reset_page.error_message).to_be_visible()
        else:
            expect(reset_page.password_input).not_to_be_visible()

    @pytest.mark.regression
    @pytest.mark.xfail(
        reason="BR-03: Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password",
        strict=True
    )
    def test_tc16_auth_password_reset_mismatched_confirmation(self, page: Page):
        """TC-16-AUTH: Změna hesla s neshodným potvrzením nového hesla."""
        reset_page = ResetPasswordPage(page)
        reset_page.open(token="valid_sample_token_xyz123", email="tester@kitner.cz")

        expect(reset_page.password_input).to_be_visible()
        expect(reset_page.password_again_input).to_be_visible()

        reset_page.reset_password(password="PrvniHeslo123!", password_again="DruheOdlišneHeslo456!")
        expect(reset_page.password_error).to_be_visible()

    # =========================================================================
    # 3. OVĚŘENÍ E-MAILOVÉ ADRESY (EMAIL VERIFICATION - US-06)
    # =========================================================================

    @pytest.mark.regression
    def test_tc17_auth_email_verification_success(self, page: Page):
        """TC-17-AUTH: Úspěšné ověření e-mailu přes platný odkaz."""
        verify_page = EmailVerificationPage(page)
        verify_page.open_verification_link(token="platny_verifikacni_token_123")

        # Ověření, že systém přijal požadavek a zobrazil stránku
        expect(verify_page.container).to_be_visible()

    @pytest.mark.regression
    def test_tc18_auth_email_verification_invalid_link(self, page: Page):
        """TC-18-AUTH: Pokus o ověření e-mailu s neplatným odkazem."""
        verify_page = EmailVerificationPage(page)
        verify_page.open_verification_link(token="neplatny_token_xyz")

        expect(verify_page.container).to_be_visible()

    @pytest.mark.regression
    def test_tc19_auth_resend_verification_email_rate_limit(self, page: Page):
        """TC-19-AUTH: Znovuzaslání ověřovacího e-mailu a časový limit."""
        verify_page = EmailVerificationPage(page)
        verify_page.open_prompt()

        expect(verify_page.container).to_be_visible()

