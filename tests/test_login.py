import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage


class TestLogin:
    """Refaktorovaná testovací sada pro ověření přihlašování s využitím parametrizace (DRY)."""

    # ==========================================
    # 1. POZITIVNÍ SCÉNÁŘE (HAPPY PATH & VARIANTY)
    # ==========================================

    @pytest.mark.parametrize(
        "email_transformer, submit_method, test_id",
        [
            (lambda e: e, "click", "standard_button_click"),
            (lambda e: e, "enter_key", "submit_with_enter_key"),
            (lambda e: e.upper(), "click", "uppercase_email_case_insensitivity"),
        ],
        ids=["standard-click", "enter-key", "uppercase-email"]
    )
    def test_successful_login_variants(
        self, page: Page, test_user: dict, email_transformer, submit_method: str, test_id: str
    ):
        """
        Ověření úspěšného přihlášení a jeho variant:
        - Běžné odeslání kliknutím na tlačítko
        - Odeslání formuláře stiskem klávesy Enter
        - Zadání e-mailu velkými písmeny (Case Insensitivity)
        """
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        login_page.open()
        expect(login_page.heading).to_be_visible()
        expect(login_page.heading).to_have_text("Přihlášení")

        # Příprava údajů
        email_to_use = email_transformer(test_user["email"])
        login_page.fill_email(email_to_use)
        login_page.fill_password(test_user["password"])

        # Způsob odeslání
        if submit_method == "enter_key":
            login_page.password_input.press("Enter")
        else:
            login_page.click_login()

        # Ověření úspěšného přihlášení
        expect(page).to_have_url(courses_page.URL, timeout=10000)
        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(courses_page.logout_button).to_have_text("Odhlásit se")

    def test_login_from_courses_navigation(self, page: Page, test_user: dict):
        """Integrační test: přechod na přihlášení přes horní navigační menu a návrat na kurzy."""
        courses_page = CoursesPage(page)
        login_page = LoginPage(page)

        courses_page.open()
        courses_page.login_link.first.click()

        expect(page).to_have_url(login_page.URL)
        login_page.login(test_user["email"], test_user["password"])

        expect(page).to_have_url(courses_page.URL)
        expect(courses_page.logout_button).to_be_visible()

    def test_login_and_logout_lifecycle(self, page: Page, test_user: dict):
        """Kompletní životní cyklus: přihlášení -> odhlášení -> kontrola anonymního stavu."""
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        login_page.open()
        login_page.login(test_user["email"], test_user["password"])
        expect(courses_page.logout_button).to_be_visible()

        courses_page.logout()

        expect(courses_page.logout_button).not_to_be_visible()
        expect(page.locator('[data-testid="login_link"]').first).to_be_visible()

    def test_session_persists_after_page_reload(self, page: Page, test_user: dict):
        """Perzistence session: po obnovení stránky (F5/reload) zůstává uživatel přihlášen."""
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        login_page.open()
        login_page.login(test_user["email"], test_user["password"])
        expect(courses_page.logout_button).to_be_visible()

        page.reload()

        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(page).to_have_url(courses_page.URL)

    # ==========================================
    # 2. NEGATIVNÍ A VALIDAČNÍ SCÉNÁŘE (PARAMETRIZOVANÉ)
    # ==========================================

    @pytest.mark.parametrize(
        "email, password, expected_error_selector, expected_error_text",
        [
            ("tester@kitner.cz", "SpatneHeslo123!", '[data-testid="email_input_errors"]', None),
            ("neexistujici_uzivatel_999@kitner.cz", "LibovolneHeslo123", '[data-testid="email_input_errors"]', None),
            ("tester@kitner.cz", "", '[data-testid="password_input_errors"]', "The password field is required."),
            ("", "", None, None),
            ("neplatny_email_bez_zavinace", "TajneHeslo123", None, None),
        ],
        ids=[
            "invalid-password",
            "non-existent-user",
            "empty-password-required",
            "empty-form-submit",
            "invalid-email-format",
        ]
    )
    def test_invalid_and_incomplete_login_credentials(
        self, page: Page, email: str, password: str, expected_error_selector: str, expected_error_text: str
    ):
        """
        Parametrizovaný negativní test pro neplatné, chybějící či vadné vstupy.
        Ověřuje, že:
        1. Uživatel nikdy neprojde dál a zůstane na /login
        2. Pokud má být zobrazena chybová hláška, ověří její viditelnost a případně přesný text
        """
        login_page = LoginPage(page)
        login_page.open()

        # Vyplnění polí (pokud jsou zadána)
        if email:
            login_page.fill_email(email)
        if password:
            login_page.fill_password(password)

        login_page.click_login()

        # 1. Kontrola, že nedošlo k přihlášení
        expect(page).to_have_url(login_page.URL)

        # 2. Kontrola chybové hlášky, pokud je očekávána
        if expected_error_selector:
            error_locator = page.locator(expected_error_selector)
            expect(error_locator).to_be_visible(timeout=5000)
            if expected_error_text:
                expect(error_locator).to_have_text(expected_error_text)

    # ==========================================
    # 3. NAVIGAČNÍ ODKAZY NA FORMULÁŘI (PARAMETRIZOVANÉ)
    # ==========================================

    @pytest.mark.parametrize(
        "link_selector, expected_url",
        [
            ('[data-testid="forgot_password_link"]', "http://testovani.kitner.cz/forgot-password"),
            ('[data-testid="register_link"]', "http://testovani.kitner.cz/register"),
        ],
        ids=["forgot-password-link", "register-link"]
    )
    def test_login_form_navigation_links(self, page: Page, link_selector: str, expected_url: str):
        """Parametrizovaný test odkazů na přihlašovací stránce (Zapomenuté heslo, Registrace)."""
        login_page = LoginPage(page)
        login_page.open()

        link = page.locator(link_selector)
        expect(link).to_be_visible()
        link.click()

        expect(page).to_have_url(expected_url)

    # ==========================================
    # 4. UI A BEZPEČNOSTNÍ KONTROLY
    # ==========================================

    def test_login_page_title_and_password_masking(self, page: Page):
        """Ověření HTML titulku stránky a bezpečnostního maskování hesla (type='password')."""
        login_page = LoginPage(page)
        login_page.open()

        # Titulek záložky
        expect(page).to_have_title("Testování - přihlášení")

        # Maskování hesla
        expect(login_page.password_input).to_have_attribute("type", "password")
