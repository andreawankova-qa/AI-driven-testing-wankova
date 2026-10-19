from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class LoginPage(BasePage):
    """Page Object reprezentující přihlašovací stránku Demo Login (kitner.cz)."""

    URL = f"{settings.BASE_URL}/login"

    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory přes get_by_test_id
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.login_button: Locator = page.get_by_test_id("login_button")
        self.email_error: Locator = page.get_by_test_id("email_input_errors")
        self.password_error: Locator = page.get_by_test_id("password_input_errors")
        self.heading: Locator = page.get_by_test_id("login_text")
        self.register_link: Locator = page.get_by_test_id("register_link")
        self.forgot_password_link: Locator = page.get_by_test_id("forgot_password_link")

    def open(self):
        """Otevře přihlašovací stránku."""
        self.navigate_to(self.URL)
        self.email_input.wait_for(state="visible")
        return self

    def fill_email(self, email: str):
        """Vyplní email do vstupního pole."""
        self.email_input.fill(email)
        return self

    def fill_password(self, password: str):
        """Vyplní heslo do vstupního pole."""
        self.password_input.fill(password)
        return self

    def click_login(self):
        """Klikne na tlačítko Přihlásit."""
        self.login_button.click()
        return self

    def login(self, email: str, password: str):
        """Provede kompletní přihlašovací proces."""
        self.fill_email(email)
        self.fill_password(password)
        self.click_login()
        return self
