from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class EmailVerificationPage(BasePage):
    """Page Object reprezentující stránku pro ověření e-mailu a výzvu k ověření."""

    VERIFY_URL = f"{settings.BASE_URL}/overeni-emailu"
    PROMPT_URL = f"{settings.BASE_URL}/email/verify"

    def __init__(self, page: Page):
        super().__init__(page)
        self.container: Locator = page.get_by_test_id("page_container")

    def open_verification_link(self, token: str = None):
        """Otevře verifikační odkaz s tokenem."""
        url = self.VERIFY_URL
        if token:
            url += f"?token={token}"
        self.navigate_to(url)
        return self

    def open_prompt(self):
        """Otevře stránku s výzvou k ověření e-mailu."""
        self.navigate_to(self.PROMPT_URL)
        return self
