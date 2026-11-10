import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class CreateIterationPage(BasePage):
    """Page Object pro formulář vypsání nového termínu (iterace) kurzu lektorem (/courses/:id/create-iteration)."""

    URL_PATTERN = re.compile(r".*/courses/\d+/create-iteration")

    def __init__(self, page: Page):
        super().__init__(page)
        self.form: Locator = page.get_by_test_id("course_iteration_form")
        self.start_input: Locator = page.get_by_test_id("course_start_input")
        self.end_input: Locator = page.get_by_test_id("course_end_input")
        self.day_select: Locator = page.get_by_test_id("course_day_select")
        self.time_input: Locator = page.get_by_test_id("course_time_input")
        self.location_input: Locator = page.get_by_test_id("course_location_input")
        self.submit_button: Locator = self.form.get_by_test_id("registration_link")

    def open(self, course_id: int = 1):
        """Otevře stránku vytvoření termínu pro daný kurz."""
        self.navigate_to(f"{settings.BASE_URL}/courses/{course_id}/create-iteration")
        return self

    def fill_iteration_form(
        self,
        start_date: str = None,
        end_date: str = None,
        day: str = None,
        time: str = None,
        location: str = None
    ):
        """Vyplní formulář pro vypsání nového termínu kurzu."""
        if start_date:
            self.start_input.fill(start_date)
        if end_date:
            self.end_input.fill(end_date)
        if day:
            self.day_select.select_option(day)
        if time:
            self.time_input.fill(time)
        if location:
            self.location_input.fill(location)
        return self

    def submit(self):
        """Odešle formulář pro vypsání nového termínu."""
        self.submit_button.click()
        return self
