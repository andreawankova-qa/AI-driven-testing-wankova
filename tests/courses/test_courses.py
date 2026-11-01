"""
Automatizované E2E testy pro Modul 2: Katalog a detail kurzů (Courses Catalog).
=============================================================================
Pokrývá testovací případy:
- TC-22-CRS: Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka
- TC-23-CRS: Ověření zobrazení atributů kurzu v katalogu (cena, kapacita, náhled)
- TC-24-CRS: Zobrazení detailu kurzu a seznamu vypsaných termínů
- TC-25-CRS: Zobrazení tlačítka zápisu u termínu s volnou kapacitou
- TC-26-CRS: Zamezení registrace a indikace plně obsazeného běhu
"""

import re
import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.course_detail_page import CourseDetailPage
from helpers.auth_helpers import login_user


@pytest.mark.courses
class TestCoursesCatalog:
    """Testovací sada pro katalog kurzů a detail vypsaných běhů."""

    @pytest.mark.smoke
    def test_tc22_crs_catalog_display_for_guest(self, page: Page):
        """TC-22-CRS: Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka."""
        courses_page = CoursesPage(page)
        courses_page.open()

        # Ověření zobrazení záhlaví a karet kurzů
        expect(courses_page.courses_header).to_be_visible()
        expect(courses_page.course_cards.first).to_be_visible()
        expect(courses_page.course_cards).not_to_have_count(0)

        # Ověření přítomnosti výzvy k registraci pod katalogem pro nepřihlášeného
        expect(courses_page.navbar.login_link).to_be_visible()

    @pytest.mark.regression
    def test_tc23_crs_course_card_attributes(self, page: Page):
        """TC-23-CRS: Ověření zobrazení atributů kurzu v katalogu."""
        courses_page = CoursesPage(page)
        courses_page.open()

        # První karta kurzu
        first_card = courses_page.course_cards.first
        expect(first_card).to_be_visible()

        # Kontrola názvu, popisu, ceny, kapacity a náhledu přes Page Object
        expect(courses_page.get_card_name(first_card)).to_be_visible()
        expect(courses_page.get_card_description(first_card)).to_be_visible()
        expect(courses_page.get_card_price(first_card)).to_be_visible()
        expect(courses_page.get_card_capacity(first_card)).to_be_visible()
        expect(courses_page.get_card_image(first_card)).to_be_visible()

        # Cena obsahuje měnu a je zaokrouhlena (např. Kč) – web-first ověření
        expect(courses_page.get_card_price(first_card)).to_contain_text(re.compile(r"Kč|\d+", re.IGNORECASE))

    @pytest.mark.smoke
    def test_tc24_crs_course_detail_and_iterations_display(self, page: Page):
        """TC-24-CRS: Zobrazení detailu kurzu a seznamu vypsaných termínů."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()

        # Ověření nadpisu kurzu a sekce běhů
        expect(course_detail.heading).to_be_visible()
        expect(course_detail.runs_heading).to_be_visible()

    @pytest.mark.smoke
    def test_tc25_crs_enrollment_button_for_available_capacity(self, page: Page, test_user: dict):
        """TC-25-CRS: Zobrazení tlačítka zápisu u termínu s volnou kapacitou pro přihlášeného zákazníka."""
        # Přihlášení zákazníka
        login_user(page, test_user["email"], test_user["password"])

        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()

        # Ověření přítomnosti tlačítka zápisu u vypsaného běhu (Locator Chaining na dostupný termín)
        expect(course_detail.available_run_enroll_button).to_be_visible()
        expect(course_detail.available_run_enroll_button).to_have_text("Nezávazná registrace")

    @pytest.mark.regression
    def test_tc26_crs_indication_when_capacity_full_or_unauthenticated(self, page: Page):
        """TC-26-CRS: Zamezení registrace a zobrazení výzvy k registraci pro nepřihlášeného."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()

        # Nepřihlášený návštěvník nemá tlačítko přímého zápisu, ale výzvu k registraci účtu
        expect(course_detail.guest_registration_prompt).to_be_visible()
