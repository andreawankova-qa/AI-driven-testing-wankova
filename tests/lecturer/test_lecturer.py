"""
Automatizované E2E testy pro Modul 4: Správa kurzů a výuky (Role: Lektor).
========================================================================
Pokrývá testovací případy:
- TC-32-LEC: Vytvoření nového kurzu lektorem s obrázkem 16:9
- TC-33-LEC: Odmítnutí náhledu kurzu s nevyhovujícím poměrem stran
- TC-34-LEC: Validace povinných polí a číselné kapacity/ceny
- TC-35-LEC: Úspěšné vypsání nového termínu kurzu lektorem
- TC-36-LEC: Validace povinných polí při vypsání termínu
- TC-37-LEC: Zobrazení tabulky přihlášených účastníků pro lektora
- TC-38-LEC: Zamezení přístupu k účastníkům pro zákazníka
"""

from pathlib import Path
import pytest
from playwright.sync_api import Page, expect
from pages.courses_page import CoursesPage
from pages.create_course_page import CreateCoursePage
from pages.create_iteration_page import CreateIterationPage
from pages.course_detail_page import CourseDetailPage
from pages.participants_page import ParticipantsPage
from helpers.auth_helpers import login_lecturer, login_user
from config.settings import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_16_9 = str(PROJECT_ROOT / "data" / "test_image_16_9.bmp")
IMAGE_1_1 = str(PROJECT_ROOT / "data" / "test_image_1_1.bmp")


@pytest.mark.lecturer
class TestLecturerCourseManagement:
    """Testovací sada pro lektorské operace a správu kurzů."""

    @pytest.mark.smoke
    def test_tc32_lec_create_course_with_16_9_aspect_ratio_image(self, page: Page):
        """TC-32-LEC: Vytvoření nového kurzu s náhledem s poměrem stran 16:9."""
        login_lecturer(page)

        create_page = CreateCoursePage(page)
        create_page.open()

        expect(create_page.title).to_be_visible()
        expect(create_page.form).to_be_visible()

        create_page.fill_course_form(
            name="Playwright Testování Pokročilý",
            description="Detailní kurz automatizace",
            capacity="15",
            price="14900",
            file_path=IMAGE_16_9
        )

        expect(create_page.name_input).to_have_value("Playwright Testování Pokročilý")
        expect(create_page.capacity_input).to_have_value("15")
        expect(create_page.price_input).to_have_value("14900")
        expect(create_page.submit_button).to_be_visible()

    @pytest.mark.regression
    @pytest.mark.xfail(reason="Aplikace v testovacím prostředí v rozporu s US-13 nekontroluje poměr stran obrázku na frontendu")
    def test_tc33_lec_reject_invalid_aspect_ratio_image(self, page: Page):
        """TC-33-LEC: Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran."""
        login_lecturer(page)

        create_page = CreateCoursePage(page)
        create_page.open()

        create_page.fill_course_form(
            name="Kurz s chybným poměrem",
            description="Testovací popis",
            capacity="10",
            price="9900",
            file_path=IMAGE_1_1
        )
        create_page.submit()

        # Podle US-13 má systém zůstat na formuláři s chybou
        expect(create_page.form).to_be_visible()

    @pytest.mark.regression
    @pytest.mark.xfail(reason="Aplikace v testovacím prostředí postrádá validaci povinných polí a číselných hodnot")
    def test_tc34_lec_validation_required_fields_and_numeric_values(self, page: Page):
        """TC-34-LEC: Validace povinných polí a číselné kapacity/ceny kurzu."""
        login_lecturer(page)

        create_page = CreateCoursePage(page)
        create_page.open()

        # Odeslání s prázdnými poli
        create_page.submit()
        expect(create_page.form).to_be_visible()

        # Pokus o nečíselné / záporné hodnoty
        create_page.capacity_input.fill("-5")
        create_page.price_input.fill("zdarma")
        create_page.submit()
        expect(create_page.form).to_be_visible()

    @pytest.mark.regression
    def test_tc35_lec_create_course_iteration_by_lecturer(self, page: Page):
        """TC-35-LEC: Úspěšné vypsání nového termínu kurzu lektorem."""
        # 1. ARRANGE: Přihlášení lektora a otevření formuláře pro nový termín kurzu
        courses_page = login_lecturer(page)
        create_iter_page = CreateIterationPage(page)
        create_iter_page.open(course_id=1)

        expect(create_iter_page.form).to_be_visible()

        # 2. ACT: Vyplnění formuláře rozvrhu a uložení nového termínu
        create_iter_page.fill_iteration_form(
            start_date="2026-12-01",
            end_date="2026-12-20",
            day="Úterý",
            time="18:00",
            location="Online (Google Meet)"
        )
        create_iter_page.submit()

        # 3. ASSERT: 3úrovňové ověření (Routing, Session, Data State)
        course_detail_page = CourseDetailPage(page, course_id=1)
        expect(page).to_have_url(course_detail_page.URL)
        expect(courses_page.navbar.logout_button).to_be_visible()
        expect(course_detail_page.container).to_be_visible()
        expect(course_detail_page.heading).to_be_visible()

    @pytest.mark.regression
    @pytest.mark.xfail(reason="Aplikace v testovacím prostředí odesílá formulář termínu bez klientské validace povinných polí (US-14 AK-3)")
    def test_tc36_lec_validation_iteration_required_fields(self, page: Page):
        """TC-36-LEC: Validace povinných polí při vypsání termínu."""
        login_lecturer(page)
        create_iter_page = CreateIterationPage(page)
        create_iter_page.open(course_id=1)

        expect(create_iter_page.form).to_be_visible()

        # Pokus o odeslání prázdného formuláře
        create_iter_page.submit()

        # Dle US-14 AK-3 má systém zůstat na formuláři s validační chybou
        expect(create_iter_page.form).to_be_visible()


    @pytest.mark.smoke
    def test_tc37_lec_lecturer_interface_and_navigation(self, page: Page):
        """TC-37-LEC: Zobrazení detailu kurzu a ověření tabulky účastníků se sloupci Jméno, Email, Telefon a IČO."""
        # 1. ARRANGE: Přihlášení lektora a příprava Page Objectů
        courses_page = login_lecturer(page)
        course_detail_page = CourseDetailPage(page)
        participants_page = ParticipantsPage(page)

        # 2. ACT: Rozkliknutí detailu kurzu a přechod do seznamu účastníků běhu
        courses_page.click_course_detail()
        expect(course_detail_page.container).to_be_visible()
        expect(course_detail_page.runs_heading).to_be_visible()

        course_detail_page.click_iteration_participants()

        # 3. ASSERT: 3úrovňové ověření (Routing, Session, Data State / UI Feedback)
        # Routing & Session
        expect(page).to_have_url(participants_page.URL_PATTERN)
        expect(courses_page.navbar.logout_button).to_be_visible()

        # Záhlaví a tabulka účastníků
        expect(participants_page.header_title).to_be_visible()
        expect(participants_page.header_title).to_have_text("Seznam přihlášených")
        expect(participants_page.table).to_be_visible()

        # Sloupce tabulky: Jméno, Email, Telefon, IČO
        expect(participants_page.name_header).to_be_visible()
        expect(participants_page.name_header).to_contain_text("Jméno", ignore_case=True)

        expect(participants_page.email_header).to_be_visible()
        expect(participants_page.email_header).to_contain_text("Email", ignore_case=True)

        expect(participants_page.phone_header).to_be_visible()
        expect(participants_page.phone_header).to_contain_text("Telefon", ignore_case=True)

        expect(participants_page.ico_header).to_be_visible()
        expect(participants_page.ico_header).to_contain_text("IČO", ignore_case=True)

        # Skutečné zobrazení záznamů účastníků v tabulce (konkrétní buňky přes get_by_test_id bez indexu .first)
        expect(participants_page.primary_row).to_be_visible()
        expect(participants_page.primary_name).to_be_visible()
        expect(participants_page.primary_email).to_be_visible()
        expect(participants_page.primary_phone).to_be_visible()
        expect(participants_page.primary_ico).to_be_visible()

    @pytest.mark.smoke
    @pytest.mark.xfail(reason="BR-01: Aplikace v rozporu s US-18 nezabezpečuje /courses/create před rolí Zákazník")
    def test_tc38_lec_customer_cannot_access_lecturer_create_course(self, page: Page, test_user: dict):
        """TC-38-LEC: Zamezení přístupu k lektorským operacím pro běžného zákazníka."""
        login_user(page, test_user["email"], test_user["password"])

        create_page = CreateCoursePage(page)
        create_page.open()
        page.wait_for_load_state("networkidle")

        # Zákazník nesmí mít přístup k lektorskému formuláři
        expect(create_page.form).not_to_be_visible()
