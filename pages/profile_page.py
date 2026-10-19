from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class ProfilePage(BasePage):
    """Page Object reprezentující správu uživatelského profilu (/profile)."""

    URL = f"{settings.BASE_URL}/profile"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading: Locator = page.get_by_test_id("profile_heading")
        self.form: Locator = page.get_by_test_id("profile_form")
        self.name_input: Locator = page.get_by_test_id("profile_name_input")
        self.email_input: Locator = page.get_by_test_id("profile_email_input")
        self.ico_input: Locator = page.get_by_test_id("profile_ico_input")
        self.phone_input: Locator = page.get_by_test_id("profile_phone_input")
        self.save_button: Locator = page.get_by_test_id("registration_link")

    def open(self):
        """Otevře profil přímo přes URL."""
        self.navigate_to(self.URL)
        return self

    def update_profile(self, name: str = None, email: str = None, ico: str = None, phone: str = None):
        """Vyplní formulář profilu a uloží změny."""
        if name is not None:
            self.name_input.fill(name)
        if email is not None:
            self.email_input.fill(email)
        if ico is not None:
            self.ico_input.fill(ico)
        if phone is not None:
            self.phone_input.fill(phone)
        self.save_button.click()
        return self
