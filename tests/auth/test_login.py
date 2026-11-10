"""
Automatizované E2E testy pro přihlašování (Authentication - Login).
===================================================================
Architektura testů:
- Framework: Pytest + Playwright
- Vzor: Page Object Model (POM) – veškeré lokátory jsou zapouzdřeny v Page objektech
- Data: Externí testovací data ze souboru data/invalid_emails.json (Data-driven testing)
- Markery: @pytest.mark.auth, @pytest.mark.smoke, @pytest.mark.regression
"""

import re
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage
from utils.data_generator import load_json_data, generate_random_user
from helpers.auth_helpers import logout_user, register_and_login_user
from config.settings import settings


@pytest.mark.auth
class TestLogin:
    """Testovací sada pro ověření přihlašování a validace přihlašovacího formuláře."""

    # =========================================================================
    # 1. POZITIVNÍ SCÉNÁŘE (HAPPY PATH & JEHO VARIANTY)
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "email_transformer, submit_method, test_id",
        [
            (lambda e: e, "click", "standard_button_click"),
            (lambda e: e, "enter_key", "submit_with_enter_key"),
            (lambda e: e.upper(), "click", "uppercase_email_case_insensitivity"),
            (lambda e: f"  {e}  ", "click", "padded_email_whitespace_trimming"),
        ],
        ids=["standard-click", "enter-key", "uppercase-email", "padded-whitespace"]
    )
    def test_tc06_auth_successful_login_variants(
        self, page: Page, test_user: dict, email_transformer, submit_method: str, test_id: str
    ):
        """TC-06-AUTH: Ověření úspěšného přihlášení uživatele (Happy Path a jeho varianty)."""
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        login_page.open()
        expect(login_page.heading).to_be_visible()
        expect(login_page.heading).to_have_text("Přihlášení")

        email_to_use = email_transformer(test_user["email"])
        login_page.fill_email(email_to_use)
        login_page.fill_password(test_user["password"])

        if submit_method == "enter_key":
            login_page.password_input.press("Enter")
        else:
            login_page.click_login()

        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(courses_page.logout_button).to_have_text("Odhlásit se")

    @pytest.mark.smoke
    @pytest.mark.lecturer
    def test_tc37_lec_lecturer_successful_login_and_rights(self, page: Page, lecturer_user: dict):
        """TC-37-LEC: Úspěšné přihlášení lektora a ověření lektorských práv (přidat kurz)."""
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        login_page.open()
        login_page.login(lecturer_user["email"], lecturer_user["password"])

        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible()

        expect(courses_page.courses_header).to_contain_text("Přidat kurz")
        expect(courses_page.add_course_button).to_be_visible()

        courses_page.add_course_button.click()
        expect(page).to_have_url(courses_page.CREATE_URL)
        expect(courses_page.course_form).to_be_visible()
        expect(courses_page.course_name_input).to_be_visible()

    # =========================================================================
    # 2. NEGATIVNÍ A VALIDAČNÍ SCÉNÁŘE
    # =========================================================================

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "email, password, error_field, expected_error_text",
        [
            (settings.TEST_USER["email"], "SpatneHeslo123!", "email", None),
            ("neexistujici_uzivatel_999@kitner.cz", "LibovolneHeslo123", "email", None),
            (settings.TEST_USER["email"], "", "password", "The password field is required."),
            ("", "", None, None),
        ],
        ids=[
            "invalid-password",
            "non-existent-user",
            "empty-password-required",
            "empty-form-submit",
        ]
    )
    def test_tc07_auth_invalid_and_incomplete_login_credentials(
        self, page: Page, email: str, password: str, error_field: str, expected_error_text: str
    ):
        """TC-07-AUTH: Negativní a validační test pro chybné či neúplné přihlašovací údaje."""
        login_page = LoginPage(page)
        login_page.open()

        if email:
            login_page.fill_email(email)
        if password:
            login_page.fill_password(password)

        login_page.click_login()

        expect(page).to_have_url(login_page.URL)

        if error_field == "email":
            expect(login_page.email_error).to_be_visible(timeout=5000)
            if expected_error_text:
                expect(login_page.email_error).to_have_text(expected_error_text)
        elif error_field == "password":
            expect(login_page.password_error).to_be_visible(timeout=5000)
            if expected_error_text:
                expect(login_page.password_error).to_have_text(expected_error_text)

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "item",
        load_json_data("invalid_emails.json"),
        ids=lambda item: item["scenario_id"]
    )
    def test_tc08_auth_invalid_email_format_validation(self, page: Page, item: dict):
        """TC-08-AUTH: Data-driven ověření zamezení odeslání při neplatných formátech e-mailu (ze souboru data/invalid_emails.json)."""
        login_page = LoginPage(page)
        login_page.open()

        login_page.fill_email(item["email"])
        login_page.fill_password("PlatneHeslo123")
        login_page.click_login()

        # Uživatel musí zůstat na přihlašovací stránce (prohlížeč zamezí odeslání nevalidního e-mailu)
        expect(page).to_have_url(login_page.URL)

    # =========================================================================
    # 3. UI A BEZPEČNOSTNÍ KONTROLY
    # =========================================================================

    @pytest.mark.smoke
    def test_tc06_auth_title_and_password_masking(self, page: Page):
        """TC-06-AUTH: Kontrola metadat stránky (<title>) a bezpečnostního maskování hesla."""
        login_page = LoginPage(page)
        login_page.open()

        expect(page).to_have_title("Testování - přihlášení")
        expect(login_page.password_input).to_have_attribute("type", "password")

    @pytest.mark.smoke
    def test_tc06_auth_form_ui_elements_state(self, page: Page):
        """TC-06-AUTH: Kontrola výchozího stavu UI prvků přihlašovacího formuláře."""
        login_page = LoginPage(page)
        login_page.open()

        expect(login_page.email_input).to_have_attribute("placeholder", "Email")
        expect(login_page.email_input).to_be_enabled()
        expect(login_page.password_input).to_be_enabled()
        expect(login_page.login_button).to_have_text("Přihlásit")
        expect(login_page.login_button).to_be_enabled()

    # =========================================================================
    # 4. OCHRANA PROTI ÚTOKŮM HRUBOU SILOU (RATE LIMITING - US-07)
    # =========================================================================

    @pytest.mark.smoke
    def test_tc20_auth_temporary_lockout_after_five_failed_logins(self, page: Page):
        """TC-20-AUTH: Dočasná blokace po 5 neúspěšných pokusech o přihlášení."""
        # =====================================================================
        # 1. ARRANGE (Příprava izolovaného uživatele a Page Objectů)
        # =====================================================================
        login_page = LoginPage(page)
        user = generate_random_user(name_prefix="RateLimit P1")

        # Registrace a odhlášení nového uživatele
        register_and_login_user(page, user)
        logout_user(page)

        login_page.open()
        invalid_password = "ChybneHeslo999!"

        # =====================================================================
        # 2. ACT (5 neúspěšných pokusů za sebou)
        # =====================================================================
        for _ in range(5):
            with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
                login_page.login(user["email"], invalid_password)
            expect(login_page.email_error).to_be_visible()

        # 6. pokus o přihlášení
        with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
            login_page.login(user["email"], invalid_password)

        # =====================================================================
        # 3. ASSERT (3úrovňová validace: Routing + Session + Data State)
        # =====================================================================
        expect(page).to_have_url(login_page.URL)
        expect(login_page.email_error).to_be_visible()
        expect(login_page.email_error).to_contain_text(re.compile(r"Too many login attempts.*seconds", re.IGNORECASE))

    @pytest.mark.regression
    def test_tc21_auth_reset_failed_login_counter_on_success(self, page: Page):
        """TC-21-AUTH: Vynulování počítadla neúspěchů po úspěšném přihlášení."""
        # =====================================================================
        # 1. ARRANGE (Příprava izolovaného uživatele a Page Objectů)
        # =====================================================================
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)
        user = generate_random_user(name_prefix="RateReset P2")

        # Registrace a odhlášení nového uživatele
        register_and_login_user(page, user)
        logout_user(page)

        login_page.open()
        invalid_password = "ChybneHeslo999!"

        # =====================================================================
        # 2. ACT (3 neúspěšné pokusy + úspěšné přihlášení + odhlášení + 3 neúspěchy)
        # =====================================================================
        for _ in range(3):
            with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
                login_page.login(user["email"], invalid_password)
            expect(login_page.email_error).to_be_visible()

        # Úspěšné přihlášení vynuluje počítadlo neúspěchů
        login_page.login(user["email"], user["password"])
        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible()

        # Odhlášení
        courses_page.logout()
        expect(courses_page.login_link).to_be_visible()

        # Další 3 neúspěšné pokusy (celkem 6 pokusů přerušených úspěchem)
        login_page.open()
        for _ in range(3):
            with page.expect_response(lambda r: "/login" in r.url and r.request.method == "POST"):
                login_page.login(user["email"], invalid_password)
            expect(login_page.email_error).to_be_visible()

        # =====================================================================
        # 3. ASSERT (Uživatel není zablokován po celkových 6 neúspěších)
        # =====================================================================
        expect(page).to_have_url(login_page.URL)
        expect(login_page.email_error).to_be_visible()
        expect(login_page.email_error).not_to_contain_text(re.compile(r"Too many login attempts", re.IGNORECASE))

    @pytest.mark.regression
    def test_tc10_auth_keyboard_navigation_tab_and_enter(self, page: Page, test_user: dict):
        """TC-10-AUTH: Navigace klávesnicí (Tab + Enter) ve formuláři."""
        # =====================================================================
        # 1. ARRANGE
        # =====================================================================
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)
        login_page.open()

        # =====================================================================
        # 2. ACT
        # =====================================================================
        # 1. Zafokusovat e-mail a zadat text
        login_page.email_input.focus()
        page.keyboard.type(test_user["email"])

        # 2. Stisknout Tab pro přechod na heslo
        page.keyboard.press("Tab")
        expect(login_page.password_input).to_be_focused()

        # 3. Napsat heslo a odeslat klávesou Enter
        page.keyboard.type(test_user["password"])
        page.keyboard.press("Enter")

        # =====================================================================
        # 3. ASSERT
        # =====================================================================
        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible()


