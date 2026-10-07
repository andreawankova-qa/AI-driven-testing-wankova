"""
Automatizované E2E testy pro modul Demo Login (http://testovani.kitner.cz)
=======================================================================
Architektura testů:
- Jazyk: Python 3
- Test Runner: Pytest
- Automatizační nástroj: Playwright (Chromium)
- Návrhový vzor: Page Object Model (POM) – oddělení logiky stránek od samotných testů
- Přístup: DRY (Don't Repeat Yourself) s využitím parametrizace (@pytest.mark.parametrize)
"""

import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.courses_page import CoursesPage


class TestLogin:
    """Testovací sada pro ověření přihlašování a navazujících funkcionalit."""

    # =========================================================================
    # 1. POZITIVNÍ SCÉNÁŘE (HAPPY PATH & JEHO VARIANTY)
    # =========================================================================

    @pytest.mark.parametrize(
        "email_transformer, submit_method, test_id",
        [
            # Varianta 1: Běžné zadání e-mailu a odeslání kliknutím na tlačítko "Přihlásit"
            (lambda e: e, "click", "standard_button_click"),
            # Varianta 2: Odeslání formuláře stiskem klávesy Enter v poli pro heslo (UX test)
            (lambda e: e, "enter_key", "submit_with_enter_key"),
            # Varianta 3: Zadání e-mailu velkými písmeny pro ověření Case-Insensitivity
            (lambda e: e.upper(), "click", "uppercase_email_case_insensitivity"),
        ],
        ids=["standard-click", "enter-key", "uppercase-email"]
    )
    def test_successful_login_variants(
        self, page: Page, test_user: dict, email_transformer, submit_method: str, test_id: str
    ):
        """
        TC01: Ověření úspěšného přihlášení uživatele (Happy Path a jeho varianty).
        
        Kroky testu:
        1. Inicializace Page Objectů (LoginPage, CoursesPage).
        2. Otevření přihlašovací stránky (/login) a ověření viditelnosti nadpisu.
        3. Příprava a vyplnění přihlašovacích údajů (e-mail dle varianty, heslo).
        4. Odeslání formuláře (kliknutím nebo klávesou Enter).
        5. Kontrola přesměrování na stránku s kurzy (/courses).
        6. Kontrola zobrazení tlačítka pro odhlášení (důkaz aktivní autorizace).
        """
        # [ARRANGE] Inicializace stránek
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        # [ACT] 1. Otevření přihlašovací stránky
        login_page.open()

        # [ASSERT] 2. Kontrola přítomnosti a textu nadpisu formuláře
        expect(login_page.heading).to_be_visible()
        expect(login_page.heading).to_have_text("Přihlášení")

        # [ACT] 3. Vyplnění údajů (s transformací e-mailu dle varianty)
        email_to_use = email_transformer(test_user["email"])
        login_page.fill_email(email_to_use)
        login_page.fill_password(test_user["password"])

        # [ACT] 4. Odeslání formuláře podle zadané metody (klik / Enter)
        if submit_method == "enter_key":
            login_page.password_input.press("Enter")
        else:
            login_page.click_login()

        # [ASSERT] 5. Ověření přesměrování na přehled kurzů po přihlášení
        expect(page).to_have_url(courses_page.URL, timeout=10000)

        # [ASSERT] 6. Ověření, že uživatel je přihlášen (vidí tlačítko "Odhlásit se")
        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(courses_page.logout_button).to_have_text("Odhlásit se")

    def test_login_from_courses_navigation(self, page: Page, test_user: dict):
        """
        TC02: Integrační test – přihlášení přes navigační lištu z hlavní stránky kurzů.
        
        Kroky testu:
        1. Otevření hlavní stránky kurzů (/courses).
        2. Kliknutí na odkaz "Přihlásit se" v horním menu.
        3. Ověření přesměrování na přihlašovací formulář (/login).
        4. Vyplnění platných údajů a odeslání přihlášení.
        5. Ověření návratu na přehled kurzů a přihlášeného stavu.
        """
        # [ARRANGE] Příprava stránek
        courses_page = CoursesPage(page)
        login_page = LoginPage(page)

        # [ACT] 1. Otevření stránky s kurzy
        courses_page.open()

        # [ACT] 2. Kliknutí na odkaz "Přihlásit se" v navigaci
        courses_page.login_link.first.click()

        # [ASSERT] 3. Kontrola přechodu na přihlašovací stránku
        expect(page).to_have_url(login_page.URL)

        # [ACT] 4. Vyplnění údajů a přihlášení
        login_page.login(test_user["email"], test_user["password"])

        # [ASSERT] 5. Kontrola návratu na kurzy a přihlášeného stavu
        expect(page).to_have_url(courses_page.URL)
        expect(courses_page.logout_button).to_be_visible()

    def test_login_and_logout_lifecycle(self, page: Page, test_user: dict):
        """
        TC03: E2E test kompletního životního cyklu (Login -> Logout).
        
        Kroky testu:
        1. Úspěšné přihlášení uživatele.
        2. Ověření, že je přihlášen (tlačítko "Odhlásit se" je viditelné).
        3. Kliknutí na tlačítko "Odhlásit se".
        4. Ověření zrušení relace – tlačítko "Odhlásit se" zmizí a objeví se odkaz "Přihlásit se".
        """
        # [ARRANGE] Příprava stránek
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        # [ACT] 1. Provedení přihlášení
        login_page.open()
        login_page.login(test_user["email"], test_user["password"])

        # [ASSERT] 2. Ověření, že je uživatel v přihlášeném stavu
        expect(courses_page.logout_button).to_be_visible()

        # [ACT] 3. Provedení odhlášení
        courses_page.logout()

        # [ASSERT] 4. Ověření návratu do anonymního stavu
        expect(courses_page.logout_button).not_to_be_visible()
        expect(page.locator('[data-testid="login_link"]').first).to_be_visible()

    def test_session_persists_after_page_reload(self, page: Page, test_user: dict):
        """
        TC04: Ověření perzistence přihlášení po obnovení stránky (Reload / F5).
        
        Kroky testu:
        1. Úspěšné přihlášení do aplikace.
        2. Obnovení stránky pomocí page.reload().
        3. Ověření, že session/token přetrval a uživatel je stále přihlášen.
        """
        # [ARRANGE] Příprava stránek
        login_page = LoginPage(page)
        courses_page = CoursesPage(page)

        # [ACT] 1. Přihlášení
        login_page.open()
        login_page.login(test_user["email"], test_user["password"])
        expect(courses_page.logout_button).to_be_visible()

        # [ACT] 2. Obnovení stránky (simulace stisku klávesy F5)
        page.reload()

        # [ASSERT] 3. Ověření, že uživatel zůstal přihlášen
        expect(courses_page.logout_button).to_be_visible(timeout=5000)
        expect(page).to_have_url(courses_page.URL)

    # =========================================================================
    # 2. NEGATIVNÍ A VALIDAČNÍ SCÉNÁŘE (PARAMETRIZOVANÉ)
    # =========================================================================

    @pytest.mark.parametrize(
        "email, password, expected_error_selector, expected_error_text",
        [
            # Scénář 1: Správný e-mail, ale neplatné heslo -> obecná chyba neshody údajů
            ("tester@kitner.cz", "SpatneHeslo123!", '[data-testid="email_input_errors"]', None),
            # Scénář 2: Neexistující uživatelský e-mail -> obecná chyba neshody údajů
            ("neexistujici_uzivatel_999@kitner.cz", "LibovolneHeslo123", '[data-testid="email_input_errors"]', None),
            # Scénář 3: Vyplněný e-mail, ale prázdné heslo -> validační zpráva povinného pole
            ("tester@kitner.cz", "", '[data-testid="password_input_errors"]', "The password field is required."),
            # Scénář 4: Odeslání zcela prázdného formuláře -> setrvání na přihlašovací stránce
            ("", "", None, None),
            # Scénář 5: Neplatný formát e-mailu (bez @ a domény) -> setrvání na stránce
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
        TC05: Parametrizovaný negativní a validační test pro chybné či neúplné vstupy.
        
        Kroky testu:
        1. Otevření přihlašovací stránky.
        2. Vyplnění zadané kombinace e-mailu a hesla.
        3. Pokus o odeslání formuláře kliknutím na "Přihlásit".
        4. Kontrola, že systém uživatele nepustil dál (URL zůstává /login).
        5. Kontrola zobrazení a textu chybové hlášky (pokud je pro daný scénář definována).
        """
        # [ARRANGE] Otevření přihlašovacího formuláře
        login_page = LoginPage(page)
        login_page.open()

        # [ACT] Vyplnění polí dle testovacích parametrů
        if email:
            login_page.fill_email(email)
        if password:
            login_page.fill_password(password)

        login_page.click_login()

        # [ASSERT] 1. Negativní kontrola: Uživatel MUSÍ zůstat na přihlašovací stránce (/login)
        expect(page).to_have_url(login_page.URL)

        # [ASSERT] 2. Validační kontrola: Ověření zobrazení a případně přesného textu chyby
        if expected_error_selector:
            error_locator = page.locator(expected_error_selector)
            expect(error_locator).to_be_visible(timeout=5000)
            if expected_error_text:
                expect(error_locator).to_have_text(expected_error_text)

    # =========================================================================
    # 3. NAVIGAČNÍ ODKAZY NA PŘIHLAŠOVACÍ STRÁNCE (PARAMETRIZOVANÉ)
    # =========================================================================

    @pytest.mark.parametrize(
        "link_selector, expected_url",
        [
            # Odkaz na obnovení hesla -> přesměrování na /forgot-password
            ('[data-testid="forgot_password_link"]', "http://testovani.kitner.cz/forgot-password"),
            # Odkaz na registraci nového účtu -> přesměrování na /register
            ('[data-testid="register_link"]', "http://testovani.kitner.cz/register"),
        ],
        ids=["forgot-password-link", "register-link"]
    )
    def test_login_form_navigation_links(self, page: Page, link_selector: str, expected_url: str):
        """
        TC06: Ověření funkčnosti sekundárních odkazů na přihlašovacím formuláři.
        
        Kroky testu:
        1. Otevření přihlašovací stránky.
        2. Nalezení a ověření viditelnosti příslušného odkazu.
        3. Kliknutí na odkaz.
        4. Ověření přesměrování na správnou cílovou URL adresu.
        """
        # [ARRANGE] Otevření stránky
        login_page = LoginPage(page)
        login_page.open()

        # [ACT] Vyhledání odkazu a kliknutí
        link = page.locator(link_selector)
        expect(link).to_be_visible()
        link.click()

        # [ASSERT] Ověření přesměrování na očekávanou URL
        expect(page).to_have_url(expected_url)

    # =========================================================================
    # 4. UI A BEZPEČNOSTNÍ KONTROLY
    # =========================================================================

    def test_login_page_title_and_password_masking(self, page: Page):
        """
        TC07: Kontrola metadat stránky (<title>) a bezpečnostního maskování hesla.
        
        Kroky testu:
        1. Otevření přihlašovací stránky.
        2. Ověření správného textu v HTML tagu <title> (záložka prohlížeče).
        3. Ověření, že vstupní pole pro heslo má HTML atribut type="password" (hvězdičkování).
        """
        # [ARRANGE] Otevření stránky
        login_page = LoginPage(page)
        login_page.open()

        # [ASSERT] 1. Kontrola HTML titulku záložky prohlížeče
        expect(page).to_have_title("Testování - přihlášení")

        # [ASSERT] 2. Bezpečnostní kontrola: pole pro heslo musí mít type="password"
        expect(login_page.password_input).to_have_attribute("type", "password")
