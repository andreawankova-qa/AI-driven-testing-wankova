from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class MyCoursesPage(BasePage):
    """Page Object reprezentující sekci Moje kurzy pro přihlášeného studenta."""

    URL = f"{settings.BASE_URL}/my-courses"

    def __init__(self, page: Page):
        super().__init__(page)
        self.header: Locator = page.get_by_test_id("courses_header")
        self.title: Locator = page.get_by_test_id("courses_title")
        self.section: Locator = page.get_by_test_id("courses_section")

    def open(self):
        """Otevře sekci Moje kurzy přímo."""
        self.navigate_to(self.URL)
        return self
