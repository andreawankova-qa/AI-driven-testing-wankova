from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CoursesPage(BasePage):
    """Page Object reprezentující stránku přehledu kurzů po přihlášení."""

    URL = "http://testovani.kitner.cz/courses"

    def __init__(self, page: Page):
        super().__init__(page)
        # Lokátory na stránce kurzů a navigační liště
        self.courses_header: Locator = page.locator('[data-testid="courses_header"]')
        self.logout_button: Locator = page.locator('[data-testid="logout_button"]')
        self.login_link: Locator = page.locator('[data-testid="login_link"]')
        self.courses_link: Locator = page.locator('[data-testid="courses_link"]')

    def open(self):
        """Otevře stránku kurzů přímo."""
        self.navigate_to(self.URL)
        return self

    def is_logged_in(self) -> bool:
        """Ověří, zda je uživatel přihlášen podle přítomnosti tlačítka Odhlásit se."""
        return self.logout_button.is_visible()

    def logout(self):
        """Klikne na tlačítko Odhlásit se."""
        self.logout_button.click()
        return self
