from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class EnrollmentPage(BasePage):
    """Page Object pro formulář nezávazného zápisu na běh kurzu."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.title: Locator = page.get_by_test_id("registration_title")
        self.form: Locator = page.get_by_test_id("registration_form")
        self.ico_input: Locator = page.get_by_test_id("ico_input")
        self.phone_input: Locator = page.get_by_test_id("phone_input")
        self.submit_button: Locator = page.get_by_test_id("registration_link")

    def fill_enrollment_form(self, phone: str, ico: str = None):
        """Vyplní formulář zápisu na kurz."""
        if phone is not None:
            self.phone_input.fill(phone)
        if ico is not None:
            self.ico_input.fill(ico)
        return self

    def submit(self):
        """Odešle formulář pro zápis na kurz."""
        self.submit_button.click()
        return self
