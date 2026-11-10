import re
from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class CourseDetailPage(BasePage):
    """Page Object reprezentující detail konkrétního kurzu a jeho vypsaných termínů."""

    def __init__(self, page: Page, course_id: int = 1):
        super().__init__(page)
        self.course_id = course_id
        self.URL = f"{settings.BASE_URL}/courses/{course_id}"
        self.container: Locator = page.get_by_test_id("course_detail")
        self.heading: Locator = page.get_by_test_id("course_name")
        self.description: Locator = page.get_by_test_id("course_description")
        self.price: Locator = page.get_by_test_id("course_price")
        self.runs_heading: Locator = page.get_by_test_id("iterations_heading")
        self.iterations: Locator = page.get_by_test_id(re.compile(r"^iteration_"))
        self.primary_iteration: Locator = page.get_by_test_id("iteration_1")
        # Plně obsazená iterace (např. Kapacita: 12/12)
        self.full_iteration: Locator = page.get_by_test_id("iteration_2")
        self.guest_registration_prompt: Locator = self.container.get_by_test_id("registration_link")

    @property
    def available_run_enroll_button(self) -> Locator:
        """Vrátí první dostupné tlačítko pro nezávaznou registraci."""
        buttons = self.container.get_by_role("button", name="Nezávazná registrace").all()
        if buttons:
            return buttons[0]
        return self.container.get_by_test_id("registration_link")

    def open(self, course_id: int = None):
        """Otevře detail kurzu přímo."""
        c_id = course_id or self.course_id
        self.navigate_to(f"{settings.BASE_URL}/courses/{c_id}")
        return self

    def get_run_enroll_button(self, iteration_testid: str = "iteration_24") -> Locator:
        """Vrátí lokátor tlačítka zápisu pro konkrétní vypsaný termín."""
        return self.page.get_by_test_id(iteration_testid).get_by_test_id("registration_link")

    def click_first_enroll_button(self):
        """Klikne na dostupné tlačítko pro nezávaznou registraci."""
        self.available_run_enroll_button.click()
        return self

    def click_iteration_participants(self, iteration: Locator = None):
        """Klikne na tlačítko zobrazení účastníků u vybraného běhu (pro lektora)."""
        target_iteration = iteration or self.primary_iteration
        target_iteration.get_by_test_id("registration_link").click()
        return self
