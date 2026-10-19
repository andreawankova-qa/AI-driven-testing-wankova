from playwright.sync_api import Page, Locator
from pages.base_page import BasePage
from config.settings import settings


class CoursesPage(BasePage):
    """Page Object reprezentující stránku přehledu kurzů po přihlášení."""

    URL = f"{settings.BASE_URL}/courses"
    CREATE_URL = f"{settings.BASE_URL}/courses/create"

    def __init__(self, page: Page):
        super().__init__(page)
        # Nativní Playwright lokátory s řetězením kontejnerů přes get_by_test_id
        self.courses_header: Locator = page.get_by_test_id("courses_header")
        self.add_course_button: Locator = self.courses_header.get_by_test_id("registration_link")
        # Formulář pro tvorbu kurzu (lektorská práva)
        self.course_form: Locator = page.get_by_test_id("course_form")
        self.course_name_input: Locator = page.get_by_test_id("course_name_input")
        # Karty kurzů a jejich atributy
        self.course_cards: Locator = page.locator('[data-testid^="course_"]')
        self.course_names: Locator = page.get_by_test_id("course_name")
        self.course_descriptions: Locator = page.get_by_test_id("course_description")
        self.course_prices: Locator = page.get_by_test_id("course_price")
        self.course_capacities: Locator = page.get_by_test_id("course_capacity")
        self.course_images: Locator = page.get_by_test_id("course_image")
        # Delegace na sdílenou komponentu Navbar
        self.logout_button: Locator = self.navbar.logout_button
        self.login_link: Locator = self.navbar.login_link
        self.courses_link: Locator = self.navbar.courses_link

    def open(self):
        """Otevře stránku kurzů přímo."""
        self.navigate_to(self.URL)
        return self

    def is_logged_in(self) -> bool:
        """Ověří, zda je uživatel přihlášen podle přítomnosti tlačítka Odhlásit se."""
        return self.navbar.is_logged_in()

    def logout(self):
        """Klikne na tlačítko Odhlásit se v navigaci."""
        self.navbar.click_logout()
        return self
