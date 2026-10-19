"""
Komponenta navigace (Navbar) sdílená napříč stránkami aplikace.
"""

from playwright.sync_api import Page, Locator


class NavbarComponent:
    """Reprezentace horní navigační lišty (Navbar) a jejích interakcí."""

    def __init__(self, page: Page):
        self.page = page
        self.container: Locator = page.get_by_test_id("navigation")
        self.courses_link: Locator = self.container.get_by_test_id("courses_link").filter(has_text="Přehled kurzů")
        self.my_courses_link: Locator = self.container.get_by_test_id("courses_link").filter(has_text="Moje kurzy")
        self.home_link: Locator = self.container.get_by_test_id("home_link")
        self.profile_link: Locator = self.container.get_by_test_id("courses_profile")
        self.login_link: Locator = self.container.get_by_test_id("login_link")
        self.logout_button: Locator = self.container.get_by_test_id("logout_button")

    def click_courses(self):
        """Přejde na stránku s nabídkou kurzů."""
        self.courses_link.click()
        return self

    def click_my_courses(self):
        """Přejde do sekce Moje kurzy."""
        self.my_courses_link.click()
        return self

    def click_home(self):
        """Přejde na domovskou stránku."""
        self.home_link.click()
        return self

    def click_profile(self):
        """Přejde do profilu uživatele."""
        self.profile_link.click()
        return self

    def click_login(self):
        """Přejde na přihlašovací formulář."""
        self.login_link.click()
        return self

    def click_logout(self):
        """Klikne na tlačítko pro odhlášení."""
        self.logout_button.click()
        return self

    def is_logged_in(self) -> bool:
        """Ověří, zda je uživatel přihlášen podle přítomnosti tlačítka odhlášení."""
        return self.logout_button.is_visible()

