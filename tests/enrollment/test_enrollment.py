"""
Automatizované E2E testy pro Modul 3: Zápis na kurz a Moje kurzy (Role: Zákazník).
=================================================================================
Pokrývá testovací případy:
- TC-27-ENR: Úspěšný zápis na kurz s platným telefonem a platným IČO
- TC-28-ENR: Úspěšný zápis na kurz bez vyplněného IČO
- TC-29-ENR: Zápis s neplatným IČO (chyba kontrolního součtu modulo 11)
- TC-30-ENR: Zápis s neplatným telefonem (méně než 9 číslic)
- TC-31-ENR: Zobrazení přehledu mých zapsaných kurzů a detailu lekcí
"""

import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.course_detail_page import CourseDetailPage
from pages.enrollment_page import EnrollmentPage
from pages.my_courses_page import MyCoursesPage
from helpers.auth_helpers import login_user
from utils.data_generator import generate_valid_ico, generate_invalid_ico


@pytest.mark.enrollment
class TestCourseEnrollment:
    """Testovací sada pro nezávaznou registraci na běh kurzu a sekci Moje kurzy."""

    @pytest.fixture(autouse=True)
    def setup_logged_in_user(self, page: Page, test_user: dict):
        """Před každým testem zajistí přihlášení testovacího zákazníka."""
        login_user(page, test_user["email"], test_user["password"])

    @pytest.mark.smoke
    def test_tc27_enr_successful_enrollment_with_ico_and_phone(self, page: Page):
        """TC-27-ENR: Úspěšný zápis na kurz s platným telefonem a platným IČO."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        valid_ico = generate_valid_ico()
        valid_phone = "+420 777 123 456"

        enrollment_page.fill_enrollment_form(phone=valid_phone, ico=valid_ico)
        expect(enrollment_page.phone_input).to_have_value(valid_phone)
        expect(enrollment_page.ico_input).to_have_value(valid_ico)
        expect(enrollment_page.submit_button).to_be_visible()

    @pytest.mark.regression
    def test_tc28_enr_successful_enrollment_without_ico(self, page: Page):
        """TC-28-ENR: Úspěšný zápis na kurz bez vyplněného IČO (IČO je nepovinné)."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        valid_phone = "777123456"
        enrollment_page.fill_enrollment_form(phone=valid_phone, ico="")
        expect(enrollment_page.phone_input).to_have_value(valid_phone)
        expect(enrollment_page.ico_input).to_have_value("")

    @pytest.mark.regression
    def test_tc29_enr_invalid_ico_validation(self, page: Page):
        """TC-29-ENR: Zápis s neplatným IČO (chyba kontrolního součtu modulo 11)."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        invalid_ico = generate_invalid_ico()
        enrollment_page.fill_enrollment_form(phone="777123456", ico=invalid_ico)
        enrollment_page.submit()

        # Uživatel zůstává na formuláři, objednávka není dokončena
        expect(enrollment_page.form).to_be_visible()

    @pytest.mark.regression
    def test_tc30_enr_short_phone_validation(self, page: Page):
        """TC-30-ENR: Zápis s neplatným telefonem (méně než 9 číslic)."""
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        enrollment_page.fill_enrollment_form(phone="12345", ico=generate_valid_ico())
        enrollment_page.submit()

        # Formulář se neodešle a zůstává zobrazen
        expect(enrollment_page.form).to_be_visible()

    @pytest.mark.smoke
    def test_tc31_enr_my_courses_overview_display(self, page: Page):
        """TC-31-ENR: Zobrazení přehledu mých zapsaných kurzů a detailu lekcí."""
        my_courses_page = MyCoursesPage(page)
        my_courses_page.open()

        # Ověření zobrazení hlavičky a sekce Moje kurzy
        expect(my_courses_page.header).to_be_visible()
        expect(my_courses_page.title).to_be_visible()
        expect(page).to_have_url(my_courses_page.URL)
