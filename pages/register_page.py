from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class RegisterPage(BasePage):
    """Page Object reprezentující registrační stránku."""

    URL = f"{settings.BASE_URL}/register"

    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory přes get_by_test_id
        self.name_input: Locator = page.get_by_test_id("name_input")
        self.email_input: Locator = page.get_by_test_id("email_input")
        self.password_input: Locator = page.get_by_test_id("password_input")
        self.password_again_input: Locator = page.get_by_test_id("password_again_input")

        # Tlačítka a formulář
        self.register_button: Locator = page.get_by_test_id("register_button")
        self.register_form: Locator = page.get_by_test_id("register_form")
        self.heading: Locator = page.get_by_test_id("register_text")

        # Validační chybové zprávy
        self.name_error: Locator = page.get_by_test_id("name_input_errors")
        self.email_error: Locator = page.get_by_test_id("email_input_errors")
        self.password_error: Locator = page.get_by_test_id("password_input_errors")

        # Navigační odkazy s využitím řetězení kontejneru (Locator Chaining)
        self.login_link: Locator = page.get_by_test_id("register_section").get_by_test_id("login_link")
        self.forgot_password_link: Locator = page.get_by_test_id("forgot_password_link")

    def open(self):
        """Otevře registrační stránku a počká na vykreslení formuláře."""
        self.navigate_to(self.URL)
        self.name_input.wait_for(state="visible")
        return self

    def fill_name(self, name: str):
        """Vyplní jméno uživatele."""
        self.name_input.fill(name)
        return self

    def fill_email(self, email: str):
        """Vyplní email uživatele."""
        self.email_input.fill(email)
        return self

    def fill_password(self, password: str):
        """Vyplní heslo uživatele."""
        self.password_input.fill(password)
        return self

    def fill_password_again(self, password: str):
        """Vyplní potvrzení hesla."""
        self.password_again_input.fill(password)
        return self

    def click_register(self):
        """Klikne na tlačítko pro registraci."""
        self.register_button.click()
        return self

    def register(self, name: str, email: str, password: str, password_again: str = None):
        """Provede kompletní proces registrace uživatele."""
        if password_again is None:
            password_again = password
        self.fill_name(name)
        self.fill_email(email)
        self.fill_password(password)
        self.fill_password_again(password_again)
        self.click_register()
        return self
