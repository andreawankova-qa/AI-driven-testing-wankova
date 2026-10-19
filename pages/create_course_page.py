from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class CreateCoursePage(BasePage):
    """Page Object pro formulář vytvoření nového kurzu lektorem (/courses/create)."""

    URL = f"{settings.BASE_URL}/courses/create"

    def __init__(self, page: Page):
        super().__init__(page)
        self.title: Locator = page.get_by_test_id("create_course_title")
        self.form: Locator = page.get_by_test_id("course_form")
        self.name_input: Locator = page.get_by_test_id("course_name_input")
        self.description_input: Locator = page.get_by_test_id("course_description_input")
        self.capacity_input: Locator = page.get_by_test_id("course_capacity_input")
        self.price_input: Locator = page.get_by_test_id("course_price_input")
        self.file_input: Locator = page.get_by_test_id("course_file_input")
        self.submit_button: Locator = page.get_by_test_id("registration_link")

    def open(self):
        """Otevře stránku vytvoření kurzu."""
        self.navigate_to(self.URL)
        return self

    def fill_course_form(self, name: str, description: str, capacity: str, price: str, file_path: str = None):
        """Vyplní formulář pro vytvoření kurzu."""
        self.name_input.fill(name)
        self.description_input.fill(description)
        self.capacity_input.fill(str(capacity))
        self.price_input.fill(str(price))
        if file_path:
            self.file_input.set_input_files(file_path)
        return self

    def submit(self):
        """Odešle formulář nového kurzu."""
        self.submit_button.click()
        return self
