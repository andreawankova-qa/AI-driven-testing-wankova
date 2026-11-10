import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class ParticipantsPage(BasePage):
    """Page Object reprezentující stránku se seznamem přihlášených účastníků kurzu."""

    URL_PATTERN = re.compile(r".*/courses/\d+/participants")

    def __init__(self, page: Page):
        super().__init__(page)
        self.section: Locator = page.get_by_test_id("courses_section")
        self.header_title: Locator = page.get_by_test_id("header_title")
        self.table: Locator = page.get_by_test_id("participants_table")
        self.table_header: Locator = page.get_by_test_id("table_header")
        self.name_header: Locator = page.get_by_test_id("name_header")
        self.email_header: Locator = page.get_by_test_id("email_header")
        self.phone_header: Locator = page.get_by_test_id("phone_header")
        self.ico_header: Locator = page.get_by_test_id("ico_header")
        self.rows: Locator = page.get_by_test_id(re.compile(r"^participant_row_"))
        self.name_cells: Locator = page.get_by_test_id(re.compile(r"^participant_name_"))
        self.email_cells: Locator = page.get_by_test_id(re.compile(r"^participant_email_"))
        self.phone_cells: Locator = page.get_by_test_id(re.compile(r"^participant_phone_"))
        self.ico_cells: Locator = page.get_by_test_id(re.compile(r"^participant_ico_"))

        # Primární záznam účastníka (konkrétní stabilní selektory bez nutnosti indexů)
        self.primary_row: Locator = page.get_by_test_id("participant_row_0")
        self.primary_name: Locator = page.get_by_test_id("participant_name_0")
        self.primary_email: Locator = page.get_by_test_id("participant_email_0")
        self.primary_phone: Locator = page.get_by_test_id("participant_phone_0")
        self.primary_ico: Locator = page.get_by_test_id("participant_ico_0")

    def open(self, course_id: int = 1):
        """Otevře stránku účastníků kurzu přímo podle ID kurzu."""
        self.navigate_to(f"{settings.BASE_URL}/courses/{course_id}/participants")
        return self

    def get_row(self, index: int = 0) -> Locator:
        """Vrátí lokátor konkrétního řádku účastníka podle indexu."""
        return self.page.get_by_test_id(f"participant_row_{index}")

    def get_participant_name(self, index: int = 0) -> Locator:
        """Vrátí lokátor buňky se jménem účastníka."""
        return self.page.get_by_test_id(f"participant_name_{index}")

    def get_participant_email(self, index: int = 0) -> Locator:
        """Vrátí lokátor buňky s e-mailem účastníka."""
        return self.page.get_by_test_id(f"participant_email_{index}")

    def get_participant_phone(self, index: int = 0) -> Locator:
        """Vrátí lokátor buňky s telefonem účastníka."""
        return self.page.get_by_test_id(f"participant_phone_{index}")

    def get_participant_ico(self, index: int = 0) -> Locator:
        """Vrátí lokátor buňky s IČO účastníka."""
        return self.page.get_by_test_id(f"participant_ico_{index}")
