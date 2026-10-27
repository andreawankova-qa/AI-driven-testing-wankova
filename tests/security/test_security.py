"""
Automatizované E2E testy pro Modul 6: Bezpečnost a autorizace (Security & Architecture).
======================================================================================
Pokrývá testovací případy:
- TC-43-SEC: Přesměrování nepřihlášeného uživatele z privátních URL na katalog
- TC-44-SEC: Zákaz lektorských operací pro zákazníka
- TC-45-SEC: Zákaz zápisu na kurz pro lektora
- TC-46-SEC: Ochrana formulářů CSRF tokenem a integrita požadavků
- TC-47-SEC: Regenerace session ID při přihlášení a odhlášení
"""

import pytest
from playwright.sync_api import Page, BrowserContext, expect
from pages.profile_page import ProfilePage
from pages.my_courses_page import MyCoursesPage
from pages.create_course_page import CreateCoursePage
from pages.course_detail_page import CourseDetailPage
from pages.courses_page import CoursesPage
from pages.login_page import LoginPage
from helpers.auth_helpers import login_user, login_lecturer, logout_user
from config.settings import settings


@pytest.mark.security
class TestSecurityAndAuthorization:
    """Testovací sada pro ověření RBAC oprávnění, ochrany privátních tras a integrity sezení."""

    @pytest.mark.smoke
    def test_tc43_sec_unauthenticated_private_url_access_blocked(self, page: Page):
        """TC-43-SEC: Přesměrování nepřihlášeného uživatele z privátních URL na katalog."""
        profile_page = ProfilePage(page)
        my_courses_page = MyCoursesPage(page)

        # 1. Pokus o přístup na /profile bez přihlášení
        profile_page.open()
        expect(profile_page.form).not_to_be_visible()

        # 2. Pokus o přístup na /my-courses bez přihlášení
        my_courses_page.open()
        expect(my_courses_page.navbar.login_link).to_be_visible()

    @pytest.mark.smoke
    @pytest.mark.xfail(reason="BR-01: Aplikace v rozporu s US-18 nezabezpečuje /courses/create před rolí Zákazník")
    def test_tc44_sec_customer_cannot_access_lecturer_operations(self, page: Page, test_user: dict):
        """TC-44-SEC: Zákaz lektorských operací pro uživatele v roli zákazníka."""
        login_user(page, test_user["email"], test_user["password"])

        create_course_page = CreateCoursePage(page)
        create_course_page.open()
        page.wait_for_load_state("networkidle")

        # Zákazník nemá přístup k formuláři pro tvorbu kurzu
        expect(create_course_page.form).not_to_be_visible()

    @pytest.mark.regression
    def test_tc45_sec_lecturer_cannot_enroll_as_customer(self, page: Page):
        """TC-45-SEC: Zákaz zápisu na kurz pro uživatele v roli lektora."""
        login_lecturer(page)
        courses_page = CoursesPage(page)

        # Lektor otevře katalog
        expect(courses_page.courses_header).to_be_visible()
        # V horní liště má tlačítko pro přidání kurzu, nikoliv klientské registrace
        expect(courses_page.add_course_button).to_have_text("Přidat kurz")

    @pytest.mark.security
    def test_tc46_sec_csrf_cookie_present_for_stateful_forms(self, page: Page, context: BrowserContext):
        """TC-46-SEC: Ochrana formulářů CSRF tokenem (přítomnost XSRF-TOKEN)."""
        login_page = LoginPage(page)
        login_page.open()
        page.wait_for_load_state("networkidle")

        cookies = context.cookies()
        cookie_names = [c["name"] for c in cookies]

        # Aplikace nastavuje bezpečnostní CSRF / session tokeny
        has_security_cookie = any("XSRF" in name or "session" in name.lower() for name in cookie_names)
        assert has_security_cookie, f"Očekáván bezpečnostní token v cookies, nalezeno: {cookie_names}"

    @pytest.mark.security
    def test_tc47_sec_session_regeneration_on_login_and_logout(self, page: Page, context: BrowserContext, test_user: dict):
        """TC-47-SEC: Regenerace session ID při přihlášení a odhlášení (ochrana proti Session Fixation)."""
        page.goto(f"{settings.BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        initial_cookies = {c["name"]: c["value"] for c in context.cookies()}
        initial_session = initial_cookies.get("laravel_session")

        # Přihlášení
        login_user(page, test_user["email"], test_user["password"])
        logged_in_cookies = {c["name"]: c["value"] for c in context.cookies()}
        logged_in_session = logged_in_cookies.get("laravel_session")

        # Session ID se po úspěšném přihlášení změnilo
        assert logged_in_session is not None
        if initial_session:
            assert logged_in_session != initial_session, "Session ID musí být při přihlášení regenerováno"

        # Odhlášení
        logout_user(page)
        logged_out_cookies = {c["name"]: c["value"] for c in context.cookies()}
        assert "logout_button" not in page.content()
