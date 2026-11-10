"""
Automatizované E2E testy pro Modul 3: Zápis na kurz a Moje kurzy (Role: Zákazník).
=================================================================================
Pokrývá testovací případy:
- TC-27-ENR: Úspěšný zápis na kurz s platným telefonem a platným IČO
- TC-28-ENR: Úspěšný zápis na kurz bez vyplněného IČO
- TC-29-ENR: Zápis s neplatným IČO (chyba kontrolního součtu modulo 11)
- TC-30-ENR: Zápis s neplatným telefonem (méně než 9 číslic)
- TC-31-ENR: Zobrazení přehledu mých zapsaných kurzů a detailu lekcí
- TC-48-ENR: Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State)
"""

import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.course_detail_page import CourseDetailPage
from pages.enrollment_page import EnrollmentPage
from pages.my_courses_page import MyCoursesPage
from pages.profile_page import ProfilePage
from helpers.auth_helpers import login_user, register_and_login_user
from config.settings import settings
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
        # 1. ARRANGE: Otevření detailu kurzu a přechod do formuláře zápisu
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        valid_ico = generate_valid_ico()
        valid_phone = "+420 777 123 456"

        # 2. ACT: Vyplnění platných údajů a odeslání nezávazné registrace
        enrollment_page.fill_enrollment_form(phone=valid_phone, ico=valid_ico)
        expect(enrollment_page.phone_input).to_have_value(valid_phone)
        expect(enrollment_page.ico_input).to_have_value(valid_ico)
        enrollment_page.submit()

        # 3. ASSERT: 3úrovňové ověření (Routing, Session, Data State a propsání do profilu)
        my_courses_page = MyCoursesPage(page)
        expect(page).to_have_url(my_courses_page.URL)
        expect(my_courses_page.navbar.logout_button).to_be_visible()
        expect(my_courses_page.section).to_be_visible()
        expect(my_courses_page.section).to_contain_text("Mé zapsané kurzy")

        # Ověření propsání zadaných údajů do profilu zákazníka (US-11 AK-7)
        profile_page = ProfilePage(page)
        profile_page.open()
        expect(profile_page.phone_input).to_have_value(valid_phone)
        expect(profile_page.ico_input).to_have_value(valid_ico)

    @pytest.mark.regression
    @pytest.mark.xfail(reason="Aplikace v rozporu s US-11 AK-3 vyžaduje IČO jako povinné a při prázdném poli hlásí Neplatné IČO")
    def test_tc28_enr_successful_enrollment_without_ico(self, page: Page):
        """TC-28-ENR: Úspěšný zápis na kurz bez vyplněného IČO (IČO je nepovinné)."""
        # 1. ARRANGE: Otevření detailu kurzu a přechod do formuláře zápisu
        course_detail = CourseDetailPage(page, course_id=1)
        course_detail.open()
        course_detail.click_first_enroll_button()

        enrollment_page = EnrollmentPage(page)
        expect(enrollment_page.form).to_be_visible()

        valid_phone = "777123456"

        # 2. ACT: Vyplnění pouze telefonu (IČO nepovinné) a odeslání
        enrollment_page.fill_enrollment_form(phone=valid_phone, ico="")
        expect(enrollment_page.phone_input).to_have_value(valid_phone)
        expect(enrollment_page.ico_input).to_have_value("")
        enrollment_page.submit()

        # 3. ASSERT: Přesměrování do Moje kurzy a zobrazení zapsaných kurzů
        my_courses_page = MyCoursesPage(page)
        expect(page).to_have_url(my_courses_page.URL)
        expect(my_courses_page.navbar.logout_button).to_be_visible()
        expect(my_courses_page.section).to_be_visible()

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
        # 1. ARRANGE: Otevření sekce Moje kurzy pro přihlášeného studenta
        my_courses_page = MyCoursesPage(page)
        my_courses_page.open()

        # 2. ASSERT: 3úrovňové ověření (Routing, Session, Data State)
        # Routing & Session (AK-1)
        expect(page).to_have_url(my_courses_page.URL)
        expect(my_courses_page.navbar.logout_button).to_be_visible()
        expect(my_courses_page.header).to_be_visible()
        expect(my_courses_page.title).to_have_text("Mé zapsané kurzy")

        # Karta zapsaného kurzu a její atributy: název, popis, cena, obrázek (AK-2, AK-3)
        expect(my_courses_page.primary_course_card).to_be_visible()
        expect(my_courses_page.course_name).to_be_visible()
        expect(my_courses_page.course_description).to_be_visible()
        expect(my_courses_page.course_price).to_be_visible()
        expect(my_courses_page.course_price).to_contain_text("Kč")
        expect(my_courses_page.course_image).to_be_visible()

        # Organizační údaje lekcí běhu kurzu: data, den, čas, místo (AK-4, AK-5, AK-6)
        expect(my_courses_page.date_time_from).to_be_visible()
        expect(my_courses_page.date_time_from).to_contain_text("První lekce:")

        expect(my_courses_page.date_time_to).to_be_visible()
        expect(my_courses_page.date_time_to).to_contain_text("Poslední lekce:")

        expect(my_courses_page.day_information).to_be_visible()
        expect(my_courses_page.day_information).to_contain_text("Kdy:")

        expect(my_courses_page.place_information).to_be_visible()
        expect(my_courses_page.place_information).to_contain_text("Kde:")

        # Přechod na detail daného kurzu (AK-7)
        my_courses_page.click_course_detail()
        course_detail = CourseDetailPage(page, course_id=1)
        expect(page).to_have_url(course_detail.URL)
        expect(course_detail.container).to_be_visible()


@pytest.mark.enrollment
class TestMyCoursesOverview:
    """Testovací sada pro přehled a zobrazení sekce Moje kurzy (US-12)."""

    @pytest.mark.regression
    def test_tc48_enr_empty_state_my_courses_without_enrollments(self, page: Page):
        """TC-48-ENR: Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State)."""
        # =====================================================================
        # 1. ARRANGE: Registrace a přihlášení nového uživatele bez zapsaných kurzů
        # =====================================================================
        register_and_login_user(page)
        my_courses_page = MyCoursesPage(page)

        # =====================================================================
        # 2. ACT: Přechod do sekce Moje kurzy přes horní navigaci
        # =====================================================================
        my_courses_page.navbar.click_my_courses()

        # =====================================================================
        # 3. ASSERT: 3úrovňová validace (Routing, Session, Data State - Empty)
        # =====================================================================
        # Úroveň 1: Routing
        expect(page).to_have_url(my_courses_page.URL)

        # Úroveň 2: Session
        expect(my_courses_page.navbar.logout_button).to_be_visible()

        # Úroveň 3: Data State / UI Feedback (zobrazení sekce a absence kurzových karet)
        expect(my_courses_page.section).to_be_visible()
        expect(my_courses_page.header).to_be_visible()
        expect(my_courses_page.title).to_have_text("Mé zapsané kurzy")
        expect(my_courses_page.course_cards).to_have_count(0)

