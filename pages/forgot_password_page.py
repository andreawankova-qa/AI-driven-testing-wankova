from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class ForgotPasswordPage(BasePage):
    """Page Object reprezentující stránku pro obnovení zapomenutého hesla."""

    URL = f"{settings.BASE_URL}/forgot-password"

    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory s řetězením kontejnerů přes get_by_test_id
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.submit_button: Locator = page.get_by_test_id("submit_button")
        self.info_text: Locator = page.get_by_test_id("forget_password_p")
        self.login_link: Locator = self.navbar.login_link

    def open(self):
        """Otevře stránku pro obnovení hesla."""
        self.navigate_to(self.URL)
        self.email_input.wait_for(state="visible")
        return self

    def fill_email(self, email: str):
        """Vyplní e-mail pro obnovu hesla."""
        self.email_input.fill(email)
        return self

    def submit(self):
        """Odešle formulář pro obnovu hesla."""
        self.submit_button.click()
        return self

    def request_password_reset(self, email: str):
        """Vyplní e-mail a odešle požadavek na reset hesla."""
        self.fill_email(email)
        self.submit()
        return self
