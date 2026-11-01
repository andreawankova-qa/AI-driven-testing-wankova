from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class ResetPasswordPage(BasePage):
    """Page Object reprezentující stránku pro nastavení nového hesla (/reset-password)."""

    URL = f"{settings.BASE_URL}/reset-password"

    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory s prioritou get_by_test_id
        self.form: Locator = page.get_by_test_id("reset_password_form")
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.password_again_input: Locator = page.get_by_test_id("password_again_input")
        self.submit_button: Locator = page.get_by_test_id("submit_button")

        # Chybová a stavová hlášení
        self.email_error: Locator = page.get_by_test_id("email_input_errors")
        self.password_error: Locator = page.get_by_test_id("password_input_errors")
        self.status_message: Locator = page.get_by_test_id("status_message")
        self.error_message: Locator = page.get_by_test_id("error_message")

    def open(self, token: str = None, email: str = None):
        """Otevře stránku pro nastavení nového hesla s tokenem a volitelným e-mailem."""
        query_params = []
        if token:
            query_params.append(f"token={token}")
        if email:
            query_params.append(f"email={email}")

        url = self.URL
        if query_params:
            url += f"?{'&'.join(query_params)}"

        self.navigate_to(url)
        return self

    def reset_password(self, password: str, password_again: str, email: str = None):
        """Vyplní formulář pro změnu hesla a odešle."""
        if email and self.email_input.is_visible():
            self.email_input.fill(email)
        self.password_input.fill(password)
        self.password_again_input.fill(password_again)
        self.submit_button.click()
        return self
