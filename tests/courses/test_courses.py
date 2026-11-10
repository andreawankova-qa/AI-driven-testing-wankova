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
from pages.enrollment_page import EnrollmentPage
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
        expect(courses_page.primary_course_card).to_be_visible()
        expect(courses_page.course_cards).not_to_have_count(0)

        # Ověření přítomnosti výzvy k registraci pod katalogem pro nepřihlášeného
        expect(courses_page.navbar.login_link).to_be_visible()

    @pytest.mark.regression
    def test_tc23_crs_course_card_attributes(self, page: Page):
        """TC-23-CRS: Ověření zobrazení atributů kurzu v katalogu."""
        courses_page = CoursesPage(page)
        courses_page.open()

        # Karta kurzu přes Page Object (stabilní get_by_test_id bez křehkého indexu .first)
        card = courses_page.primary_course_card
        expect(card).to_be_visible()

        # Kontrola názvu, popisu, ceny, kapacity a náhledu přes Page Object
        expect(courses_page.get_card_name(card)).to_be_visible()
        expect(courses_page.get_card_description(card)).to_be_visible()
        expect(courses_page.get_card_price(card)).to_be_visible()
        expect(courses_page.get_card_capacity(card)).to_be_visible()
        expect(courses_page.get_card_image(card)).to_be_visible()

        # Cena obsahuje měnu a je zaokrouhlena (např. Kč) – web-first ověření
        expect(courses_page.get_card_price(card)).to_contain_text(re.compile(r"Kč|\d+", re.IGNORECASE))

    @pytest.mark.smoke
    def test_tc24_crs_course_detail_and_iterations_display(self, page: Page):
        """TC-24-CRS: Zobrazení detailu kurzu a seznamu vypsaných termínů."""
        # 1. ARRANGE & ACT: Přechod z katalogu na detail kurzu (US-08 AK-4)
        courses_page = CoursesPage(page)
        courses_page.open()
        courses_page.click_course_detail()

        # 2. ASSERT: 3úrovňové ověření detailu kurzu a jeho atributů (US-09 AK-1, AK-2, AK-3)
        course_detail = CourseDetailPage(page, course_id=1)
        expect(page).to_have_url(course_detail.URL)

        # Název, popis, cena kurzu
        expect(course_detail.heading).to_be_visible()
        expect(course_detail.description).to_be_visible()
        expect(course_detail.price).to_be_visible()
        expect(course_detail.price).to_contain_text("Kč")

        # Sekce běhů kurzu a organizační údaje (zahájení, ukončení, kapacita)
        expect(course_detail.runs_heading).to_be_visible()
        expect(course_detail.primary_iteration).to_be_visible()
        expect(course_detail.primary_iteration).to_contain_text("Zahájení:")
        expect(course_detail.primary_iteration).to_contain_text("Ukončení:")
        expect(course_detail.primary_iteration).to_contain_text("Kapacita:")

    @pytest.mark.smoke
    def test_tc25_crs_enrollment_button_for_available_capacity(self, page: Page, test_user: dict):
        """TC-25-CRS: Zobrazení tlačítka zápisu u termínu s volnou kapacitou pro přihlášeného zákazníka."""
        # 1. ARRANGE: Přihlášení zákazníka a přechod na detail kurzu
        login_user(page, test_user["email"], test_user["password"])

        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()

        # 2. ACT & ASSERT: Ověření tlačítka zápisu u vypsaného běhu s volnou kapacitou
        expect(course_detail.available_run_enroll_button).to_be_visible()
        expect(course_detail.available_run_enroll_button).to_have_text("Nezávazná registrace")

        # Kliknutí na tlačítko a ověření přesměrování do objednávkového formuláře
        course_detail.click_first_enroll_button()
        enrollment_page = EnrollmentPage(page)
        expect(page).to_have_url(re.compile(r".*/courses/\d+/register.*"))
        expect(enrollment_page.form).to_be_visible()

    @pytest.mark.regression
    def test_tc26_crs_indication_when_capacity_full_or_unauthenticated(self, page: Page, test_user: dict):
        """TC-26-CRS: Zamezení registrace a indikace plně obsazeného běhu i výzva pro nepřihlášeného."""
        course_detail = CourseDetailPage(page, course_id=1)

        # 1. Krok: Nepřihlášený návštěvník nemá tlačítko přímého zápisu, ale výzvu k přihlášení/registraci
        course_detail.open()
        expect(course_detail.guest_registration_prompt).to_be_visible()

        # 2. Krok: Přihlášený zákazník na detailu kurzu – ověření plně obsazeného termínu
        login_user(page, test_user["email"], test_user["password"])
        course_detail.open()

        # Vyhledání běhu s plně obsazenou kapacitou (např. 12/12)
        expect(course_detail.full_iteration).to_be_visible()
        expect(course_detail.full_iteration).to_contain_text(re.compile(r"Kapacita:\s*12/12"))

        # Zamezení registrace: plně obsazený běh nemá tlačítko pro registraci
        expect(course_detail.full_iteration.get_by_test_id("registration_link")).not_to_be_visible()
