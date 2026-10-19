from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class HomePage(BasePage):
    """Page Object reprezentující úvodní stránku po úspěšné registraci (/home)."""

    URL = f"{settings.BASE_URL}/home"

    def __init__(self, page: Page):
        super().__init__(page)
        self.welcome_section: Locator = page.get_by_test_id("home_section")

    def open(self):
        """Otevře domovskou stránku přímo."""
        self.navigate_to(self.URL)
        return self
