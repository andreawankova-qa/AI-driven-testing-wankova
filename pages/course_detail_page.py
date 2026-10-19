from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class CourseDetailPage(BasePage):
    """Page Object reprezentující detail konkrétního kurzu a jeho vypsaných termínů."""

    def __init__(self, page: Page, course_id: int = 1):
        super().__init__(page)
        self.course_id = course_id
        self.URL = f"{settings.BASE_URL}/courses/{course_id}"
        self.heading: Locator = page.locator("h1, h2").first
        self.runs_heading: Locator = page.locator("text=Vypsané běhy kurzu:")
        self.enroll_buttons: Locator = page.locator("text=Nezávazná registrace")
        self.guest_registration_prompt: Locator = page.locator("text=Zaregistrujte se zde")

    def open(self, course_id: int = None):
        """Otevře detail kurzu přímo."""
        c_id = course_id or self.course_id
        self.navigate_to(f"{settings.BASE_URL}/courses/{c_id}")
        return self

    def click_first_enroll_button(self):
        """Klikne na první dostupné tlačítko pro nezávaznou registraci."""
        self.enroll_buttons.first.click()
        return self
