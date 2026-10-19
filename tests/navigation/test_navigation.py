"""
Automatizované E2E testy pro navigaci a propojení stránek (Navigation & Linking).
=================================================================================
Architektura testů:
- Framework: Pytest + Playwright
- Vzor: Page Object Model (POM)
- Markery: @pytest.mark.navigation, @pytest.mark.smoke, @pytest.mark.regression
"""

import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.forgot_password_page import ForgotPasswordPage


@pytest.mark.navigation
class TestNavigation:
    """Testovací sada pro navigaci, přechody mezi formuláři a chráněnými trasami."""

    @pytest.mark.smoke
    def test_login_from_courses_navigation(self, page: Page, test_user: dict):
        """TC01: Integrační test – přechod z přehledu kurzů na přihlášení a návrat zpět."""
        courses_page = CoursesPage(page)
        login_page = LoginPage(page)

        courses_page.open()
        courses_page.login_link.click()

        expect(page).to_have_url(login_page.URL)

        login_page.login(test_user["email"], test_user["password"])

        expect(page).to_have_url(courses_page.URL)
        expect(courses_page.logout_button).to_be_visible()

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "link_attr, expected_page_class",
        [
            ("forgot_password_link", ForgotPasswordPage),
            ("register_link", RegisterPage),
        ],
        ids=["to-forgot-password", "to-register"]
    )
    def test_login_form_footer_links(self, page: Page, link_attr: str, expected_page_class):
        """TC02: Funkčnost doplňkových odkazů ve spodní části přihlašovacího formuláře (/login -> /forgot-password, /register)."""
        login_page = LoginPage(page)
        target_page = expected_page_class(page)

        login_page.open()
        link = getattr(login_page, link_attr)
        expect(link).to_be_visible()
        link.click()

        expect(page).to_have_url(target_page.URL)

    @pytest.mark.smoke
    def test_register_page_login_link_returns_to_login(self, page: Page):
        """TC03: Návratový odkaz 'Přihlásit se' z registrační stránky zpět na přihlášení (/register -> /login)."""
        register_page = RegisterPage(page)
        login_page = LoginPage(page)

        register_page.open()
        expect(register_page.login_link).to_be_visible()
        register_page.login_link.click()

        expect(page).to_have_url(login_page.URL)
        expect(login_page.login_button).to_be_visible()
